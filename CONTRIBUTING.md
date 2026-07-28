# Contributing

Thank you for helping make pagewise document extraction reliable and reviewable.

## Scope for the first release

The project is a local PDF artifact pipeline and a client for a configured OCR endpoint. Keep changes focused on page-level preparation, manifests, endpoint compatibility, resume behavior, or documentation. Do not add an embedded model server, automatic upload, telemetry, or a local CPU Unlimited-OCR claim without an explicit architecture decision.

## Local setup

```bash
./scripts/install.sh
uv run ruff check .
uv run pyright
uv run pytest
```

The test suite must not need a real OCR endpoint or model weights. Endpoint behavior belongs behind a fake-server contract test; an actual GPU endpoint smoke test is a separately authorized integration check.

## Pull requests

- Keep changes narrowly scoped and explain the user-visible behavior.
- Add or update tests for manifests, ordering, retries, output integrity, and error behavior as applicable.
- Do not commit source PDFs, page images, run directories, raw OCR responses, or credentials.
- Preserve the CPU-safe/GPU-endpoint boundary in help text and documentation.
- Update `THIRD_PARTY_NOTICES.md` and lockfile evidence when dependencies or adapter profiles change.

## Documentation and diagrams

Documentation should distinguish a planned interface, a unit-tested path, and a real endpoint-verified result. Architecture images are real reviewed assets in `docs/assets/`; do not replace them with placeholder diagrams. When a diagram changes, update the corresponding explanation and ensure labels preserve the local-versus-endpoint trust boundary.

## Reporting problems

Include the CLI version, operating system, command shape with secrets removed, manifest state, and a minimal non-sensitive reproduction. For security issues, follow the private-reporting guidance in [docs/security.md](docs/security.md).
