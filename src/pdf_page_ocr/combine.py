"""Ordered Markdown assembly with explicit partial-result guard."""

from __future__ import annotations

from pathlib import Path

from .manifest import load_manifest


def combine_manifest(
    manifest_file: Path, output_file: Path, *, allow_partial: bool = False
) -> Path:
    manifest = load_manifest(manifest_file)
    run_dir = manifest_file.parent
    incomplete = [
        str(page.number)
        for page in manifest.pages
        if page.state != "succeeded"
        or not page.markdown
        or not (run_dir / page.markdown).is_file()
    ]
    if incomplete and not allow_partial:
        raise ValueError(
            "cannot combine because pages are not successful: "
            + ", ".join(incomplete)
            + "; rerun OCR or pass --allow-partial"
        )
    sections = [f"<!-- pdf-page-ocr source-sha256: {manifest.source.sha256} -->", ""]
    for page in manifest.pages:
        if (
            page.state != "succeeded"
            or not page.markdown
            or not (run_dir / page.markdown).is_file()
        ):
            if allow_partial:
                sections.extend([f"<!-- page {page.number}: OCR unavailable -->", ""])
            continue
        content = (run_dir / page.markdown).read_text(encoding="utf-8").strip()
        sections.extend([f"<!-- page {page.number} -->", content, ""])
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    return output_file
