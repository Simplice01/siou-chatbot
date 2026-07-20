import hashlib
from pathlib import Path


def safe_document_id(path: Path) -> str:
    digest = hashlib.sha256(str(path.name).encode("utf-8")).hexdigest()[:12]
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in path.stem).strip("-")
    return f"{slug}-{digest}"


def file_sha256(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def is_pdf(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".pdf"

