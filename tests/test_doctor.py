from __future__ import annotations

from pathlib import Path

from pdf_page_ocr.doctor import doctor_report


def test_doctor_is_offline_and_can_check_output_directory(tmp_path: Path) -> None:
    report = doctor_report(tmp_path / "writeable")
    assert any(line.startswith("Python:") for line in report)
    assert "endpoint health: not checked (offline by default)" in report
    assert any("output directory: writable" in line for line in report)
