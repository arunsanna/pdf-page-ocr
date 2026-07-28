"""Local PDF validation, page splitting, rendering, and provenance."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any, cast

import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter

from .manifest import Manifest, PageRecord, RenderInfo, SourceInfo, manifest_path, save_manifest


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _prepare_output_directory(output_dir: Path, *, force: bool) -> None:
    resolved = output_dir.resolve()
    if resolved == Path(resolved.anchor) or resolved == Path.home():
        raise ValueError("refusing to use a filesystem root or home directory as --out")
    if output_dir.exists() and any(output_dir.iterdir()):
        if not force:
            raise ValueError(
                f"output directory is not empty: {output_dir}; choose a new --out or pass --force"
            )
        if not (output_dir / "manifest.json").is_file():
            raise ValueError(
                "refusing --force because the non-empty output directory is not an existing "
                "pdf-page-ocr run"
            )
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def prepare_pdf(input_pdf: Path, output_dir: Path, *, dpi: int = 150, force: bool = False) -> Path:
    """Create deterministic page artifacts and return the manifest path."""
    if dpi < 72 or dpi > 600:
        raise ValueError("--dpi must be between 72 and 600")
    if not input_pdf.is_file():
        raise ValueError(f"input PDF not found: {input_pdf}")
    if input_pdf.suffix.lower() != ".pdf":
        raise ValueError(f"input must be a .pdf file: {input_pdf}")
    try:
        reader = PdfReader(str(input_pdf))
        page_count = len(reader.pages)
    except Exception as exc:  # pypdf exposes several parser errors
        raise ValueError(f"could not read PDF: {input_pdf}: {exc}") from exc
    if page_count == 0:
        raise ValueError(f"PDF has no pages: {input_pdf}")

    _prepare_output_directory(output_dir, force=force)
    source_dir = output_dir / "source"
    pages_dir = output_dir / "pages"
    source_dir.mkdir()
    pages_dir.mkdir()
    copied_source = source_dir / input_pdf.name
    shutil.copy2(input_pdf, copied_source)

    try:
        document = pdfium.PdfDocument(str(input_pdf))
        if len(document) != page_count:
            raise ValueError("pypdf and pypdfium2 reported different page counts")
        records: list[PageRecord] = []
        for index, source_page in enumerate(reader.pages, start=1):
            stem = f"page-{index:04d}"
            page_pdf = pages_dir / f"{stem}.pdf"
            writer = PdfWriter()
            writer.add_page(source_page)
            with page_pdf.open("wb") as destination:
                writer.write(destination)

            rendered_page = document[index - 1]
            # pypdfium2 accepts a float scale; its current type stub incorrectly says int.
            bitmap = rendered_page.render(scale=cast(Any, dpi / 72))
            image = bitmap.to_pil()
            image_path = pages_dir / f"{stem}.png"
            image.save(image_path, format="PNG")
            records.append(
                PageRecord(
                    number=index,
                    source_pdf=page_pdf.relative_to(output_dir).as_posix(),
                    image=image_path.relative_to(output_dir).as_posix(),
                    image_sha256=sha256_file(image_path),
                    width=image.width,
                    height=image.height,
                )
            )
    except Exception:
        # The caller can inspect a failed output only when they deliberately choose --force.
        # Removing it avoids accidentally treating a partial directory as a completed run.
        shutil.rmtree(output_dir, ignore_errors=True)
        raise

    result = Manifest(
        source=SourceInfo(
            path=copied_source.relative_to(output_dir).as_posix(),
            sha256=sha256_file(copied_source),
            page_count=page_count,
        ),
        render=RenderInfo(dpi=dpi),
        pages=records,
    )
    result_path = manifest_path(output_dir)
    save_manifest(result_path, result)
    return result_path
