from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.auth.models import User
from backend.chat.models import ChatSession
from backend.db.database import get_db
from backend.models.query_request import QueryRequest
from backend.services.document_service import DocumentService
from backend.services.indexing_service import IndexingService
from backend.services.rag_service import RAGService

router = APIRouter(prefix="/api/rag", tags=["RAG"])
rag_service = RAGService()
document_service = DocumentService()
indexing_service = IndexingService()
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def validate_extension(filename: str) -> bool:
    return bool(filename and "." in filename and "." + filename.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS)


@router.post("/upload")
async def upload_for_rag(
    files: List[UploadFile] = File(...),
    session_id: int | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if session_id is not None:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        ).first()
        if session is None:
            raise HTTPException(status_code=404, detail="Chat session not found.")
    document_ids, errors = [], []
    for file in files:
        document = None
        if not validate_extension(file.filename):
            errors.append(f"{file.filename}: unsupported file type")
            continue
        try:
            content = await file.read()
            if not content:
                errors.append(f"{file.filename}: file is empty")
                continue
            if len(content) > MAX_UPLOAD_BYTES:
                errors.append(f"{file.filename}: exceeds the 20 MB limit")
                continue
            document = await document_service.save_document(
                file.filename,
                content,
                user_id=current_user.id,
                session_id=session_id,
            )
            await indexing_service.index_document(document)
            document_ids.append(document.id)
        except Exception as exc:
            if document is not None:
                document_service.delete_document(document.id, user_id=current_user.id)
            errors.append(f"{file.filename}: {exc}")
    return {"document_ids": document_ids, "uploaded": len(document_ids), "errors": errors}


@router.post("/query")
async def query(request: QueryRequest, current_user: User = Depends(get_current_user)):
    return await rag_service.retrieve(question=request.query, top_k=request.top_k,
                                      document_ids=request.document_ids, filenames=request.filenames,
                                      user_id=current_user.id)


@router.post("/answer")
async def answer(request: QueryRequest, current_user: User = Depends(get_current_user)):
    return await rag_service.answer(question=request.query, top_k=request.top_k,
                                    document_ids=request.document_ids, filenames=request.filenames,
                                    user_id=current_user.id)
