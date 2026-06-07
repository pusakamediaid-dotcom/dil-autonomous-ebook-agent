"""
DIL Autonomous Ebook Agent - Site Builder

Membuat folder site jika belum ada.
Mengambil input dari output/ebook.md, jika tidak ada gunakan samples/ebook.md.
Menghasilkan site/index.html, site/style.css, dan site/metadata.json.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Resolve repo root relative to this file (src/exporters/site_builder.py)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT / "src" / "exporters") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src" / "exporters"))

from markdown_to_html import (
    read_markdown,
    markdown_to_html,
    wrap_html_document,
    write_html,
)


def ensure_site_dir() -> Path:
    """Memastikan direktori site/ ada."""
    site_dir = REPO_ROOT / "site"
    site_dir.mkdir(parents=True, exist_ok=True)
    return site_dir


def find_source_markdown() -> Optional[Path]:
    """Mencari sumber Markdown: output/ebook.md, lalu samples/ebook.md."""
    candidates = [REPO_ROOT / "output" / "ebook.md", REPO_ROOT / "samples" / "ebook.md"]
    for candidate in candidates:
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate
    return None


def build_site() -> None:
    """Build site/index.html, pastikan site/style.css tersedia, dan buat metadata.json."""
    site_dir = ensure_site_dir()
    source = find_source_markdown()

    if source is None:
        # Fallback: buat index.html minimal yang menjelaskan tidak ada konten
        title = "DIL Autonomous Ebook Agent — Preview"
        body = (
            "<h1>DIL Autonomous Ebook Agent</h1>"
            "<p>Belum ada konten ebook yang tersedia.</p>"
            "<p>Jalankan generator terlebih dahulu atau pastikan <code>samples/ebook.md</code> ada.</p>"
        )
        doc = wrap_html_document(title, body, css_path=str(site_dir / "style.css"))
        write_html(str(site_dir / "index.html"), doc)
        metadata = {
            "title": title,
            "build_time": datetime.now(timezone.utc).isoformat(),
            "source": None,
            "status": "NO_CONTENT",
            "message": "Tidak ada output/ebook.md atau samples/ebook.md. Site dibuat dengan halaman fallback.",
        }
        (site_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print("Site built with fallback (no content)")
        return

    md_text = read_markdown(str(source))
    title = "DIL Autonomous Ebook Agent — Preview"
    # Coba ambil judul dari baris pertama # Judul
    first_line = md_text.strip().splitlines()[0] if md_text.strip() else ""
    if first_line.startswith("# "):
        title = first_line[2:].strip()

    body = markdown_to_html(md_text)
    doc = wrap_html_document(title, body, css_path=str(site_dir / "style.css"))
    write_html(str(site_dir / "ebook.html"), doc)

    # Pastikan style.css tersedia di site/
    css_source = site_dir / "style.css"
    if not css_source.exists():
        # Agar konsisten, kita buat style.css minimal di site/
        css_source.write_text(
            """/* DIL Autonomous Ebook Agent - Site Styles */
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; line-height: 1.7; max-width: 720px; margin: 0 auto; padding: 2rem 1rem; color: #1a1a2e; background: #fff; }
h1, h2, h3 { color: #16213e; margin-top: 1.5em; margin-bottom: 0.5em; }
h1 { font-size: 1.8rem; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.25rem; }
code { background: #f3f4f6; padding: 0.15em 0.3em; border-radius: 0.25em; font-size: 0.95em; }
pre { background: #f3f4f6; padding: 1em; border-radius: 0.5em; overflow-x: auto; }
blockquote { border-left: 4px solid #e5e7eb; padding-left: 1em; color: #4b5563; margin-left: 0; }
ul, ol { padding-left: 1.25em; }
hr { border: 0; border-top: 1px solid #e5e7eb; margin: 2em 0; }
a { color: #0f766e; }
""",
            encoding="utf-8",
        )

    metadata = {
        "title": title,
        "build_time": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "status": "OK",
        "message": f"Site built from {source}",
    }
    (site_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Site built: {site_dir}/ebook.html from {source}")


def main() -> None:
    build_site()


if __name__ == "__main__":
    main()
