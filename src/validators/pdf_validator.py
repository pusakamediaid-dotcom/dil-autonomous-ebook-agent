"""
DIL Autonomous Ebook Agent - PDF Validator

Mengecek apakah output/ebook.pdf ada dan ukurannya lebih dari 1 KB.
Jika PDF tidak ada tetapi output/ebook_pdf_fallback.txt ada,
status = WARNING, bukan FAILED.

Menghasilkan output/pdf_validation_report.json.
"""

import json
from pathlib import Path
from typing import Dict, Any

# Resolve repo root relative to this file (src/validators/pdf_validator.py)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class PDFValidator:
    """Validator untuk output PDF."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = REPO_ROOT / output_dir

    def validate(self) -> Dict[str, Any]:
        pdf_path = self.output_dir / "ebook.pdf"
        fallback_path = self.output_dir / "ebook_pdf_fallback.txt"

        pdf_exists = pdf_path.exists() and pdf_path.stat().st_size > 1024
        pdf_size = pdf_path.stat().st_size if pdf_path.exists() else 0
        fallback_exists = fallback_path.exists() and fallback_path.stat().st_size > 0

        if pdf_exists:
            status = "PASS"
            message = f"PDF ditemukan ({pdf_size} bytes)."
        elif fallback_exists:
            status = "WARNING"
            message = (
                "PDF tidak ditemukan, tetapi fallback note tersedia. "
                "Pandoc mungkin belum tersedia di environment. "
                "Lihat output/ebook_pdf_fallback.txt untuk instruksi manual."
            )
        else:
            status = "FAIL"
            message = (
                "PDF tidak ditemukan dan fallback note juga tidak ada. "
                "PDF export gagal atau belum dijalankan."
            )

        report = {
            "pdf_exists": pdf_exists,
            "pdf_size_bytes": pdf_size,
            "fallback_exists": fallback_exists,
            "status": status,
            "message": message,
        }

        report_path = self.output_dir / "pdf_validation_report.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"PDF validation report: {report_path} ({status})")
        return report


def validate_pdf(output_dir: str = "output") -> Dict[str, Any]:
    validator = PDFValidator(output_dir)
    return validator.validate()


def main() -> None:
    validate_pdf()


if __name__ == "__main__":
    main()
