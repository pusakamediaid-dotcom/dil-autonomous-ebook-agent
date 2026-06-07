"""
DIL Autonomous Ebook Agent - Website Validator

Mengecek site/index.html dan site/style.css.
Validasi dasar HTML: ada tag html, head, body.
Deteksi placeholder fatal seperti TODO, FIXME, lorem ipsum.

Menghasilkan output/website_validation_report.json.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

# Resolve repo root relative to this file (src/validators/website_validator.py)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class WebsiteValidator:
    """Validator untuk output website statis."""

    def __init__(self, site_dir: str = "site", output_dir: str = "output"):
        self.site_dir = REPO_ROOT / site_dir
        self.output_dir = REPO_ROOT / output_dir

    def validate(self) -> Dict[str, Any]:
        index_path = self.site_dir / "index.html"
        style_path = self.site_dir / "style.css"

        index_exists = index_path.exists()
        style_exists = style_path.exists()
        index_size = index_path.stat().st_size if index_exists else 0

        basic_html_valid = False
        placeholder_detected = False
        message_parts = []

        if index_exists and index_size > 0:
            content = index_path.read_text(encoding="utf-8")
            has_html = "<html" in content.lower()
            has_head = "<head>" in content.lower() or "<head " in content.lower()
            has_body = "<body>" in content.lower() or "<body " in content.lower()
            basic_html_valid = has_html and has_head and has_body

            # Placeholder detection (case-insensitive)
            placeholders = ["todo", "fixme", "lorem ipsum", "placeholder", "{subtopic"]
            for ph in placeholders:
                if ph in content.lower():
                    placeholder_detected = True
                    break

            if not basic_html_valid:
                message_parts.append("index.html tidak memiliki struktur html/head/body yang lengkap.")
            if placeholder_detected:
                message_parts.append("Placeholder atau teks generik terdeteksi di index.html.")
        else:
            message_parts.append("index.html tidak ditemukan atau kosong.")

        if not style_exists:
            message_parts.append("style.css tidak ditemukan.")

        # Determine status
        if index_exists and index_size > 0 and basic_html_valid and not placeholder_detected:
            status = "PASS"
            message = "Website valid. HTML lengkap, tidak ada placeholder fatal."
        elif index_exists and index_size > 0 and (not basic_html_valid or placeholder_detected):
            status = "WARNING"
            message = "Website dibuat tetapi ada masalah: " + " ".join(message_parts)
        else:
            status = "FAIL"
            message = "Website tidak valid: " + " ".join(message_parts)

        report = {
            "index_exists": index_exists,
            "style_exists": style_exists,
            "index_size_bytes": index_size,
            "basic_html_valid": basic_html_valid,
            "placeholder_detected": placeholder_detected,
            "status": status,
            "message": message,
        }

        self.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.output_dir / "website_validation_report.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Website validation report: {report_path} ({status})")
        return report


def validate_website(site_dir: str = "site", output_dir: str = "output") -> Dict[str, Any]:
    validator = WebsiteValidator(site_dir, output_dir)
    return validator.validate()


def main() -> None:
    validate_website()


if __name__ == "__main__":
    main()
