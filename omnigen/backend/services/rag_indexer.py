import os
import uuid
import asyncio
from typing import List, Dict, Any

import numpy as np

# Embedding models – lazy load on first use
_text_encoder = None
_image_encoder = None
_image_preprocess = None

def _load_text_encoder():
    global _text_encoder
    if _text_encoder is None:
        from sentence_transformers import SentenceTransformer
        _text_encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _text_encoder

def _load_image_encoder():
    global _image_encoder, _image_preprocess
    if _image_encoder is None:
        import torch
        from torchvision import transforms
        import clip
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _image_encoder, _ = clip.load("ViT-B/32", device=device)
        _image_preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.48145466, 0.4578275, 0.40821073), std=(0.26862954, 0.26130258, 0.27577711)),
        ])
    return _image_encoder, _image_preprocess

# Helper to split long text into chunks (approx 200 tokens ≈ 300 characters)
def _chunk_text(text: str, max_chars: int = 300) -> List[str]:
    chunks = []
    while text:
        chunk = text[:max_chars]
        # try not to cut mid‑sentence
        split_pos = chunk.rfind('\n')
        if split_pos == -1:
            split_pos = max_chars
        chunks.append(text[:split_pos].strip())
        text = text[split_pos:]
    return [c for c in chunks if c]

# Simple text extraction for supported formats
def _extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in {'.txt', '.md', '.json'}:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    if ext == '.pdf':
        from pdfminer.high_level import extract_text
        return extract_text(file_path)
    if ext in {'.docx', '.doc'}:
        import docx
        doc = docx.Document(file_path)
        return '\n'.join(p.text for p in doc.paragraphs)
    # fallback – treat as binary
    return ''

# Image embedding via CLIP
def _encode_image(file_path: str) -> np.ndarray:
    import torch
    from PIL import Image
    model, preprocess = _load_image_encoder()
    device = next(model.parameters()).device
    image = Image.open(file_path).convert('RGB')
    tensor = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(tensor)
    embedding = embedding / embedding.norm(dim=-1, keepdim=True)
    return embedding.cpu().numpy().astype(np.float32).squeeze()

# Text embedding
def _encode_text(texts: List[str]) -> np.ndarray:
    encoder = _load_text_encoder()
    embeddings = encoder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype(np.float32)

# Global vector store instance – dimension 512 for CLIP, 384 for MiniLM – we unify to 512 by padding smaller vectors
from ..services.vector_store import VectorStore

# Determine dimension dynamically – use CLIP (512) as canonical
_VECTOR_DIM = 512
try:
    _store = VectorStore(dim=_VECTOR_DIM)
except ImportError:
    _store = None

async def process_upload(file_path: str) -> str:
    """Index a newly uploaded file.
    Returns a document‑level UUID.
    """
    ext = os.path.splitext(file_path)[1].lower()
    doc_id = str(uuid.uuid4())
    if _store is None:
        raise RuntimeError(
            "RAG vector storage is unavailable because FAISS is not installed."
        )
    metadata_entries = []
    ids = []
    vectors = []

    if ext in {'.png', '.jpg', '.jpeg', '.gif'}:
        # Image – single embedding
        vec = _encode_image(file_path)
        # Pad if needed to match VECTOR_DIM (CLIP already 512)
        ids.append(f"{doc_id}_0")
        vectors.append(vec)
        metadata_entries.append({"doc_id": doc_id, "source": os.path.basename(file_path), "type": "image", "page": 0, "snippet": "[image]"})
    else:
        # Text documents – extract full text then chunk
        raw = _extract_text(file_path)
        chunks = _chunk_text(raw)
        if not chunks:
            return doc_id
        text_vecs = _encode_text(chunks)
        # Pad text vectors to VECTOR_DIM if they are smaller (MiniLM 384)
        if text_vecs.shape[1] < _VECTOR_DIM:
            pad_width = _VECTOR_DIM - text_vecs.shape[1]
            text_vecs = np.pad(text_vecs, ((0,0),(0,pad_width)), mode='constant')
        for i, (chunk, vec) in enumerate(zip(chunks, text_vecs)):
            ids.append(f"{doc_id}_{i}")
            vectors.append(vec)
            metadata_entries.append({"doc_id": doc_id, "source": os.path.basename(file_path), "type": "text", "page": i, "snippet": chunk[:200]})
    # Convert to numpy matrix
    vec_matrix = np.vstack(vectors)
    _store.add_vectors(ids, vec_matrix, metadata_entries)
    return doc_id

async def rag_query(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve top‑k most similar chunks for a user query.
    Returns a list of dictionaries containing `doc_id`, `source`, `snippet`, and similarity `score`.
    """
    if _store is None:
        raise RuntimeError(
            "RAG vector storage is unavailable because FAISS is not installed."
        )
    # Encode query with same text encoder (MiniLM) and pad
    q_vec = _encode_text([query])[0]
    if q_vec.shape[0] < _VECTOR_DIM:
        q_vec = np.pad(q_vec, (0, _VECTOR_DIM - q_vec.shape[0]), mode='constant')
    results = _store.search(q_vec, k=k)
    # Trim to essential fields
    cleaned = []
    for r in results:
        cleaned.append({
            "doc_id": r.get("doc_id"),
            "source": r.get("source"),
            "snippet": r.get("snippet"),
            "score": r.get("score"),
        })
    return cleaned
