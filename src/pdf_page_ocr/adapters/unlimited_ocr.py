"""OpenAI-compatible, one-page-at-a-time Unlimited-OCR endpoint adapter."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import httpx

ADAPTER_PROFILE = "unlimited-ocr-openai-v1"
NORMALIZATION_VERSION = "plain-message-content-v1"
PROMPT = "document parsing."


def endpoint_url(endpoint: str) -> str:
    return endpoint.rstrip("/") + "/chat/completions"


def request_payload(image_path: Path, model: str) -> dict[str, Any]:
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded}"},
                    },
                ],
            }
        ],
        "temperature": 0,
        "stream": False,
        "skip_special_tokens": False,
        "images_config": {"image_mode": "gundam"},
        "custom_params": {"ngram_size": 35, "window_size": 128},
    }


def extract_markdown(response: dict[str, Any]) -> str:
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("endpoint response has no choices[0].message.content") from exc
    if isinstance(content, str):
        return content.strip() + "\n"
    if isinstance(content, list):
        text = "\n".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ).strip()
        if text:
            return text + "\n"
    raise ValueError("endpoint response content is not text")


def call_endpoint(
    client: httpx.Client,
    *,
    endpoint: str,
    image_path: Path,
    model: str,
    api_key: str | None,
) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    response = client.post(
        endpoint_url(endpoint), headers=headers, json=request_payload(image_path, model)
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("endpoint response was not a JSON object")
    return payload
