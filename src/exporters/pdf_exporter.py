"""
DIL Autonomous Ebook Agent - PDF Exporter

Mencoba mengubah output/ebook.md menjadi output/ebook.pdf.
Prioritas:
1. Jika pandoc tersedia, gunakan pandoc.
2. Jika pandoc tidak tersedia, buat output/ebook_pdf_fallback.txt berisi instruksi manual export.

Jangan membuat workflow gagal hanya karena PDF dependency tidak tersedia.
Output PDF bersifat best-effort pada tahap ini.
"""

import shutil
import subprocess
from pathlib import Path

# Resolve repo root relative to this file (src/exporters/pdf_exporter.py)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def pandoc_available() -> bool:
    """Cek apakah pandoc tersedia di PATH."""
    return shutil.which("pandoc") is not None


def export_pdf_with_pandoc(input_md: str, output_pdf: str) -> bool:
    """Export PDF menggunakan pandoc."""
    input_path = Path(input_md)
    output_path = Path(output_pdf)
    if not input_path.exists():
        print(f"PDF export skipped: input tidak ditemukan: {input_md}")
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            [
                "pandoc",
                str(input_path),
                "-o",
                str(output_path),
                "--pdf-engine=xelatex",
                "-V",
                "geometry:margin=2.5cm",
                "-V",
                "fontsize=11pt",
                "--toc",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            print(f"PDF exported via pandoc: {output_pdf}")
            return True
        else:
            print(f"Pandoc failed (rc={result.returncode}): {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception running pandoc: {e}")
        return False


def create_pdf_fallback_note(input_md: str) -> None:
    """Buat catatan fallback jika pandoc tidak tersedia."""
    input_path = Path(input_md)
    output_path = REPO_ROOT / "output" / "ebook_pdf_fallback.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    note = """PDF Export - Fallback Note
============================

Pandoc tidak tersedia di environment saat ini, sehingga PDF tidak bisa
dibangun secara otomatis pada tahap ini.

Cara manual untuk membuat PDF:
1. Instal pandoc di komputer lokal: https://pandoc.org/installing.html
2. Instal LaTeX engine (misalnya xelatex atau lualatex).
3. Jalankan perintah berikut dari root repository:

   pandoc output/ebook.md -o output/ebook.pdf --pdf-engine=xelatex -V geometry:margin=2.5cm --toc

Alternatif lain:
- Gunakan VS Code extension Markdown PDF.
- Gunakan layanan online yang mendukung Markdown to PDF.
- Gunakan WeasyPrint (Python library) jika ingin otomatis tanpa LaTeX:

   pip install markdown weasyprint
   python -c "import markdown; from weasyprint import HTML; md=open('output/ebook.md').read(); html=markdown.markdown(md); HTML(string=html).write_pdf('output/ebook.pdf')"

Status tahap ini: best-effort. PDF akan otomatis tersedia jika pandoc
terinstal di environment runner GitHub Actions maupun lokal.
"""
    if input_path.exists():
        note += f"\nSumber Markdown: {input_path.resolve()}\n"
    else:
        note += f"\nSumber Markdown tidak ditemukan: {input_path}\n"

    output_path.write_text(note, encoding="utf-8")
    print(f"PDF fallback note created: {output_path}")


def main() -> None:
    input_md = REPO_ROOT / "output" / "ebook.md"
    output_pdf = REPO_ROOT / "output" / "ebook.pdf"

    if pandoc_available():
        success = export_pdf_with_pandoc(str(input_md), str(output_pdf))
        if not success:
            create_pdf_fallback_note(str(input_md))
    else:
        print("Pandoc tidak tersedia. Membuat fallback note.")
        create_pdf_fallback_note(str(input_md))


if __name__ == "__main__":
    main()
