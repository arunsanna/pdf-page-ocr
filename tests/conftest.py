from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfWriter


@pytest.fixture()
def sample_pdf(tmp_path: Path) -> Path:
    path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.add_blank_page(width=612, height=792)
    with path.open("wb") as destination:
        writer.write(destination)
    return path
