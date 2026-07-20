from pathlib import Path

import pytest
from reportlab.pdfgen import canvas


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    path = tmp_path / "contrat-test.pdf"
    pdf = canvas.Canvas(str(path))
    pdf.drawString(72, 740, "Le montant du contrat est de 1200 euros.")
    pdf.drawString(72, 720, "La date de signature est le 14 janvier 2026.")
    pdf.showPage()
    pdf.drawString(72, 740, "La clause de resiliation impose un preavis de trente jours.")
    pdf.save()
    return path

