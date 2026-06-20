import logging
from pathlib import Path
from typing import Optional

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

logger = logging.getLogger(__name__)


class FileParser:
    @staticmethod
    def parse_txt(file_path: Path) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def parse_md(file_path: Path) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def parse_pdf(file_path: Path) -> str:
        if not PdfReader:
            raise ImportError("pypdf is required to parse PDF files.")

        try:
            reader = PdfReader(str(file_path))
            text_blocks = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_blocks.append(text)
            return "\n\n".join(text_blocks)
        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {e}")
            raise

    @staticmethod
    def parse_docx(file_path: Path) -> str:
        if not docx:
            raise ImportError("python-docx is required to parse DOCX files.")

        try:
            doc = docx.Document(str(file_path))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Failed to parse DOCX {file_path}: {e}")
            raise

    @classmethod
    def parse_file(cls, file_path: str | Path) -> Optional[str]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        ext = path.suffix.lower()
        if ext == ".txt":
            return cls.parse_txt(path)
        elif ext == ".md":
            return cls.parse_md(path)
        elif ext == ".pdf":
            return cls.parse_pdf(path)
        elif ext in [".doc", ".docx"]:
            return cls.parse_docx(path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
