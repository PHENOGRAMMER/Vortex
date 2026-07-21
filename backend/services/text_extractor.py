from pathlib import Path


class TextExtractor:

    @staticmethod
    def extract(path: str) -> str:

        extension = Path(path).suffix.lower()

        if extension == ".pdf":
            return TextExtractor._extract_pdf(path)

        elif extension == ".docx":
            return TextExtractor._extract_docx(path)

        elif extension in [".txt", ".md"]:
            return Path(path).read_text(
                encoding="utf-8",
                errors="ignore",
            )

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    @staticmethod
    def _extract_pdf(path: str) -> str:
        try:
            import fitz
        except ImportError as ex:
            raise RuntimeError("PDF extraction requires PyMuPDF. Install 'PyMuPDF'.") from ex

        document = fitz.open(path)

        text = ""

        for page in document:
            text += page.get_text()

        document.close()

        return text

    @staticmethod
    def _extract_docx(path: str) -> str:
        try:
            from docx import Document as DocxDocument
        except ImportError as ex:
            raise RuntimeError("DOCX extraction requires python-docx.") from ex

        document = DocxDocument(path)

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )
