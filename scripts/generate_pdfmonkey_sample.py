"""Generate a sample PDFMonkey document from repository content.

Usage in GitHub Actions:
    python scripts/generate_pdfmonkey_sample.py

Required environment variables:
    PDFMONKEY_API_KEY
    PDFMONKEY_TEMPLATE_ID

Optional:
    PDFMONKEY_BASE_URL
"""

from __future__ import annotations

import json
from pathlib import Path

from src.integrations.pdfmonkey_client import PDFMonkeyClient, build_ebook_payload_from_markdown


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


SAMPLE_MARKDOWN = """# Contoh Ebook Teknik Elektro Premium

## Dasar Tegangan, Arus, dan Hambatan

Ebook contoh ini digunakan untuk menguji integrasi PDFMonkey pada repository DIL Autonomous Ebook Agent.

### Box Info
Tegangan adalah beda potensial listrik yang mendorong arus melalui rangkaian tertutup.

### Tabel Ringkas
| Konsep | Satuan | Fungsi |
| --- | --- | --- |
| Tegangan | V | Dorongan listrik |
| Arus | A | Aliran muatan |
| Hambatan | Ω | Pembatas arus |

### Rumus
V = I × R

### Catatan K3
Jangan melakukan praktik langsung pada tegangan PLN tanpa pengawasan teknisi kompeten.
"""


def main() -> None:
    client = PDFMonkeyClient()
    payload = build_ebook_payload_from_markdown(
        title="Contoh Ebook Teknik Elektro Premium",
        markdown=SAMPLE_MARKDOWN,
        metadata={
            "kode_seri": "CONTOH-API-01",
            "target_pembaca": "Pemula teknik elektro",
            "status": "PDFMonkey integration test",
        },
    )

    created = client.create_document(payload)
    document = created.get("document", created)
    document_id = str(document.get("id") or document.get("document_id") or "")

    if not document_id:
        raise RuntimeError("PDFMonkey did not return a document id.")

    final_doc = client.wait_for_document(document_id)

    (OUTPUT_DIR / "pdfmonkey_created.json").write_text(json.dumps(created, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "pdfmonkey_final.json").write_text(json.dumps(final_doc, indent=2), encoding="utf-8")

    doc_data = final_doc.get("document", final_doc)
    download_url = doc_data.get("download_url") or doc_data.get("url") or doc_data.get("public_url")
    report = {
        "status": doc_data.get("status"),
        "document_id": document_id,
        "download_url": download_url,
        "note": "If download_url is empty, open pdfmonkey_final.json artifact and check PDFMonkey response fields.",
    }
    (OUTPUT_DIR / "pdfmonkey_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
