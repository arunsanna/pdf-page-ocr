"""Offline environment checks; no endpoint request is made."""

from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path


def doctor_report(output_dir: Path | None = None) -> list[str]:
    lines = [f"Python: {sys.version.split()[0]}"]
    for package in ("pypdf", "pypdfium2", "httpx", "pydantic", "typer"):
        try:
            lines.append(f"{package}: {importlib.metadata.version(package)}")
        except importlib.metadata.PackageNotFoundError:
            lines.append(f"{package}: missing")
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        probe = output_dir / ".pdf-page-ocr-write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        lines.append(f"output directory: writable ({output_dir})")
    lines.append("endpoint health: not checked (offline by default)")
    return lines
