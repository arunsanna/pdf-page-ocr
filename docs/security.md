# Security and data handling

## Threat model in one sentence

The sensitive assets are the source PDF, rendered page images, raw endpoint responses, derived Markdown, and endpoint credentials; the primary boundary is between local artifacts and the user-selected OCR endpoint.

## Defaults

- Local commands do not upload a PDF by default.
- OCR requests send one page at a time only after an endpoint is configured and OCR is invoked.
- The client must not persist API keys, authorization headers, or credential-bearing endpoint URLs in manifests, raw response files, logs, or diagnostics.
- Run artifacts remain on local storage selected by the caller; no project-operated telemetry or storage is part of the design.

## Operator responsibilities

- Use a GPU endpoint you are authorized to send the document to.
- Verify transport security, authentication, retention, logging, and access controls for that endpoint.
- Protect the run directory as you would the original PDF: it can hold page images and raw OCR output.
- Set restrictive directory permissions when documents are sensitive and do not commit `runs/` to source control.
- Review OCR output before using it in legal, financial, security, medical, or other high-impact workflows.

## Input and output safety

The implementation should validate PDFs, resolve output paths carefully, reject unsafe overwrite behavior by default, and record errors per page. It should bound network timeouts and retries, avoid logging request bodies, and keep a clear distinction between a failed page and a complete one.

An OCR result is untrusted input. Downstream renderers or applications must escape or sanitize extracted Markdown/HTML according to their own security model.

## Dependencies and model runtime

The default package must use a lockfile and avoid pulling GPU runtimes or model code. A future GPU runner is opt-in and has a distinct security posture: model servers, model revisions, and any `trust_remote_code` mechanism require review by the endpoint operator. See [third-party notices](../THIRD_PARTY_NOTICES.md) for supply-chain tracking policy.

## Reporting a vulnerability

Do not publish exploit details in a public issue. Until a dedicated security contact is added, open a private GitHub security advisory for the repository or contact the maintainer through the channel listed in the repository profile.
