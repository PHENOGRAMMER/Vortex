import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from backend.models.document import Document
from backend.config import get_settings
from backend.services.text_extractor import TextExtractor
from backend.services.text_chunker import TextChunker
from backend.services.text_cleaner import TextCleaner

class DocumentService:

    STORAGE_DIR = get_settings().data_dir
    UPLOAD_DIR = STORAGE_DIR / "uploads"
    IMAGE_DIR = Path(tempfile.gettempdir()) / "omnigen-document-images"
    MANIFEST_FILE = STORAGE_DIR / "documents.json"

    def __init__(self):

        self.UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.MANIFEST_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _read_manifest(self) -> dict:
        if not self.MANIFEST_FILE.exists():
            return {"documents": []}
        return json.loads(self.MANIFEST_FILE.read_text(encoding="utf-8"))

    def _write_manifest(self, manifest: dict) -> None:
        self.MANIFEST_FILE.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    def _serialize_document(self, document: Document) -> dict:
        chunk_objects = document.metadata.get("chunk_objects", [])
        metadata = {
            key: value
            for key, value in document.metadata.items()
            if key != "chunk_objects"
        }
        metadata["chunks"] = [
            {
                "index": chunk.index,
                "text": chunk.text,
                "start": chunk.start,
                "end": chunk.end,
            }
            for chunk in chunk_objects
        ]
        return {
            "id": document.id,
            "filename": document.filename,
            "content": document.content,
            "metadata": metadata,
            "uploaded_at": document.uploaded_at.isoformat(),
        }

    def _deserialize_document(self, item: dict) -> Document:
        from backend.services.text_chunker import TextChunk

        metadata = dict(item.get("metadata") or {})
        metadata["chunk_objects"] = [
            TextChunk(
                index=chunk["index"],
                text=chunk["text"],
                start=chunk["start"],
                end=chunk["end"],
            )
            for chunk in metadata.get("chunks", [])
        ]
        return Document(
            id=item["id"],
            filename=item["filename"],
            content=item.get("content", ""),
            metadata=metadata,
            uploaded_at=datetime.fromisoformat(item["uploaded_at"]),
        )

    def list_documents(self, user_id: int | None = None) -> list[dict]:
        manifest = self._read_manifest()
        return [
            {
                "id": item["id"],
                "filename": item["filename"],
                "metadata": {
                    key: value
                    for key, value in (item.get("metadata") or {}).items()
                    if key != "chunks"
                },
                "uploaded_at": item.get("uploaded_at"),
            }
            for item in manifest["documents"]
            if user_id is None or (item.get("metadata") or {}).get("user_id") == user_id
        ]

    def get_document(self, document_id: str, user_id: int | None = None) -> Document | None:
        manifest = self._read_manifest()
        for item in manifest["documents"]:
            if item["id"] == document_id and (user_id is None or (item.get("metadata") or {}).get("user_id") == user_id):
                return self._deserialize_document(item)
        return None

    def get_all_documents(self, user_id: int | None = None) -> list[Document]:
        manifest = self._read_manifest()
        return [
            self._deserialize_document(item)
            for item in manifest["documents"]
            if user_id is None or (item.get("metadata") or {}).get("user_id") == user_id
        ]

    def delete_document(self, document_id: str, user_id: int | None = None) -> bool:
        manifest = self._read_manifest()
        kept = []
        deleted = None
        for item in manifest["documents"]:
            if item["id"] == document_id and (user_id is None or (item.get("metadata") or {}).get("user_id") == user_id):
                deleted = item
            else:
                kept.append(item)
        if deleted is None:
            return False
        raw_path = deleted.get("metadata", {}).get("path")
        path = Path(raw_path) if raw_path else None
        if path is not None and path.is_file():
            path.unlink()
        image_dir = self.IMAGE_DIR / document_id
        if image_dir.is_dir():
            for image_path in image_dir.iterdir():
                if image_path.is_file():
                    image_path.unlink()
            image_dir.rmdir()
        manifest["documents"] = kept
        self._write_manifest(manifest)
        return True

    def rename_document(self, document_id: str, filename: str, user_id: int | None = None) -> Document | None:
        manifest = self._read_manifest()
        for item in manifest["documents"]:
            if item["id"] == document_id and (user_id is None or (item.get("metadata") or {}).get("user_id") == user_id):
                item["filename"] = filename
                self._write_manifest(manifest)
                return self._deserialize_document(item)
        return None

    async def replace_document(
        self,
        document_id: str,
        filename: str,
        content: bytes,
        user_id: int | None = None,
    ) -> Document | None:
        if not self.delete_document(document_id, user_id=user_id):
            return None
        return await self.save_document(filename=filename, content=content, document_id=document_id, user_id=user_id)

    async def save_document(
        self,
        filename: str,
        content: bytes,
        document_id: str | None = None,
        user_id: int | None = None,
        session_id: int | None = None,
    ) -> Document:

        document_id = document_id or str(uuid4())

        extension = Path(filename).suffix

        stored_name = f"{document_id}{extension}"

        path = self.UPLOAD_DIR / stored_name

        path.write_bytes(content)

        print()
        print("=" * 70)
        print("DOCUMENT UPLOAD")
        print("=" * 70)

        text = TextExtractor.extract(str(path))
        text = TextCleaner.clean(text)

        if not text.strip():
            path.unlink(missing_ok=True)
            raise ValueError("No readable text could be extracted from this document.")

        print(f"Characters Extracted : {len(text)}")

        chunks = TextChunker.chunk(
            text=text,
            chunk_size=800,
            overlap_sentences=2,
        )

        print(f"Chunks Created : {len(chunks)}")
        print()

        for chunk in chunks:

            print(
                f"Chunk {chunk.index:<3}"
                f" Start={chunk.start:<6}"
                f" End={chunk.end:<6}"
                f" Length={len(chunk.text)}"
            )

        print("=" * 70)
        print()

        document = Document(
            id=document_id,
            filename=filename,
            content=text,
            metadata={
                "path": str(path),
                "extension": extension,
                "size": len(content),
                "characters": len(text),
                "chunks": len(chunks),
                "user_id": user_id,
                "session_id": session_id,
                "images": self._extract_document_images(path, document_id, extension.lower()),

                # IMPORTANT
                "chunk_objects": chunks,
            },
        )

        manifest = self._read_manifest()
        manifest["documents"] = [
            item
            for item in manifest["documents"]
            if item["id"] != document.id
        ]
        manifest["documents"].append(self._serialize_document(document))
        self._write_manifest(manifest)

        return document

    def _extract_document_images(self, document_path: Path, document_id: str, extension: str) -> list[dict]:
        if extension == ".pdf":
            return self._extract_pdf_images(document_path, document_id)
        if extension == ".docx":
            return self._extract_docx_images(document_path, document_id)
        return []

    def _extract_pdf_images(self, pdf_path: Path, document_id: str) -> list[dict]:
        """Extract a bounded set of embedded PDF images for chat attachments."""
        try:
            import fitz
        except ImportError:
            return []

        destination = self.IMAGE_DIR / document_id
        images: list[dict] = []
        try:
            pdf = fitz.open(pdf_path)
            destination.mkdir(parents=True, exist_ok=True)
            for page_number, page in enumerate(pdf, start=1):
                for image_number, image in enumerate(page.get_images(full=True), start=1):
                    if len(images) >= 20:
                        return images
                    pixmap = fitz.Pixmap(pdf, image[0])
                    if pixmap.colorspace and pixmap.colorspace.n > 3:
                        pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
                    image_name = f"page-{page_number}-image-{image_number}.png"
                    pixmap.save(destination / image_name)
                    images.append({"name": image_name, "page": page_number})
            return images
        except Exception as exc:
            print(f"PDF image extraction skipped for {pdf_path.name}: {exc}")
            return []
        finally:
            if 'pdf' in locals():
                pdf.close()

    def _extract_docx_images(self, docx_path: Path, document_id: str) -> list[dict]:
        destination = self.IMAGE_DIR / document_id
        images: list[dict] = []
        try:
            with zipfile.ZipFile(docx_path) as archive:
                members = [
                    member for member in archive.infolist()
                    if member.filename.startswith("word/media/") and not member.is_dir()
                ][:20]
                if members:
                    destination.mkdir(parents=True, exist_ok=True)
                for number, member in enumerate(members, start=1):
                    suffix = Path(member.filename).suffix.lower() or ".bin"
                    image_name = f"image-{number}{suffix}"
                    with archive.open(member) as source, (destination / image_name).open("wb") as target:
                        shutil.copyfileobj(source, target)
                    images.append({"name": image_name, "page": None})
        except (OSError, zipfile.BadZipFile) as exc:
            print(f"DOCX image extraction skipped for {docx_path.name}: {exc}")
        return images
