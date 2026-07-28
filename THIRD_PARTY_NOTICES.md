# Third-party notices and supply-chain policy

This file tracks material third-party components used or referenced by PDF Page OCR. It is not a substitute for the complete license texts shipped by package distributions. Before a public release, generate and review a dependency inventory from the committed `uv.lock`, and update this file with the exact package versions and notices required by their licenses.

## Project dependencies

The default project environment is intended to use Python packages for CLI parsing, manifest validation, HTTP requests, PDF splitting/rendering, tests, linting, and type checking. Their exact versions are pinned in `uv.lock`; no dependency should be introduced without a license and maintenance review.

The default installation deliberately excludes GPU runtimes, model weights, and a model-serving stack.

## External OCR model reference

- **Unlimited-OCR**, Baidu, [`baidu/Unlimited-OCR`](https://github.com/baidu/Unlimited-OCR). The first endpoint adapter is designed for a compatible user-operated serving endpoint. The model repository and its runtime are not bundled, downloaded, or executed by default. Consult the upstream repository and model card for its license, notices, serving requirements, and any `trust_remote_code` implications before operating it.

## Release checklist

Before tagging a release:

1. Regenerate the dependency inventory from `uv.lock`.
2. Verify licenses and required notices for every distributed dependency.
3. Record pinned adapter/model profile revisions separately from credentials.
4. Review the release artifact for source PDFs, page images, raw OCR responses, API keys, and other sensitive data.
