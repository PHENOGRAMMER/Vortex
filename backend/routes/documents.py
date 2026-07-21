from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path
import mimetypes
from pydantic import BaseModel

from backend.auth.dependencies import get_current_user
from backend.auth.models import User
from backend.services.document_service import DocumentService
from backend.services.indexing_service import IndexingService

router = APIRouter(prefix="/api/documents", tags=["Documents"])
service = DocumentService()
indexing_service = IndexingService()
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


class RenameDocumentRequest(BaseModel):
    filename: str


def validate_extension(filename: str) -> None:
    if not filename or "." not in filename or "." + filename.rsplit(".", 1)[-1].lower() not in {".pdf", ".docx", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, TXT, or Markdown.")


async def reindex_all_documents() -> None:
    await indexing_service.reindex_documents(service.get_all_documents())


def document_payload(document, preview_length: int = 500) -> dict:
    metadata = {key: value for key, value in document.metadata.items() if key != "chunk_objects"}
    metadata.pop("path", None)
    return {"id": document.id, "filename": document.filename, "metadata": metadata,
            "characters": len(document.content), "preview": document.content[:preview_length],
            "uploaded_at": document.uploaded_at}


@router.get("")
async def list_documents(
    session_id: int | None = Query(None),
    current_user: User = Depends(get_current_user),
):
    documents = service.list_documents(user_id=current_user.id)
    if session_id is not None:
        documents = [
            document for document in documents
            if document["metadata"].get("session_id") == session_id
        ]
    return {"documents": documents}


@router.get("/{document_id}/images/{image_name}")
async def get_document_image(
    document_id: str,
    image_name: str,
    current_user: User = Depends(get_current_user),
):
    if Path(image_name).name != image_name:
        raise HTTPException(status_code=404, detail="Image not found.")
    document = service.get_document(document_id, user_id=current_user.id)
    if document is None or image_name not in {
        image.get("name") for image in document.metadata.get("images", [])
    }:
        raise HTTPException(status_code=404, detail="Image not found.")
    image_path = service.IMAGE_DIR / document_id / image_name
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(image_path, media_type=mimetypes.guess_type(image_path.name)[0] or "application/octet-stream")


@router.get("/{document_id}")
async def get_document(document_id: str, current_user: User = Depends(get_current_user)):
    document = service.get_document(document_id, user_id=current_user.id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document_payload(document, preview_length=1000)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    validate_extension(file.filename)
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="The uploaded file exceeds the 20 MB limit.")
    document = None
    try:
        document = await service.save_document(filename=file.filename, content=content, user_id=current_user.id)
        await indexing_service.index_document(document)
    except Exception as exc:
        if document is not None:
            service.delete_document(document.id, user_id=current_user.id)
        raise HTTPException(status_code=422, detail=f"Unable to index document: {exc}") from exc
    return document_payload(document)


@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: User = Depends(get_current_user)):
    if not service.delete_document(document_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="Document not found.")
    await reindex_all_documents()
    return {"deleted": True, "id": document_id}


@router.patch("/{document_id}/rename")
async def rename_document(document_id: str, request: RenameDocumentRequest, current_user: User = Depends(get_current_user)):
    validate_extension(request.filename)
    document = service.rename_document(document_id, request.filename, user_id=current_user.id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    await reindex_all_documents()
    return document_payload(document)


@router.put("/{document_id}/replace")
async def replace_document(document_id: str, file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    validate_extension(file.filename)
    document = await service.replace_document(document_id, file.filename, await file.read(), user_id=current_user.id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    await reindex_all_documents()
    return document_payload(document)


@router.post("/reindex")
async def reindex_documents(current_user: User = Depends(get_current_user)):
    await reindex_all_documents()
    return {"documents": service.list_documents(user_id=current_user.id), "reindexed": True}
