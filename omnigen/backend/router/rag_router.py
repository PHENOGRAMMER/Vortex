import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from ..services.rag_indexer import process_upload, rag_query

router = APIRouter(prefix="/api/rag", tags=["RAG"])

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Accept multiple file uploads, store them, and index for retrieval.
    Returns a list of document IDs."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    ids = []
    for uploaded in files:
        upload_dir = os.getenv("RAG_UPLOAD_DIR", "omnigen/uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, uploaded.filename)
        with open(file_path, "wb") as f:
            content = await uploaded.read()
            f.write(content)
        doc_id = await process_upload(file_path)
        ids.append(doc_id)
    return {"document_ids": ids}

@router.post("/query")
async def query_rag(query: str):
    """Retrieve relevant chunks for a user query."""
    results = await rag_query(query)
    return {"results": results}
