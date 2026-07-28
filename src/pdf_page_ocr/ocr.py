"""Resumable page-level OCR orchestration."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import httpx

from .adapters.unlimited_ocr import (
    ADAPTER_PROFILE,
    NORMALIZATION_VERSION,
    call_endpoint,
    extract_markdown,
)
from .manifest import Manifest, load_manifest, save_manifest


def _append_failure(run_dir: Path, page_number: int, attempts: int, error: str) -> None:
    record = {"page": page_number, "attempt": attempts, "error": error}
    with (run_dir / "failures.jsonl").open("a", encoding="utf-8") as destination:
        destination.write(json.dumps(record) + "\n")


def ocr_manifest(
    manifest_file: Path,
    *,
    endpoint: str,
    adapter: str = "unlimited-ocr",
    api_key: str | None = None,
    model: str = "Unlimited-OCR",
    resume: bool = True,
    timeout_seconds: float = 120.0,
    transport: httpx.BaseTransport | None = None,
) -> Manifest:
    """OCR pending pages, preserving every successful page before continuing."""
    if not endpoint.strip():
        raise ValueError("an OCR endpoint is required; set --endpoint or PDF_PAGE_OCR_ENDPOINT")
    if adapter != "unlimited-ocr":
        raise ValueError(f"unsupported adapter: {adapter}; supported: unlimited-ocr")
    run_dir = manifest_file.parent
    manifest = load_manifest(manifest_file)
    with httpx.Client(timeout=timeout_seconds, transport=transport) as client:
        for page in manifest.pages:
            markdown_path = run_dir / (page.markdown or f"pages/page-{page.number:04d}.md")
            if resume and page.state == "succeeded" and markdown_path.is_file():
                continue
            page.attempts += 1
            page.adapter = adapter
            page.adapter_profile = ADAPTER_PROFILE
            page.model = model
            page.normalization_version = NORMALIZATION_VERSION
            page.error = None
            started = time.monotonic()
            try:
                payload = call_endpoint(
                    client,
                    endpoint=endpoint,
                    image_path=run_dir / page.image,
                    model=model,
                    api_key=api_key,
                )
                raw_path = run_dir / f"pages/page-{page.number:04d}.raw.json"
                raw_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
                markdown = extract_markdown(payload)
                markdown_path.write_text(markdown, encoding="utf-8")
                page.raw_response = raw_path.relative_to(run_dir).as_posix()
                page.markdown = markdown_path.relative_to(run_dir).as_posix()
                page.markdown_sha256 = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
                page.elapsed_seconds = round(time.monotonic() - started, 3)
                page.state = "succeeded"
            except (httpx.HTTPError, ValueError, OSError, json.JSONDecodeError) as exc:
                page.elapsed_seconds = round(time.monotonic() - started, 3)
                page.state = "failed"
                page.error = str(exc)
                _append_failure(run_dir, page.number, page.attempts, page.error)
            save_manifest(manifest_file, manifest)
    return manifest
