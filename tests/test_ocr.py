from __future__ import annotations

import json
from pathlib import Path

import httpx

from pdf_page_ocr.manifest import load_manifest
from pdf_page_ocr.ocr import ocr_manifest
from pdf_page_ocr.prepare import prepare_pdf


def test_ocr_request_shape_and_resume(sample_pdf: Path, tmp_path: Path) -> None:
    manifest_path = prepare_pdf(sample_pdf, tmp_path / "run")
    received: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        received.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": "# page"}}]})

    transport = httpx.MockTransport(handler)
    result = ocr_manifest(
        manifest_path,
        endpoint="https://ocr.example/v1",
        api_key="not-persisted",
        transport=transport,
    )
    assert len(received) == 2
    assert received[0].url == "https://ocr.example/v1/chat/completions"
    assert received[0].headers["authorization"] == "Bearer not-persisted"
    payload = json.loads(received[0].content)
    assert payload["model"] == "Unlimited-OCR"
    assert payload["messages"][0]["content"][0]["text"] == "document parsing."
    image_url = payload["messages"][0]["content"][1]["image_url"]["url"]
    assert image_url.startswith("data:image/png;base64,")
    assert payload["images_config"] == {"image_mode": "gundam"}
    assert payload["custom_params"] == {"ngram_size": 35, "window_size": 128}
    assert all(page.state == "succeeded" for page in result.pages)
    assert all(page.adapter_profile == "unlimited-ocr-openai-v1" for page in result.pages)
    assert all(page.normalization_version == "plain-message-content-v1" for page in result.pages)
    assert "not-persisted" not in manifest_path.read_text(encoding="utf-8")

    ocr_manifest(manifest_path, endpoint="https://ocr.example/v1", transport=transport)
    assert len(received) == 2
    manifest = load_manifest(manifest_path)
    assert all(page.attempts == 1 for page in manifest.pages)
