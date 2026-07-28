from __future__ import annotations

from pathlib import Path

import pytest

from pdf_page_ocr.manifest import load_manifest
from pdf_page_ocr.prepare import prepare_pdf


def test_prepare_splits_renders_and_records_manifest(sample_pdf: Path, tmp_path: Path) -> None:
    manifest_path = prepare_pdf(sample_pdf, tmp_path / "run", dpi=150)

    manifest = load_manifest(manifest_path)
    assert manifest.schema_version == 1
    assert manifest.source.page_count == 2
    assert manifest.render.dpi == 150
    assert [page.number for page in manifest.pages] == [1, 2]
    for page in manifest.pages:
        assert (manifest_path.parent / page.source_pdf).is_file()
        assert (manifest_path.parent / page.image).is_file()
        assert page.width > 0 and page.height > 0
        assert len(page.image_sha256) == 64


def test_prepare_force_refuses_a_non_run_directory(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "not-a-run"
    output.mkdir()
    (output / "keep-me.txt").write_text("user data", encoding="utf-8")

    with pytest.raises(ValueError, match="not an existing pdf-page-ocr run"):
        prepare_pdf(sample_pdf, output, force=True)

    assert (output / "keep-me.txt").read_text(encoding="utf-8") == "user data"
