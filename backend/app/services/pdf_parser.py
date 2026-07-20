from pathlib import Path

from pypdf import PdfReader

from app.models.document import PageText


class PdfParser:
    def parse(self, path: Path) -> list[PageText]:
        reader = PdfReader(str(path))
        pages: list[PageText] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            clean = " ".join(text.replace("\x00", " ").split())
            pages.append(PageText(page=index, text=clean))
        return pages

    def page_count(self, path: Path) -> int:
        return len(PdfReader(str(path)).pages)

