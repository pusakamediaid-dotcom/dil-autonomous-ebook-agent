"""PDFMonkey integration client.

This module is intentionally secret-free. It reads PDFMonkey credentials from
environment variables so GitHub Actions can use repository secrets safely.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


class PDFMonkeyError(RuntimeError):
    """Raised when PDFMonkey request fails in a sanitized way."""


@dataclass
class PDFMonkeyConfig:
    api_key: str
    template_id: str
    base_url: str = "https://api.pdfmonkey.io/api/v1"
    timeout: int = 60

    @classmethod
    def from_env(cls) -> "PDFMonkeyConfig":
        api_key = os.getenv("PDFMONKEY_API_KEY", "").strip()
        template_id = os.getenv("PDFMONKEY_TEMPLATE_ID", "").strip()
        base_url = os.getenv("PDFMONKEY_BASE_URL", "https://api.pdfmonkey.io/api/v1").strip()

        if not api_key:
            raise PDFMonkeyError("PDFMONKEY_API_KEY is not configured.")
        if not template_id:
            raise PDFMonkeyError("PDFMONKEY_TEMPLATE_ID is not configured.")

        return cls(api_key=api_key, template_id=template_id, base_url=base_url.rstrip("/"))


class PDFMonkeyClient:
    def __init__(self, config: Optional[PDFMonkeyConfig] = None) -> None:
        self.config = config or PDFMonkeyConfig.from_env()

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.config.base_url}{path}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            safe_body = ""
            try:
                safe_body = exc.read().decode("utf-8")[:500]
            except Exception:
                safe_body = ""
            raise PDFMonkeyError(f"PDFMonkey HTTP error {exc.code}. {safe_body}") from exc
        except urllib.error.URLError as exc:
            raise PDFMonkeyError("PDFMonkey network error. Check connection or API endpoint.") from exc
        except json.JSONDecodeError as exc:
            raise PDFMonkeyError("PDFMonkey returned invalid JSON.") from exc

    def create_document(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        document_payload = {
            "document": {
                "document_template_id": self.config.template_id,
                "payload": payload,
                "status": "pending",
            }
        }
        return self._request("POST", "/documents", document_payload)

    def get_document(self, document_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/documents/{document_id}")

    def wait_for_document(self, document_id: str, timeout_seconds: int = 180, interval_seconds: int = 5) -> Dict[str, Any]:
        deadline = time.time() + timeout_seconds
        last_doc: Dict[str, Any] = {}

        while time.time() < deadline:
            last_doc = self.get_document(document_id)
            document = last_doc.get("document", last_doc)
            status = str(document.get("status", "")).lower()
            if status in {"success", "done", "generated", "completed"}:
                return last_doc
            if status in {"failure", "failed", "error"}:
                raise PDFMonkeyError("PDFMonkey document generation failed.")
            time.sleep(interval_seconds)

        raise PDFMonkeyError("PDFMonkey document generation timed out.")


def build_ebook_payload_from_markdown(title: str, markdown: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "title": title,
        "metadata": metadata or {},
        "markdown": markdown,
        "project": "DIL 50 Seri Ebook Teknik Elektro Premium",
        "format": "A4 portrait premium PDF",
    }
