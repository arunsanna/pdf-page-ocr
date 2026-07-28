# Operations

## A normal run

```bash
./scripts/install.sh
pdf-page-ocr doctor
pdf-page-ocr prepare input.pdf --out runs/input --dpi 150
pdf-page-ocr ocr runs/input/manifest.json --adapter unlimited-ocr --resume
pdf-page-ocr combine runs/input/manifest.json --out runs/input/input.md
```

`prepare` is safe to use without any endpoint configuration. Before `ocr`, set `PDF_PAGE_OCR_ENDPOINT` and, if the endpoint requires it, `PDF_PAGE_OCR_API_KEY`. Keep credentials out of shell history where possible; a secret manager or environment-injection mechanism is preferable.

## Resuming safely

Use `--resume` to retain verified successes and continue with pending work:

```bash
pdf-page-ocr ocr runs/input/manifest.json --adapter unlimited-ocr --resume
```

In 0.1, a resume skips a successful page only when its page Markdown artifact is present; failed pages are attempted again on the next resumed OCR invocation. It preserves the earlier failure record in `failures.jsonl`. Hash verification before a resume skip is planned hardening work.

`combine` is intentionally strict. It fails when the manifest has incomplete pages. If a time-sensitive use case requires an incomplete document, pass `--allow-partial` and treat the resulting Markdown as visibly incomplete.

## Output lifecycle

- Keep `manifest.json`, page Markdown, and raw responses together. Separating them breaks provenance and resume behavior.
- Back up or archive an entire run directory when it is a record you may need to reproduce.
- Delete run directories only under your organization's retention policy; they can contain source PDFs and sensitive derived content.
- Do not reuse an output directory for a different source PDF. The CLI should fail rather than overwrite it unless an explicit, documented force option is used.

## Endpoint health and capacity

Start at one page of concurrency. Raise concurrency only after a controlled test establishes the endpoint's queueing, memory, timeout, and error behavior. A server returning HTTP success is not enough: review the returned Markdown for the relevant page types.

`doctor` may report endpoint configuration, but a default invocation should not send document data or require a network connection. Any future endpoint health probe must be explicit and must not send a page image.

## GPU runner helper

`scripts/install-gpu-runner.sh --check` performs only environment checks for a future Linux/NVIDIA runner. It does not install GPU packages, download weights, or start a service. Production model services should be deployed and secured independently of this client.
