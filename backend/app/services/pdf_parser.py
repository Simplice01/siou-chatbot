from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.models.document import PageText


class PdfParser:
    def parse(self, path: Path) -> list[PageText]:
        if path.suffix.lower() == ".docx":
            return self._parse_docx(path)
        reader = PdfReader(str(path))
        pages: list[PageText] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            clean = " ".join(text.replace("\x00", " ").split())
            pages.append(PageText(page=index, text=clean))
        return pages

    def page_count(self, path: Path) -> int:
        if path.suffix.lower() == ".docx":
            return 1
        return len(PdfReader(str(path)).pages)

    def _parse_docx(self, path: Path) -> list[PageText]:
        document = DocxDocument(str(path))
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        table_lines: list[str] = []
        for table in document.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if cells:
                    table_lines.append(" | ".join(cells))
        text = " ".join("\n".join(paragraphs + table_lines).replace("\x00", " ").split())
        return [PageText(page=1, text=text)] if text else []
