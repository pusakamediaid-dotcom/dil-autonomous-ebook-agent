"""
Production Website Validator
=============================

Memvalidasi bahwa folder `/docs` siap dipakai sebagai website publik produksi
GitHub Pages (branch `main`, folder `/docs`) untuk repository DIL Autonomous
Ebook Agent.

Checks yang dilakukan:
    1. docs/index.html ada dan tidak kosong
    2. docs/ebook.html ada dan tidak kosong
    3. docs/CNAME ada
    4. Isi docs/CNAME persis "agent.pusakamedia.id"
       (tanpa http://, https://, slash, atau spasi/baris tambahan signifikan)
    5. docs/index.html memuat link ke ebook.html
    6. Tidak ada string `../site/` di docs/index.html
    7. Tidak ada placeholder fatal (TODO / FIXME / lorem ipsum)
       di docs/index.html dan docs/ebook.html
    8. docs/index.html dan docs/ebook.html memiliki tag <html>, <head>, <body>

Output:
    output/production_website_validation_report.json

Status:
    PASS    -> semua aman
    WARNING -> domain belum bisa dicek otomatis / non-fatal issue
    FAIL    -> file penting hilang atau link salah

Validator ini AMAN dijalankan dari root repository ataupun dari direktori
manapun selama path repository dapat ditemukan.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


EXPECTED_CNAME = "agent.pusakamedia.id"
PLACEHOLDER_PATTERNS = ["TODO", "FIXME", "lorem ipsum"]


def _find_repo_root(start: Path) -> Path:
    """Cari root repository (folder yang memuat `docs/`)."""
    current = start.resolve()
    for parent in [current, *current.parents]:
        if (parent / "docs").is_dir():
            return parent
    # Fallback: 2 level di atas file ini (src/validators/<file>.py)
    return Path(__file__).resolve().parent.parent.parent


def _read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _check_html_structure(text: str) -> bool:
    lowered = text.lower()
    return all(tag in lowered for tag in ("<html", "<head", "<body"))


def _find_placeholders(text: str) -> List[str]:
    lowered = text.lower()
    found: List[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.lower() in lowered:
            found.append(pattern)
    return found


def validate_production_website(repo_root: Path | None = None) -> Dict[str, Any]:
    """Jalankan seluruh check dan kembalikan dict laporan."""
    if repo_root is None:
        repo_root = _find_repo_root(Path.cwd())

    docs_dir = repo_root / "docs"
    index_path = docs_dir / "index.html"
    ebook_path = docs_dir / "ebook.html"
    cname_path = docs_dir / "CNAME"

    issues: List[str] = []
    warnings: List[str] = []
    checks: Dict[str, Any] = {}

    # --- 1. docs/index.html ada & tidak kosong ---
    index_text = _read_text_safe(index_path)
    index_exists = index_path.is_file()
    index_size = index_path.stat().st_size if index_exists else 0
    checks["index_html_exists"] = index_exists
    checks["index_html_size_bytes"] = index_size
    if not index_exists:
        issues.append("docs/index.html tidak ditemukan.")
    elif index_size == 0:
        issues.append("docs/index.html kosong.")

    # --- 2. docs/ebook.html ada & tidak kosong ---
    ebook_text = _read_text_safe(ebook_path)
    ebook_exists = ebook_path.is_file()
    ebook_size = ebook_path.stat().st_size if ebook_exists else 0
    checks["ebook_html_exists"] = ebook_exists
    checks["ebook_html_size_bytes"] = ebook_size
    if not ebook_exists:
        issues.append("docs/ebook.html tidak ditemukan.")
    elif ebook_size == 0:
        issues.append("docs/ebook.html kosong.")

    # --- 3 & 4. docs/CNAME ada & isi benar ---
    cname_exists = cname_path.is_file()
    checks["cname_exists"] = cname_exists
    cname_value = ""
    cname_value_ok = False
    if cname_exists:
        raw = _read_text_safe(cname_path)
        # Ambil baris non-kosong pertama dan strip whitespace.
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        cname_value = lines[0] if lines else raw.strip()
        cname_value_ok = cname_value == EXPECTED_CNAME
        if not cname_value_ok:
            issues.append(
                f"Isi docs/CNAME tidak sesuai. "
                f"Diharapkan: '{EXPECTED_CNAME}', ditemukan: '{cname_value}'."
            )
        if len(lines) > 1:
            warnings.append(
                "docs/CNAME memiliki lebih dari satu baris non-kosong. "
                "GitHub Pages hanya akan memakai baris pertama."
            )
    else:
        issues.append("docs/CNAME tidak ditemukan.")
    checks["cname_value"] = cname_value
    checks["cname_value_ok"] = cname_value_ok

    # --- 5. link ke ebook.html di index.html ---
    has_ebook_link = False
    if index_exists and index_text:
        # Anggap valid jika ada href="ebook.html" atau href='ebook.html' atau
        # href="./ebook.html" atau href="/ebook.html" atau href="ebook.html#..."
        candidates = [
            'href="ebook.html"',
            "href='ebook.html'",
            'href="./ebook.html"',
            "href='./ebook.html'",
            'href="ebook.html#',
            'href="/ebook.html"',
        ]
        lowered = index_text.lower()
        has_ebook_link = any(c.lower() in lowered for c in candidates)
        if not has_ebook_link:
            issues.append("docs/index.html tidak memiliki link ke ebook.html.")
    checks["index_links_to_ebook"] = has_ebook_link

    # --- 6. tidak ada '../site/' di index.html ---
    has_site_path = False
    if index_text:
        has_site_path = "../site/" in index_text or "/site/" in index_text
        if has_site_path:
            issues.append(
                "docs/index.html masih memuat path '../site/' atau '/site/' yang dapat menyebabkan 404."
            )
    checks["index_has_broken_site_path"] = has_site_path

    # --- 7. tidak ada placeholder fatal ---
    index_placeholders = _find_placeholders(index_text) if index_text else []
    ebook_placeholders = _find_placeholders(ebook_text) if ebook_text else []
    checks["index_placeholders_found"] = index_placeholders
    checks["ebook_placeholders_found"] = ebook_placeholders
    if index_placeholders:
        issues.append(
            f"docs/index.html mengandung placeholder fatal: {', '.join(index_placeholders)}."
        )
    if ebook_placeholders:
        issues.append(
            f"docs/ebook.html mengandung placeholder fatal: {', '.join(ebook_placeholders)}."
        )

    # --- 8. struktur HTML dasar ---
    index_html_ok = _check_html_structure(index_text) if index_text else False
    ebook_html_ok = _check_html_structure(ebook_text) if ebook_text else False
    checks["index_basic_html_valid"] = index_html_ok
    checks["ebook_basic_html_valid"] = ebook_html_ok
    if index_exists and not index_html_ok:
        issues.append("docs/index.html tidak memuat tag <html>, <head>, dan <body> lengkap.")
    if ebook_exists and not ebook_html_ok:
        issues.append("docs/ebook.html tidak memuat tag <html>, <head>, dan <body> lengkap.")

    # --- domain reachability (tidak dicek otomatis) ---
    warnings.append(
        "Validator ini tidak melakukan request HTTP ke domain custom. "
        "Verifikasi manual http://agent.pusakamedia.id/ setelah DNS aktif."
    )

    # --- status final ---
    if issues:
        status = "FAIL"
        message = f"Ditemukan {len(issues)} masalah fatal pada website produksi."
    elif warnings:
        status = "WARNING"
        message = "Website produksi lolos validasi fatal, tetapi ada catatan non-fatal."
    else:
        status = "PASS"
        message = "Website produksi lolos seluruh validasi."

    report: Dict[str, Any] = {
        "validator": "production_website_validator",
        "validator_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "expected_cname": EXPECTED_CNAME,
        "checks": checks,
        "issues": issues,
        "warnings": warnings,
        "status": status,
        "message": message,
    }
    return report


def write_report(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main(argv: List[str] | None = None) -> int:
    repo_root = _find_repo_root(Path.cwd())
    report = validate_production_website(repo_root)
    output_path = repo_root / "output" / "production_website_validation_report.json"
    write_report(report, output_path)

    print(f"[production_website_validator] status: {report['status']}")
    print(f"[production_website_validator] message: {report['message']}")
    if report["issues"]:
        print("[production_website_validator] issues:")
        for it in report["issues"]:
            print(f"  - {it}")
    if report["warnings"]:
        print("[production_website_validator] warnings:")
        for wn in report["warnings"]:
            print(f"  - {wn}")
    print(f"[production_website_validator] report written to: {output_path}")

    # FAIL -> exit 1 (workflow gagal). WARNING/PASS -> exit 0.
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
