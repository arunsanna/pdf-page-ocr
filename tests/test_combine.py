from __future__ import annotations

from pathlib import Path

import pytest

from pdf_page_ocr.combine import combine_manifest
from pdf_page_ocr.manifest import load_manifest, save_manifest
from pdf_page_ocr.prepare import prepare_pdf


def test_combine_rejects_partial_unless_explicit(sample_pdf: Path, tmp_path: Path) -> None:
    manifest_path = prepare_pdf(sample_pdf, tmp_path / "run")
    manifest = load_manifest(manifest_path)
    first = manifest.pages[0]
    markdown = manifest_path.parent / "pages/page-0001.md"
    markdown.write_text("first page\n", encoding="utf-8")
    first.state = "succeeded"
    first.markdown = "pages/page-0001.md"
    save_manifest(manifest_path, manifest)

    with pytest.raises(ValueError, match="cannot combine"):
        combine_manifest(manifest_path, tmp_path / "result.md")

    output = combine_manifest(manifest_path, tmp_path / "result.md", allow_partial=True)
    text = output.read_text(encoding="utf-8")
    assert "first page" in text
    assert "page 2: OCR unavailable" in text


def test_combine_treats_missing_markdown_as_incomplete(sample_pdf: Path, tmp_path: Path) -> None:
    manifest_path = prepare_pdf(sample_pdf, tmp_path / "run")
    manifest = load_manifest(manifest_path)
    for page in manifest.pages:
        page.state = "succeeded"
        page.markdown = f"pages/page-{page.number:04d}.md"
    save_manifest(manifest_path, manifest)

    with pytest.raises(ValueError, match="cannot combine"):
        combine_manifest(manifest_path, tmp_path / "result.md")
