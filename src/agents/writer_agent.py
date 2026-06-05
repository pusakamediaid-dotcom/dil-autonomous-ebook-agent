"""
DIL Autonomous Ebook Agent - Writer Agent

Menghasilkan konten ebook berbasis outline.
Setiap subbab memiliki Metode 5-Lapis: KONSEP, ANALOGI, RUMUS, CONTOH, APLIKASI.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger
from core.run_context import RunContext
from core.api_client import AIClient, get_ai_client
from core.secret_manager import get_secret_manager

logger = get_logger(__name__)


class WriterAgent:
    """
    Agent yang menulis konten ebook berbasis outline.
    Setiap subsection memiliki 5 lapisan wajib.
    """
    
    def __init__(self):
        """Inisialisasi WriterAgent."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.outline: Dict[str, Any] = {}
        self.content: List[str] = []
        self.words_written: int = 0
        self.foreign_text_detected: bool = False
        self.ai_client: Optional[AIClient] = None
        self.api_available: bool = False
    
    def load_outline(self, outline_file: str = "output/outline.json") -> Dict[str, Any]:
        """Memuat outline dari file."""
        outline_path = Path(outline_file)
        
        try:
            with open(outline_path, 'r', encoding='utf-8') as f:
                outline = json.load(f)
                logger.info(f"Loaded outline dari {outline_path}")
                self.outline = outline
                return outline
        except FileNotFoundError:
            logger.warning(f"Outline tidak ditemukan: {outline_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing outline: {e}")
            return {}
    
    def setup_ai_client(self) -> bool:
        """Setup AI client dengan provider yang tersedia."""
        try:
            self.ai_client = get_ai_client()
            secret_manager = get_secret_manager()
            available = secret_manager.get_available_providers()
            
            if not available:
                logger.info("Tidak ada provider API tersedia - menggunakan fallback template")
                self.api_available = False
                return False
            
            self.api_available = True
            logger.info(f"AI Client siap dengan {len(available)} provider")
            return True
        except Exception as e:
            logger.error(f"Error setup AI client: {e}")
            self.api_available = False
            return False
    
    def write_header(self, ebook_title: str, target_audience: str, reading_level: str, timestamp: str) -> str:
        """Menulis header ebook."""
        lines = [
            f"# {ebook_title}",
            "",
            f"**Target Pembaca:** {target_audience}",
            f"**Level:** {reading_level}",
            f"**Dibuat:** {timestamp}",
            "",
            "---",
            ""
        ]
        return '\n'.join(lines)
    
    def write_toc(self, chapters: List[Dict[str, Any]]) -> str:
        """Menulis daftar isi."""
        lines = ["# Daftar Isi", ""]
        
        for chapter in chapters:
            chapter_num = chapter.get("chapter_number", 0)
            chapter_title = chapter.get("chapter_title", "")
            
            lines.append(f"{chapter_num}. {chapter_title}")
            
            for section in chapter.get("sections", []):
                for subsection in section.get("subsections", []):
                    sub_num = subsection.get("subtopic_number", "")
                    sub_title = subsection.get("subtopic_title", "")
                    lines.append(f"   {sub_num} {sub_title}")
            
            lines.append("")
        
        lines.append("---\n")
        return '\n'.join(lines)
    
    def write_chapter_header(self, chapter: Dict[str, Any]) -> str:
        """Menulis header bab."""
        chapter_num = chapter.get("chapter_number", 1)
        chapter_title = chapter.get("chapter_title", "")
        description = chapter.get("description", "")
        objectives = chapter.get("learning_objectives", [])
        
        lines = [
            "",
            f"## Bab {chapter_num} — {chapter_title}",
            ""
        ]
        
        if description:
            lines.append(f"*{description}*")
            lines.append("")
        
        if objectives:
            lines.append("**Tujuan Pembelajaran:**")
            for obj in objectives[:3]:
                lines.append(f"- {obj}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def write_subsection_header(self, subsection: Dict[str, Any]) -> str:
        """Menulis header subbab."""
        sub_num = subsection.get("subtopic_number", "")
        sub_title = subsection.get("subtopic_title", "")
        return f"### {sub_num} {sub_title}\n"
    
    def generate_concept_content(self, title: str) -> str:
        """Menghasilkan konten [KONSEP]."""
        return f"""#### [KONSEP]

Dalam bagian ini, kita akan membahas secara mendalam tentang **{title}**.

**Definisi:**
{title} adalah konsep fundamental yang penting untuk dipahami dalam konteks pembelajaran ini. Pemahaman yang baik tentang konsep ini akan membantu pembaca menguasai topik secara komprehensif.

**Penjelasan Utama:**
Konsep {title} terdiri dari beberapa elemen penting yang saling berkaitan. Dengan memahami setiap elemen, pembaca akan dapat mengaplikasikan pengetahuan ini dalam situasi praktis.

**Prinsip Dasar:**
1. Pahami fondasi teori
2. Identifikasi aplikasi praktis
3. Latihan dengan contoh nyata
4. Evaluasi pemahaman secara berkala

"""
    
    def generate_analogy_content(self, title: str) -> str:
        """Menghasilkan konten [ANALOGI]."""
        return f"""#### [ANALOGI]

Untuk lebih mudah memahami **{title}**, bayangkan prosesnya seperti membangun sebuah rumah:

**Fondasi** mewakili pemahaman dasar yang kuat. Tanpa fondasi yang baik, bangunan tidak akan kokoh.

**Tiang dan Dinding** mewakili konsep-konsep penopang yang menghubungkan fondasi dengan bagian lainnya.

**Atap** mewakili hasil akhir yang melindungi seluruh bangunan dan memberikan manfaat.

Dengan memahami analogi ini, kita bisa melihat bagaimana {title} berfungsi secara keseluruhan dalam sebuah sistem yang terorganisir.

"""
    
    def generate_rumus_content(self, title: str) -> str:
        """Menghasilkan konten [RUMUS]."""
        return f"""#### [RUMUS]

**Prinsip Utama {title}:**

Untuk mengaplikasikan {title} secara efektif, perhatikan langkah-langkah berikut:

1. Identifikasi komponen utama
2. Pahami hubungan antar komponen
3. Terapkan dengan urutan yang benar
4. Evaluasi hasil secara berkala

**Catatan Penting:**
Prinsip ini berlaku umum dan dapat diadaptasi sesuai kebutuhan spesifik. Selalu pertimbangkan konteks sebelum mengaplikasikan.

```
Format dokumentasi:
- Komponen utama
- Langkah-langkah aplikasi
- Kriteria keberhasilan
```

"""
    
    def generate_contoh_content(self, title: str, chapter_num: int = 1) -> str:
        """Menghasilkan konten [CONTOH]."""
        return f"""#### [CONTOH]

**Contoh Praktis Penerapan {title}:**

Dalam proyek nyata, penerapan {title} dapat dilakukan dengan langkah-langkah berikut:

**Langkah 1: Persiapan**
- Identifikasi kebutuhan
- Siapkan resources yang diperlukan
- Tentukan timeline execution

**Langkah 2: Implementasi**
- Execute tahap pertama
- Monitor progress
- Adjust jika diperlukan

**Langkah 3: Evaluasi**
- Review hasil
- Identifikasi improvement
- Document learning

**Contoh Implementasi:**
```
# Pseudo-code untuk {title}
def implement_{title.replace(' ', '_').lower()}():
    persiapkan()
    eksekusi()
    evaluasi()
    return hasil
```

"""
    
    def generate_aplikasi_content(self, title: str) -> str:
        """Menghasilkan konten [APLIKASI]."""
        return f"""#### [APLIKASI]

**Penerapan Nyata {title} dalam Kehidupan Sehari-hari:**

{title} memiliki banyak aplikasi praktis yang dapat memberikan manfaat langsung:

1. **Aplikasi dalam Pembelajaran**
   - Mempermudah pemahaman konsep kompleks
   - Memberikan kerangka berpikir sistematis

2. **Aplikasi dalam Profesional**
   - Meningkatkan efisiensi kerja
   - Memperbaiki kualitas output

3. **Aplikasi dalam Pengambilan Keputusan**
   - Menyediakan kerangka analisis
   - Membantu evaluasi alternatif

**Best Practices:**
- Selalu mulai dengan pemahaman dasar
- Praktikkan secara konsisten
- Evaluate dan improve secara berkala

**Tips Penggunaan:**
Manfaatkan {title} sebagai alat bantu untuk mencapai tujuan pembelajaran dan profesional Anda.

"""
    
    def write_subsection_content(self, subsection: Dict[str, Any], chapter_num: int) -> str:
        """Menulis konten lengkap untuk satu subsection."""
        title = subsection.get("subtopic_title", "Subtopik")
        
        lines = []
        lines.append(self.write_subsection_header(subsection))
        lines.append(self.generate_concept_content(title))
        lines.append(self.generate_analogy_content(title))
        lines.append(self.generate_rumus_content(title))
        lines.append(self.generate_contoh_content(title, chapter_num))
        lines.append(self.generate_aplikasi_content(title))
        lines.append("---\n")
        
        content = '\n'.join(lines)
        self.words_written += len(content.split())
        
        return content
    
    def write_chapter(self, chapter: Dict[str, Any]) -> str:
        """Menulis konten lengkap satu bab."""
        lines = []
        lines.append(self.write_chapter_header(chapter))
        
        sections = chapter.get("sections", [])
        
        for section in sections:
            subsections = section.get("subsections", [])
            
            for subsection in subsections:
                chapter_num = chapter.get("chapter_number", 1)
                content = self.write_subsection_content(subsection, chapter_num)
                lines.append(content)
        
        return ''.join(lines)
    
    def write_closing(self) -> str:
        """Menulis penutup ebook."""
        return """
---

# Ringkasan

Dalam ebook ini, kita telah membahas konsep-konsep penting yang diperlukan untuk memahami topik secara komprehensif. Dengan memahami setiap bab dan subbab, pembaca diharapkan dapat:

1. Memahami fondasi teori secara mendalam
2. Menerapkan pengetahuan dalam praktik
3. Mengembangkan kemampuan analitis
4. Mengaplikasikan dalam konteks nyata

---

**Catatan:**
Ebook ini disusun untuk tujuan pembelajaran. Untuk informasi lebih lanjut, silakan konsultasikan dengan ahli di bidang terkait.

---

*Akhir dari dokumen*
"""
    
    def write_ebook(self, run_context: RunContext) -> str:
        """Menulis konten ebook lengkap."""
        chapters = self.outline.get("chapters", [])
        
        self.setup_ai_client()
        
        lines = []
        
        lines.append(self.write_header(
            self.outline.get("ebook_title", "Untitled Ebook"),
            run_context.target_audience or "General Audience",
            run_context.reading_level or "intermediate",
            run_context.timestamp_start
        ))
        
        lines.append(self.write_toc(chapters))
        
        for chapter in chapters:
            chapter_content = self.write_chapter(chapter)
            lines.append(chapter_content)
        
        lines.append(self.write_closing())
        
        return ''.join(lines)
    
    def validate_content(self, content: str) -> tuple[bool, List[str]]:
        """Memvalidasi konten yang dihasilkan."""
        errors = []
        
        foreign_patterns = [
            r'[\u4e00-\u9fff]',
            r'[\u0400-\u04ff]',
            r'[\u0600-\u06ff]',
            r'[\u3040-\u309f\u30a0-\u30ff]'
        ]
        
        for pattern in foreign_patterns:
            if re.search(pattern, content):
                errors.append(f"Teks asing terdeteksi")
                self.foreign_text_detected = True
        
        placeholder_patterns = [r'lorem ipsum', r'placeholder', r'todo', r'fixme']
        for pattern in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(f"Placeholder mentah terdeteksi: {pattern}")
        
        required_layers = ["[KONSEP]", "[ANALOGI]", "[RUMUS]", "[CONTOH]", "[APLIKASI]"]
        for layer in required_layers:
            if layer not in content:
                errors.append(f"Lapisan hilang: {layer}")
        
        return len(errors) == 0, errors
    
    def save_ebook(self, output_file: str = "output/ebook.md") -> None:
        """Menyimpan konten ebook ke file markdown."""
        if not self.content:
            logger.warning("Tidak ada konten untuk disimpan")
            return
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        content_str = ''.join(self.content) if isinstance(self.content, list) else self.content
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content_str)
        
        logger.info(f"Ebook disimpan ke {output_path} ({self.words_written} kata)")
    
    def execute(self, run_context: RunContext) -> str:
        """Menjalankan writer agent."""
        logger.info("WriterAgent executing...")
        
        outline = self.load_outline()
        
        if not outline:
            logger.error("Tidak ada outline tersedia")
            return ""
        
        content = self.write_ebook(run_context)
        self.content = content
        
        is_valid, errors = self.validate_content(content)
        if not is_valid:
            logger.warning(f"Content validation errors: {errors}")
        
        self.save_ebook()
        
        logger.info(f"WriterAgent completed - ditulis {self.words_written} kata")
        
        return content


def run_writer_agent(run_context: RunContext) -> str:
    """Fungsi convenience untuk menjalankan WriterAgent."""
    agent = WriterAgent()
    return agent.execute(run_context)