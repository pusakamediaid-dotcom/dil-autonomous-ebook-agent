"""
DIL Autonomous Ebook Agent - Writer Agent

Menghasilkan konten ebook berbasis outline dengan AI.
Memanggil AIClient untuk menulis setiap subbab.
Fallback template lokal jika API gagal.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger
from core.run_context import RunContext
from core.api_client import AIClient, get_ai_client
from core.secret_manager import SecretManager, get_secret_manager

logger = get_logger(__name__)


class WriterAgent:
    """
    Agent yang menulis konten ebook berbasis outline dengan AI.
    Setiap subsection memiliki 5 lapisan wajib.
    Jika API gagal, menggunakan fallback template lokal.
    """
    
    def __init__(self):
        """Inisialisasi WriterAgent."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.outline: Dict[str, Any] = {}
        self.routing_decision: Dict[str, Any] = {}
        self.content: str = ""
        self.words_written: int = 0
        self.foreign_text_detected: bool = False
        
        self.ai_client: Optional[AIClient] = None
        self.api_available: bool = False
        self.fallback_used: bool = False
        self.fallback_reason: str = ""
        self.provider_failed: str = ""
        
        self.secret_manager: Optional[SecretManager] = None
    
    def load_outline(self, outline_file: str = "output/outline.json") -> Dict[str, Any]:
        """Memuat outline dari file."""
        outline_path = Path(outline_file)
        
        try:
            if outline_path.exists():
                with open(outline_path, 'r', encoding='utf-8') as f:
                    outline = json.load(f)
                    logger.info(f"Loaded outline dari {outline_path}")
                    self.outline = outline
                    return outline
            else:
                logger.warning(f"Outline tidak ditemukan: {outline_path}")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing outline: {e}")
            return {}
    
    def load_routing_decision(self, routing_file: str = "output/routing_decision.json") -> Dict[str, Any]:
        """Memuat routing decision untuk tahu provider mana yang dipakai."""
        routing_path = Path(routing_file)
        
        try:
            if routing_path.exists():
                with open(routing_path, 'r', encoding='utf-8') as f:
                    routing = json.load(f)
                    logger.info(f"Loaded routing decision dari {routing_path}")
                    self.routing_decision = routing
                    return routing
            else:
                logger.warning(f"Routing decision tidak ditemukan: {routing_path}")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing routing decision: {e}")
            return {}
    
    def setup_ai_client(self) -> bool:
        """Setup AI client dengan provider yang dipilih router."""
        try:
            self.ai_client = get_ai_client()
            self.secret_manager = get_secret_manager()
            
            routing = self.load_routing_decision()
            
            if routing.get("status") != "success":
                logger.info("Routing status tidak success - akan menggunakan fallback")
                self.api_available = False
                return False
            
            selected_provider_id = routing.get("selected_provider_id")
            
            if not selected_provider_id:
                logger.warning("Tidak ada provider yang dipilih")
                self.api_available = False
                return False
            
            api_key = self.secret_manager.get_api_key(selected_provider_id)
            
            if not api_key:
                logger.warning(f"Provider {selected_provider_id} tidak memiliki API key")
                self.api_available = False
                return False
            
            self.api_available = True
            logger.info(f"AI Client siap dengan provider {selected_provider_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setup AI client: {e}")
            self.api_available = False
            return False
    
    def build_prompt_for_subsection(
        self,
        subtopic_title: str,
        subtopic_number: str,
        chapter_title: str,
        run_context: RunContext
    ) -> str:
        """Membuat prompt internal untuk satu subbab."""
        ebook_title = run_context.ebook_title or "Untitled Ebook"
        target_audience = run_context.target_audience or "General Audience"
        reading_level = run_context.reading_level or "intermediate"
        content_brief = run_context.content_brief or ""
        special_instructions = getattr(run_context, 'special_instructions', "") or ""
        
        prompt = f"""Anda adalah penulis ebook teknis premium berbahasa Indonesia.

Tulis subbab berikut untuk ebook:

Judul Ebook:
{ebook_title}

Target Pembaca:
{target_audience}

Level Pembaca:
{reading_level}

Brief Konten:
{content_brief}

Aturan Khusus:
{special_instructions if special_instructions else "Gunakan Bahasa Indonesia rapi."}

Judul Bab:
{chapter_title}

Judul Subbab:
{subtopic_title}

Nomor Subbab:
{subtopic_number}

Tulis dalam format Markdown berikut:

### {subtopic_number} {subtopic_title}

#### [KONSEP]

Tulis penjelasan konsep dengan bahasa Indonesia yang jelas, praktis, dan mudah dipahami pemula. Jangan terlalu generik. Hubungkan dengan brief ebook.

#### [ANALOGI]

Berikan analogi sederhana dari kehidupan sehari-hari yang relevan dengan topik.

#### [RUMUS]

Jika topik membutuhkan rumus, berikan rumus dan jelaskan arti setiap komponen.

Jika tidak membutuhkan rumus matematika, tulis prinsip kerja dalam format langkah logis.

#### [CONTOH]

Berikan contoh praktis yang spesifik, bukan contoh generik.

Gunakan langkah-langkah yang mudah diikuti.

#### [APLIKASI]

Jelaskan penerapan nyata, manfaat praktis, kesalahan umum, dan tips aman.

Aturan wajib:
- Gunakan Bahasa Indonesia rapi.
- Jangan memakai bahasa Inggris kecuali istilah teknis yang dijelaskan.
- Jangan memakai bahasa asing seperti Mandarin, Rusia, Arab, Jepang, atau simbol asing.
- Jangan menulis lorem ipsum.
- Jangan menulis placeholder.
- Jangan menyebut bahwa Anda adalah AI.
- Jangan menyisipkan API key.
- Jangan membuat instruksi berbahaya.
- Jangan terlalu pendek.
- Setiap lapisan minimal 2 paragraf pendek.
- Output hanya isi subbab dalam Markdown."""

        return prompt
    
    def write_subsection_with_ai(
        self,
        subtopic_title: str,
        subtopic_number: str,
        chapter_title: str,
        run_context: RunContext
    ) -> str:
        """Menulis subbab menggunakan AIClient."""
        if not self.api_available or not self.ai_client:
            logger.info("API tidak tersedia - menggunakan fallback")
            self.fallback_used = True
            self.fallback_reason = "API tidak tersedia atau tidak dikonfigurasi"
            return self.generate_fallback_subsection(subtopic_title, subtopic_number, chapter_title, run_context)
        
        prompt = self.build_prompt_for_subsection(
            subtopic_title,
            subtopic_number,
            chapter_title,
            run_context
        )
        
        routing = self.routing_decision
        sdk_type = routing.get("selected_sdk_type", "openai")
        base_url = routing.get("selected_base_url", "")
        api_key = self.secret_manager.get_api_key(routing.get("selected_provider_id", ""))
        
        provider_config = {
            "sdk_type": sdk_type,
            "base_url": base_url,
            "model_fast": routing.get("selected_model_fast", "gpt-4o-mini"),
            "model_strong": routing.get("selected_model_strong", "gpt-4o")
        }
        
        model_type = "fast"
        
        try:
            logger.info(f"Calling AI untuk subbab: {subtopic_number} {subtopic_title}")
            
            result = self.ai_client.generate_text(
                prompt=prompt,
                provider_config=provider_config,
                api_key=api_key or "",
                model_type=model_type
            )
            
            if result.get("success"):
                text = result.get("text", "")
                logger.info(f"AI response received ({len(text)} chars)")
                return text
            else:
                error = result.get("error", "Unknown error")
                logger.warning(f"AI call failed: {error}")
                self.fallback_used = True
                self.fallback_reason = f"API call failed: {error}"
                self.provider_failed = routing.get("selected_provider_id", "unknown")
                return self.generate_fallback_subsection(subtopic_title, subtopic_number, chapter_title, run_context)
                
        except Exception as e:
            logger.error(f"Error calling AI: {e}")
            self.fallback_used = True
            self.fallback_reason = f"Exception: {str(e)}"
            self.provider_failed = routing.get("selected_provider_id", "unknown")
            return self.generate_fallback_subsection(subtopic_title, subtopic_number, chapter_title, run_context)
    
    def generate_fallback_subsection(
        self,
        subtopic_title: str,
        subtopic_number: str,
        chapter_title: str,
        run_context: RunContext
    ) -> str:
        """Fallback lokal jika API gagal - menggunakan konteks ebook yang spesifik."""
        ebook_title = run_context.ebook_title or "Ebook"
        target_audience = run_context.target_audience or "pembaca"
        content_brief = run_context.content_brief or ""
        
        brief_text = content_brief[:200] + "..." if len(content_brief) > 200 else (content_brief if content_brief else "Pembahasan umum tentang topik ini.")
        
        lines = [
            f"### {subtopic_number} {subtopic_title}",
            "",
            "#### [KONSEP]",
            "",
            f"Dalam bab ini, kita akan membahas secara mendalam tentang **{subtopic_title}** sebagai bagian dari ebook *{ebook_title}*. Konsep ini penting untuk dipahami oleh {target_audience}.",
            "",
            f"Brief ebook ini adalah: {brief_text}",
            "",
            f"Pemahaman tentang {subtopic_title} akan membantu pembaca dalam menerapkan pengetahuan ini secara praktis dalam kehidupan sehari-hari.",
            "",
            "#### [ANALOGI]",
            "",
            f"Bayangkan {subtopic_title} seperti proses belajar bertahap. Pertama kita memahami konsep dasar, kemudian menerapkan secara perlahan, dan akhirnya menjadi terbiasa.",
            "",
            f"Dalam konteks {ebook_title}, {subtopic_title} berfungsi sebagai fondasi untuk pemahaman yang lebih mendalam tentang topik yang dibahas.",
            "",
            "#### [RUMUS]",
            "",
            f"**Prinsip {subtopic_title}:**",
            "",
            "1. Pahami dasar-dasar konsep secara menyeluruh",
            "2. Identifikasi komponen utama yang relevan",
            "3. Terapkan dengan langkah sistematis dan terukur",
            "4. Evaluasi hasil secara berkala dan perbaiki jika perlu",
            "",
            f"Untuk menguasai {subtopic_title}, diperlukan pemahaman bertahap dan praktik konsisten dalam mengaplikasikan konsep.",
            "",
            "#### [CONTOH]",
            "",
            f"**Contoh penerapan {subtopic_title} dalam ebook ini:**",
            "",
            "Langkah 1: Pahami definisi dan ruang lingkup secara jelas dan komprehensif",
            "Langkah 2: Identifikasi contoh nyata dalam konteks pembelajaran yang relevan",
            "Langkah 3: Praktikkan dengan studi kasus sederhana yang mudah diikuti dan dipahami",
            "Langkah 4: Review dan evaluasi pemahaman untuk memastikan hasil yang optimal",
            "",
            f"Contoh ini dirancang khusus untuk {target_audience} yang ingin memahami {subtopic_title} secara praktis dan aplikatif.",
            "",
            "#### [APLIKASI]",
            "",
            f"**Penerapan {subtopic_title} untuk {target_audience}:**",
            "",
            f"1. Dalam pembelajaran: {subtopic_title} membantu memahami konsep secara sistematis dan terstruktur sehingga pengetahuan lebih mudah diserap",
            f"2. Dalam pekerjaan: Aplikasikan untuk meningkatkan hasil kerja dan produktivitas dalam menyelesaikan tugas sehari-hari",
            f"3. Dalam pengembangan diri: Gunakan sebagai fondasi untuk pertumbuhan pengetahuan dan keterampilan secara berkelanjutan",
            "",
            "**Tips Praktis:** Mulailah dari konsep dasar, praktikkan secara bertahap, dan evaluasi secara berkala untuk mencapai hasil terbaik dalam pemahaman topik ini.",
            "",
            "---",
            ""
        ]
        
        return '\n'.join(lines)
    
    def write_header(self, run_context: RunContext) -> str:
        """Menulis header ebook."""
        ebook_title = self.outline.get("ebook_title", run_context.ebook_title or "Untitled Ebook")
        target_audience = run_context.target_audience or "General Audience"
        reading_level = run_context.reading_level or "intermediate"
        timestamp = run_context.timestamp_start
        
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
    
    def write_toc(self) -> str:
        """Menulis daftar isi."""
        chapters = self.outline.get("chapters", [])
        
        lines = [
            "# Daftar Isi",
            ""
        ]
        
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
    
    def write_chapter(self, chapter: Dict[str, Any], run_context: RunContext) -> str:
        """Menulis satu bab lengkap."""
        lines = []
        lines.append(self.write_chapter_header(chapter))
        
        chapter_title = chapter.get("chapter_title", "")
        
        sections = chapter.get("sections", [])
        
        for section in sections:
            subsections = section.get("subsections", [])
            
            for subsection in subsections:
                subtopic_number = subsection.get("subtopic_number", "")
                subtopic_title = subsection.get("subtopic_title", "")
                
                logger.info(f"Writing subsection: {subtopic_number} {subtopic_title}")
                
                content = self.write_subsection_with_ai(
                    subtopic_title,
                    subtopic_number,
                    chapter_title,
                    run_context
                )
                
                lines.append(content)
        
        return ''.join(lines)
    
    def write_closing(self) -> str:
        """Menulis penutup ebook."""
        ebook_title = self.outline.get("ebook_title", "Ebook")
        
        return f"""
---

# Ringkasan

Dalam ebook ini, kita telah membahas konsep-konsep penting dari **{ebook_title}**. Dengan memahami setiap bab dan subbab, pembaca diharapkan dapat:

1. Memahami fondasi teori secara mendalam dan komprehensif
2. Menerapkan pengetahuan dalam praktik secara efektif dan efisien
3. Mengembangkan kemampuan analitis untuk memecahkan masalah
4. Mengaplikasikan dalam konteks nyata untuk hasil yang optimal

---

**Catatan:**
Ebook ini disusun untuk tujuan pembelajaran. Untuk informasi lebih lanjut, silakan konsultasikan dengan ahli di bidang terkait.

---

*Akhir dari dokumen*
"""
    
    def write_ebook(self, run_context: RunContext) -> str:
        """Menulis ebook lengkap."""
        chapters = self.outline.get("chapters", [])
        
        self.setup_ai_client()
        
        lines = []
        
        lines.append(self.write_header(run_context))
        lines.append(self.write_toc())
        
        for chapter in chapters:
            chapter_content = self.write_chapter(chapter, run_context)
            lines.append(chapter_content)
        
        lines.append(self.write_closing())
        
        content = '\n'.join(lines)
        self.content = content
        self.words_written = len(content.split())
        
        logger.info(f"Ebook ditulis: {self.words_written} kata")
        
        return content
    
    def validate_content(self, content: str) -> tuple[bool, List[str]]:
        """Memvalidasi konten."""
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
        
        placeholder_patterns = [r'lorem ipsum', r'placeholder', r'todo', r'fixme', r'\{subtopic']
        for pattern in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(f"Placeholder terdeteksi: {pattern}")
        
        required_layers = ["[KONSEP]", "[ANALOGI]", "[RUMUS]", "[CONTOH]", "[APLIKASI]"]
        for layer in required_layers:
            if layer not in content:
                errors.append(f"Lapisan hilang: {layer}")
        
        return len(errors) == 0, errors
    
    def save_ebook(self, output_file: str = "output/ebook.md") -> None:
        """Menyimpan ebook."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        
        logger.info(f"Ebook disimpan: {output_path} ({self.words_written} kata)")
    
    def save_fallback_info(self) -> None:
        """Menyimpan info fallback ke file."""
        fallback_info = {
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
            "provider_failed": self.provider_failed,
            "api_available": self.api_available,
            "words_written": self.words_written
        }
        
        fallback_path = self.output_dir / "fallback_info.json"
        
        with open(fallback_path, 'w', encoding='utf-8') as f:
            json.dump(fallback_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Fallback info disimpan: {fallback_path}")
    
    def execute(self, run_context: RunContext) -> str:
        """Menjalankan writer agent."""
        logger.info("WriterAgent executing...")
        
        outline = self.load_outline()
        
        if not outline:
            logger.error("Tidak ada outline tersedia")
            return ""
        
        self.load_routing_decision()
        
        content = self.write_ebook(run_context)
        
        is_valid, errors = self.validate_content(content)
        if not is_valid:
            logger.warning(f"Content validation errors: {errors}")
        
        self.save_ebook()
        self.save_fallback_info()
        
        logger.info(f"WriterAgent completed: {self.words_written} kata, fallback={self.fallback_used}")
        
        return content


def run_writer_agent(run_context: RunContext) -> str:
    """Fungsi convenience untuk menjalankan WriterAgent."""
    agent = WriterAgent()
    return agent.execute(run_context)