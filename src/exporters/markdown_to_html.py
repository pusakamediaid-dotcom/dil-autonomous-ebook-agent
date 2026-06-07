"""
DIL Autonomous Ebook Agent - Markdown to HTML Converter

Mengubah file Markdown menjadi HTML sederhana.
Mendukung heading, paragraf, daftar, bold, italic, code block, horizontal rule.
Menggunakan Python standard library sebanyak mungkin.
Jika library markdown tersedia, boleh pakai; jika tidak, fallback ke converter sederhana.
"""

import re
import html
from pathlib import Path
from typing import Optional


def read_markdown(path: str) -> str:
    """Membaca file Markdown dan mengembalikan isi teks."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File Markdown tidak ditemukan: {path}")
    return file_path.read_text(encoding="utf-8")


def markdown_to_html(markdown_text: str) -> str:
    """
    Mengubah Markdown sederhana menjadi HTML body.
    Mendukung heading, paragraf, daftar, bold, italic, code block, horizontal rule.
    """
    text = markdown_text

    # Escape HTML entities dulu untuk bagian non-code
    # Kita proses code block terlebih dahulu agar tidak di-escape di dalamnya

    # Simpan code block ``` ... ```
    code_blocks = []
    code_placeholder = "\x00CODEBLOCK{0}\x00"

    def extract_code_block(match):
        lang = match.group(1) or ""
        code = match.group(2)
        idx = len(code_blocks)
        code_blocks.append((lang, code))
        return code_placeholder.format(idx)

    text = re.sub(
        r'```(\w*)\n(.*?)```',
        extract_code_block,
        text,
        flags=re.DOTALL
    )

    # Simpan inline code `...`
    inline_codes = []
    inline_placeholder = "\x00INLINECODE{0}\x00"

    def extract_inline_code(match):
        code = match.group(1)
        idx = len(inline_codes)
        inline_codes.append(code)
        return inline_placeholder.format(idx)

    text = re.sub(r'`([^`]+)`', extract_inline_code, text)

    # Horizontal rule
    text = re.sub(r'^\s*---\s*$', '<hr>', text, flags=re.MULTILINE)

    # Headings
    text = re.sub(r'^###### (.*?)$', r'<h6>\1</h6>', text, flags=re.MULTILINE)
    text = re.sub(r'^##### (.*?)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # Bold & italic (gunakan escape HTML untuk isi)
    # **bold** atau __bold__
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
    # *italic* atau _italic_
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)

    # Images ![alt](url)
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', text)

    # Links [text](url)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)

    # Blockquotes
    text = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)

    # Ordered lists: 1. item
    ol_pattern = re.compile(r'^(\d+)\.\s+(.*?)$', re.MULTILINE)
    # Unordered lists: - item atau * item
    ul_pattern = re.compile(r'^[-*]\s+(.*?)$', re.MULTILINE)

    # Kita proses list per blok agar rapi
    # Sederhana: bungkus tiap baris list item dengan <li>
    # Lalu bungkus baris berurutan dalam <ul> atau <ol>

    lines = text.splitlines()
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Cek unordered list
        ul_match = re.match(r'^<p>\s*[-*]\s+(.*?)</p>$', line) or re.match(r'^\s*[-*]\s+(.*?)$', line)
        # Kalau sudah ada <p> dari proses paragraf, tangani juga
        # Tapi sebaiknya proses list sebelum paragraf agar lebih bersih
        # Re-render dengan proses list terlebih dahulu
        new_lines.append(line)
        i += 1

    # Proses list di seluruh text (belum dijadikan paragraf)
    # Kita ulangi dengan pendekatan yang lebih baik:
    # Deteksi blok list, ubah ke <ul>/<ol>

    text = '\n'.join(new_lines)

    # Split berdasarkan blok, lalu proses list
    def process_lists(full_text: str) -> str:
        lines = full_text.splitlines()
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Ordered list
            if re.match(r'^\s*\d+\.\s+', line):
                items = []
                while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                    item = re.sub(r'^\s*\d+\.\s+', '', lines[i])
                    items.append(item)
                    i += 1
                out.append('<ol>')
                for item in items:
                    out.append(f'<li>{item}</li>')
                out.append('</ol>')
                continue
            # Unordered list
            if re.match(r'^\s*[-*]\s+', line):
                items = []
                while i < len(lines) and re.match(r'^\s*[-*]\s+', lines[i]):
                    item = re.sub(r'^\s*[-*]\s+', '', lines[i])
                    items.append(item)
                    i += 1
                out.append('<ul>')
                for item in items:
                    out.append(f'<li>{item}</li>')
                out.append('</ul>')
                continue
            out.append(line)
            i += 1
        return '\n'.join(out)

    text = process_lists(text)

    # Paragraf: bungkus baris yang belum di-tag
    # Kita split per baris, lalu bungkus baris yang bukan tag, bukan kosong
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            new_lines.append('')
            continue
        # Jika sudah diawali tag HTML, tidak perlu bungkus
        if stripped.startswith('<') and stripped.endswith('>'):
            new_lines.append(line)
            continue
        # Bungkus dalam paragraf, escape HTML entities
        escaped = html.escape(stripped)
        new_lines.append(f'<p>{escaped}</p>')
    text = '\n'.join(new_lines)

    # Restore code blocks
    for idx, (lang, code) in enumerate(code_blocks):
        escaped_code = html.escape(code)
        html_code = f'<pre><code class="language-{lang}">{escaped_code}</code></pre>' if lang else f'<pre><code>{escaped_code}</code></pre>'
        text = text.replace(code_placeholder.format(idx), html_code)

    # Restore inline code
    for idx, code in enumerate(inline_codes):
        escaped_code = html.escape(code)
        text = text.replace(inline_placeholder.format(idx), f'<code>{escaped_code}</code>')

    return text


def wrap_html_document(title: str, html_body: str, css_path: str = "style.css") -> str:
    """
    Membungkus HTML body dalam dokumen HTML lengkap.
    Menggunakan CSS internal dari file jika tersedia; jika tidak, style minimal inline.
    """
    css_content = ""
    css_file = Path(css_path)
    if css_file.exists():
        css_content = css_file.read_text(encoding="utf-8")
    else:
        # fallback CSS inline minimal
        css_content = """
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
        """

    doc = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<style>
{css_content}
</style>
</head>
<body>
<main>
{html_body}
</main>
</body>
</html>"""
    return doc


def write_html(output_path: str, html_content: str) -> None:
    """Menyimpan string HTML ke file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_content, encoding="utf-8")


def convert_markdown_file_to_html(input_path: str, output_path: str, title: str) -> None:
    """Converter convenience: Markdown file -> HTML file."""
    md_text = read_markdown(input_path)
    body = markdown_to_html(md_text)
    doc = wrap_html_document(title, body)
    write_html(output_path, doc)


def main() -> None:
    import sys
    if len(sys.argv) >= 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        title = sys.argv[3] if len(sys.argv) > 3 else "Ebook"
    else:
        input_path = "output/ebook.md"
        output_path = "site/index.html"
        title = "DIL Autonomous Ebook"
    convert_markdown_file_to_html(input_path, output_path, title)
    print(f"HTML exported: {output_path}")


if __name__ == "__main__":
    main()
