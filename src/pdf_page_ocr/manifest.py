"""Versioned, portable run manifest handling."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class SourceInfo(BaseModel):
    path: str
    sha256: str
    page_count: int


class RenderInfo(BaseModel):
    dpi: int
    renderer: str = "pypdfium2"
    format: str = "png"


class PageRecord(BaseModel):
    number: int
    source_pdf: str
    image: str
    image_sha256: str
    width: int
    height: int
    state: Literal["pending", "succeeded", "failed"] = "pending"
    attempts: int = 0
    adapter: str | None = None
    adapter_profile: str | None = None
    model: str | None = None
    normalization_version: str | None = None
    raw_response: str | None = None
    markdown: str | None = None
    markdown_sha256: str | None = None
    elapsed_seconds: float | None = None
    error: str | None = None


class Manifest(BaseModel):
    schema_version: Literal[1] = 1
    source: SourceInfo
    render: RenderInfo
    pages: list[PageRecord] = Field(default_factory=list)


def manifest_path(run_dir: Path) -> Path:
    return run_dir / "manifest.json"


def load_manifest(path: Path) -> Manifest:
    try:
        return Manifest.model_validate_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"manifest not found: {path}") from exc
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"invalid manifest: {path}: {exc}") from exc


def save_manifest(path: Path, manifest: Manifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
