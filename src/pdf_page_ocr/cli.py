"""Typer command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from .combine import combine_manifest
from .doctor import doctor_report
from .ocr import ocr_manifest
from .prepare import prepare_pdf

app = typer.Typer(no_args_is_help=True, add_completion=False)


def _fail(exc: Exception) -> None:
    raise typer.BadParameter(str(exc)) from exc


@app.command()
def prepare(
    input_pdf: Annotated[Path, typer.Argument(exists=True, readable=True)],
    out: Annotated[Path, typer.Option("--out", "-o")],
    dpi: Annotated[int, typer.Option()] = 150,
    force: Annotated[bool, typer.Option(help="Replace a non-empty output directory.")] = False,
) -> None:
    """Split and render a PDF locally; no OCR endpoint is contacted."""
    try:
        path = prepare_pdf(input_pdf, out, dpi=dpi, force=force)
    except ValueError as exc:
        _fail(exc)
    typer.echo(f"prepared manifest: {path}")


@app.command()
def ocr(
    manifest: Annotated[Path, typer.Argument(exists=True, readable=True)],
    adapter: Annotated[
        str, typer.Option(help="OCR adapter profile. Only unlimited-ocr is available in 0.1.")
    ] = "unlimited-ocr",
    endpoint: Annotated[str | None, typer.Option(envvar="PDF_PAGE_OCR_ENDPOINT")] = None,
    api_key: Annotated[
        str | None, typer.Option(envvar="PDF_PAGE_OCR_API_KEY", hide_input=True)
    ] = None,
    model: Annotated[str, typer.Option()] = "Unlimited-OCR",
    resume: Annotated[bool, typer.Option("--resume/--no-resume")] = True,
    timeout_seconds: Annotated[float, typer.Option("--timeout-seconds")] = 120.0,
) -> None:
    """Send one pending page at a time to a configured OCR endpoint."""
    try:
        result = ocr_manifest(
            manifest,
            endpoint=endpoint or "",
            adapter=adapter,
            api_key=api_key,
            model=model,
            resume=resume,
            timeout_seconds=timeout_seconds,
        )
    except ValueError as exc:
        _fail(exc)
    succeeded = sum(page.state == "succeeded" for page in result.pages)
    typer.echo(f"OCR complete: {succeeded}/{len(result.pages)} pages succeeded")


@app.command()
def combine(
    manifest: Annotated[Path, typer.Argument(exists=True, readable=True)],
    out: Annotated[Path, typer.Option("--out", "-o")],
    allow_partial: Annotated[bool, typer.Option()] = False,
) -> None:
    """Combine page Markdown, refusing failed pages unless explicitly allowed."""
    try:
        output = combine_manifest(manifest, out, allow_partial=allow_partial)
    except ValueError as exc:
        _fail(exc)
    typer.echo(f"combined Markdown: {output}")


@app.command()
def run(
    input_pdf: Annotated[Path, typer.Argument(exists=True, readable=True)],
    out: Annotated[Path, typer.Option("--out", "-o")],
    adapter: Annotated[
        str, typer.Option(help="OCR adapter profile. Only unlimited-ocr is available in 0.1.")
    ] = "unlimited-ocr",
    endpoint: Annotated[str | None, typer.Option(envvar="PDF_PAGE_OCR_ENDPOINT")] = None,
    api_key: Annotated[
        str | None, typer.Option(envvar="PDF_PAGE_OCR_API_KEY", hide_input=True)
    ] = None,
    model: Annotated[str, typer.Option()] = "Unlimited-OCR",
    dpi: Annotated[int, typer.Option()] = 150,
    resume: Annotated[bool, typer.Option("--resume/--no-resume")] = False,
    timeout_seconds: Annotated[float, typer.Option("--timeout-seconds")] = 120.0,
) -> None:
    """Prepare, OCR, and combine a PDF in one command."""
    manifest = out / "manifest.json"
    try:
        if manifest.exists():
            if not resume:
                raise ValueError(
                    "output already has a manifest; pass --resume or choose a new --out"
                )
        else:
            prepare_pdf(input_pdf, out, dpi=dpi)
        result = ocr_manifest(
            manifest,
            endpoint=endpoint or "",
            adapter=adapter,
            api_key=api_key,
            model=model,
            resume=True,
            timeout_seconds=timeout_seconds,
        )
        failed = [page for page in result.pages if page.state != "succeeded"]
        if failed:
            raise ValueError(
                f"OCR failed for {len(failed)} page(s); "
                "inspect failures.jsonl and rerun --resume"
            )
        output = combine_manifest(manifest, out / "document.md")
    except ValueError as exc:
        _fail(exc)
    typer.echo(f"run complete: {output}")


@app.command()
def doctor(
    out: Annotated[Path | None, typer.Option("--out", "-o")] = None,
) -> None:
    """Check local CLI dependencies without contacting an OCR endpoint."""
    try:
        for line in doctor_report(out):
            typer.echo(line)
    except OSError as exc:
        _fail(exc)


if __name__ == "__main__":
    app()
