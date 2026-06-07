"""
DIL Autonomous Ebook Agent - Writer Agent

Menghasilkan konten ebook berbasis outline dengan AI.
Memanggil AIClient untuk menulis setiap subbab.
Cost Guard memeriksa budget sebelum setiap API call.
Fallback template lokal jika API gagal atau budget exceeded.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger
from core.run_context import RunContext
from core.api_client import AIClient, get_ai_client
from core.secret_manager import SecretManager, get_secret_manager
from core.cost_guard import CostGuard

logger = get_logger(__name__)


class WriterAgent:
    """
    Agent yang menulis konten ebook berbasis outline dengan AI.
    Setiap subsection memiliki 5 lapisan wajib.
    Cost Guard memeriksa budget sebelum setiap API call.
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
        self.cost_guard: Optional[CostGuard] = None
        self.cost_denied: bool = False
        self.cost_denied_reason: str = ""
    
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
    
    def setup_cost_guard(self) -> None:
        """Setup CostGuard untuk tracking biaya."""
        try:
            self.cost_guard = CostGuard()
            logger.info("CostGuard initialized for WriterAgent")
        except Exception as e:
            logger.error(f"Error initializing CostGuard: {e}")
            self.cost_guard = None
    
    def setup_ai_client(self) -> bool:
        """Setup AI client dengan provider yang dipilih router."""
        try:
            self.ai_client = get_ai_client()
            self.secret_manager = get_secret_manager()
            
            # Use already-loaded routing decision (loaded in execute())
            routing = self.routing_decision
            
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
        special_instructions = run_context.special_instructions or ""
        
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

Tulis penjelasan konsep dengan bahasa Indonesia yang jelas, praktis, dan mudah dipahami pemula. Hubungkan dengan brief ebook. Minimal 2 paragraf.

#### [ANALOGI]

Berikan analogi sederhana dari kehidupan sehari-hari yang relevan dengan topik. Minimal 2 paragraf.

#### [RUMUS]

Jika topik membutuhkan rumus, berikan rumus dan jelaskan arti setiap komponen. Jika tidak, tulis prinsip kerja dalam langkah logis. Minimal 2 paragraf.

#### [CONTOH]

Berikan contoh praktis yang spesifik. Gunakan langkah-langkah yang mudah diikuti. Minimal 2 paragraf.

#### [APLIKASI]

Jelaskan penerapan nyata, manfaat praktis, kesalahan umum, dan tips aman. Minimal 2 paragraf.

Aturan wajib:
- Gunakan Bahasa Indonesia rapi dan profesional
- Jangan pakai bahasa Inggris kecuali istilah teknis yang sudah dijelaskan
- Jangan pakai bahasa asing (Mandarin, Rusia, Arab, Jepang, dll)
- Jangan tulis lorem ipsum atau placeholder
- Jangan menyebut Anda adalah AI
- Jangan sisipkan API key atau secret
- Jangan buat instruksi berbahaya
- Output hanya isi subbab dalam Markdown"""

        return prompt
    
    def check_cost_before_api_call(self, prompt: str) -> tuple[bool, str]:
        """
        Periksa apakah request boleh dilakukan berdasarkan budget.
        
        Returns:
            Tuple (allowed, reason).
        """
        if not self.cost_guard:
            logger.warning("CostGuard not initialized - skipping cost check")
            return True, "CostGuard not available"
        
        if not self.routing_decision:
            logger.warning("No routing decision - skipping cost check")
            return True, "No routing decision"
        
        provider_id = self.routing_decision.get("selected_provider_id", "unknown")
        model_id = self.routing_decision.get("selected_model_fast", "gpt-4o-mini")
        
        result = self.cost_guard.check_and_register(
            prompt=prompt,
            provider_id=provider_id,
            model_id=model_id,
            agent_name="writer_agent"
        )
        
        if not result.get("allowed"):
            reason = result.get("reason", "Cost limit exceeded")
            logger.warning(f"Cost guard denied API call: {reason}")
            self.cost_denied = True
            self.cost_denied_reason = reason
            return False, reason
        
        return True, "OK"
    
    def write_subsection_with_ai(
        self,
        subtopic_title: str,
        subtopic_number: str,
        chapter_title: str,
        run_context: RunContext
    ) -> str:
        """Menulis subbab menggunakan AIClient dengan cost guard."""
        if not self.api_available or not self.ai_client:
            logger.info("API tidak tersedia - menggunakan fallback")
            self.fallback_used = True
            self.fallback_reason = "API tidak tersedia atau tidak dikonfigurasi"
            return self.generate_fallback_subsection(subtopic_title, subtopic_number, chapter_title, run_context)
        
        # Bangun prompt
        prompt = self.build_prompt_for_subsection(
            subtopic_title,
            subtopic_number,
            chapter_title,
            run_context
        )
        
        # COST GUARD CHECK - sebelum API call
        allowed, reason = self.check_cost_before_api_call(prompt)
        
        if not allowed:
            logger.warning(f"Cost guard denied: {reason}")
            self.fallback_used = True
            self.fallback_reason = f"Cost guard denied request: {reason}"
            self.cost_denied = True
            self.cost_denied_reason = reason
            return self.generate_fallback_subsection(subtopic_title, subtopic_number, chapter_title, run_context)
        
        # Bangun provider config
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
    
    def _detect_domain_from_brief(self, brief: str) -> str:
        """Deteksi domain dari brief konten untuk menyesuaikan fallback."""
        brief_lower = brief.lower()
        electrical_keywords = [
            "tegangan", "arus", "hambatan", "daya", "energi", "listrik",
            "elektronika", "rangkaian", "ohm", "ampere", "watt", "joule",
            "resistor", "kapasitor", "induktor", "dioda", "transistor"
        ]
        for kw in electrical_keywords:
            if kw in brief_lower:
                return "electrical"
        return "general"

    def _build_domain_specific_examples(self, domain: str, subtopic_title: str) -> str:
        """Bangun contoh spesifik berdasarkan domain."""
        if domain == "electrical":
            return (
                f"Misalkan sebuah rangkaian sederhana memiliki tegangan sumber 12 V dan "
                f"hambatan total 4 ohm. Dengan menggunakan Hukum Ohm, arus yang mengalir "
                f"adalah 3 A. Daya yang diserap oleh rangkaian dapat dihitung sebagai 12 V x 3 A = 36 W. "
                f"Jika rangkaian dihidupkan selama 5 detik, energi yang dikonversi adalah 36 W x 5 s = 180 J. "
                f"Perhitungan sederhana ini menunjukkan hubungan langsung antara tegangan, arus, hambatan, daya, dan energi."
            )
        return (
            f"Misalkan sebuah proyek memerlukan penerapan {subtopic_title} dalam tiga tahap: "
            f"persiapan, eksekusi, dan evaluasi. Pada tahap persiapan, kumpulkan semua komponen dan data yang diperlukan. "
            f"Pada tahap eksekusi, jalankan langkah demi langkah sesuai urutan logika. "
            f"Pada tahap evaluasi, bandingkan hasil dengan target awal dan catankan penyimpangan."
        )

    def _build_safety_note(self, domain: str, subtopic_title: str) -> str:
        """Bangun catatan aman berdasarkan domain."""
        if domain == "electrical":
            return (
                f"**Catatan Keamanan:** Saat bekerja dengan rangkaian listrik, pastikan sumber tegangan "
                f"dimatikan sebelum menyambung atau memodifikasi komponen. Gunakan multimeter yang tepat untuk "
                f"mengukur tegangan dan arus sesuai rentang pengukuran. Jangan menyentuh konduktor bertegangan "
                f"tanpa pelindung yang memadai. Kesalahan umum adalah mengabaikan rating daya komponen, "
                f"yang dapat menyebabkan panas berlebih atau kerusakan permanen."
            )
        return (
            f"**Catatan:** Terapkan {subtopic_title} dengan memperhatikan konteks dan batasan. "
            f"Evaluasi risiko sebelum eksekusi. Jika ada keraguan, konsultasikan dengan referensi tepercaya."
        )

    def generate_fallback_subsection(
        self,
        subtopic_title: str,
        subtopic_number: str,
        chapter_title: str,
        run_context: RunContext
    ) -> str:
        """
        Fallback lokal jika API gagal - menggunakan konteks ebook yang spesifik dan domain-aware.
        Menghasilkan konten dengan 5 lapisan wajib: [KONSEP], [ANALOGI], [RUMUS], [CONTOH], [APLIKASI].
        """
        ebook_title = run_context.ebook_title or "Ebook"
        target_audience = run_context.target_audience or "pembaca"
        content_brief = run_context.content_brief or ""
        mode = run_context.mode if hasattr(run_context, "mode") else "session"

        domain = self._detect_domain_from_brief(content_brief)
        brief_snippet = content_brief[:300] if content_brief else "Pembahasan teknis tentang topik ini."
        example_text = self._build_domain_specific_examples(domain, subtopic_title)
        safety_note = self._build_safety_note(domain, subtopic_title)

        # Target panjang: 700-1000 kata untuk session, 350-600 untuk test
        min_words = 350 if mode == "test" else 700

        # Domain-specific terminology
        if domain == "electrical":
            concept_para = (
                f"**{subtopic_title}** adalah konsep fundamental dalam dunia kelistrikan dan elektronika. "
                f"Dalam konteks ebook *{ebook_title}*, pemahaman ini menjadi fondasi bagi {target_audience} "
                f"untuk menganalisis, merancang, dan memelihara rangkaian listrik dengan aman. "
                f"Brief yang diberikan menyoroti: {brief_snippet}. "
                f"Setiap komponen dalam sistem listrik saling berkaitan melalui besaran dasar: tegangan (volt), arus (ampere), hambatan (ohm), daya (watt), dan energi (joule). "
                f"Tanpa memahami besaran-besaran ini secara terintegrasi, sulit untuk menyelesaikan masalah praktis di lapangan."
            )
            analogy_para = (
                f"Analogi yang paling tepat untuk memahami {subtopic_title} adalah sistem perpipaan air. "
                f"Tegangan listrik analog dengan tekanan air dalam pipa: semakin tinggi tekanan, semakin besar dorongan untuk mengalirkan air. "
                f"Arus listrik analog dengan laju aliran air: banyaknya air yang mengalir per satuan waktu. "
                f"Hambatan listrik analog dengan hambatan pipa: pipa yang sempit atau kasus menyebabkan aliran air melambat. "
                f"Daya listrik analog dengan daya hidrolik: tekanan kali laju aliran. Energi listrik analog dengan volume total air yang dipindahkan. "
                f"Analogi ini membantu memvisualisasikan hubungan matematis yang abstrak menjadi gambaran nyata di kehidupan sehari-hari."
            )
            rumus_para = (
                f"**Prinsip dan Rumus Utama:**\n\n"
                f"1. **Hukum Ohm**: Hubungan antara tegangan (V), arus (I), dan hambatan (R):\n\n"
                f"   V = I × R\n\n"
                f"   Artinya, tegangan yang diperlukan untuk mendorong arus tertentu sebanding dengan hambatan rangkaian. "
                f"Jika hambatan naik dan arus tetap, tegangan harus naik.\n\n"
                f"2. **Daya Listrik (P)**: Daya adalah laju transfer energi, dihitung sebagai:\n\n"
                f"   P = V × I\n\n"
                f"   Dengan substitusi Hukum Ohm, daya juga dapat dinyatakan sebagai P = I² × R atau P = V² / R. "
                f"Pemilihan rumus bergantung pada besaran yang diketahui dalam soal.\n\n"
                f"3. **Energi Listrik (W)**: Energi adalah daya dikalikan waktu:\n\n"
                f"   W = P × t\n\n"
                f"   Satuan energi dalam joule (J) atau kilowatt-jam (kWh) untuk aplikasi rumah tangga."
            )
            contoh_para = (
                f"**Contoh Praktis:**\n\n{example_text}\n\n"
                f"Langkah-langkah penyelesaian masalah:\n\n"
                f"1. Identifikasi besaran yang diketahui: tegangan, arus, hambatan, atau daya.\n"
                f"2. Pilih rumus yang sesuai berdasarkan besaran yang dicari.\n"
                f"3. Substitusikan nilai dengan satuan yang konsisten (V, A, ohm, W, s).\n"
                f"4. Hitung dan verifikasi hasil dengan perbandingan orde magnitudo.\n"
                f"5. Catat satuan akhir untuk menghindari kesalahan interpretasi."
            )
            aplikasi_para = (
                f"**Aplikasi Nyata:**\n\n"
                f"1. **Perancangan Sumber Daya**: Menentukan kapasitas trafo, catu daya, atau baterai yang diperlukan untuk beban tertentu.\n"
                f"2. **Pemilihan Komponen**: Memastikan resistor, kabel, dan perangkat semikonduktor memiliki rating daya dan arus yang memadai.\n"
                f"3. **Efisiensi Energi**: Menghitung rugi-rugi daya pada saluran transmisi sehingga dapat dioptimalkan dengan penaikan tegangan atau pengurangan hambatan.\n"
                f"4. **Kesalahan Umum**: Mengukur arus dengan multimeter dalam mode tegangan (akan merusak fuse), "
                f"mengabaikan rugi panas pada resistor berdaya kecil, atau menyambung beban ke sumber tanpa memperhitungkan hambatan sumber.\n\n{safety_note}"
            )
        else:
            concept_para = (
                f"**{subtopic_title}** merupakan konsep inti dalam ebook *{ebook_title}*. "
                f"Pembahasan ini dirancang agar {target_audience} dapat memahami prinsip dasar, mengenali konteks penggunaan, "
                f"dan menerapkan pengetahuan secara bertahap. Brief yang menjadi acuan: {brief_snippet}. "
                f"Pemahaman yang kokoh terhadap {subtopic_title} akan mempercepat pembelajaran bab-bab selanjutnya "
                f"karena banyak subbab lain membangun fondasi dari konsep ini."
            )
            analogy_para = (
                f"Analogi yang relevan: bayangkan {subtopic_title} seperti fondasi bangunan. "
                f"Fondasi yang kokoh memungkinkan struktur atas dibangun dengan aman dan stabil. "
                f"Jika fondasi goyah, seluruh bangunan rentan terhadap beban. "
                f"Dalam konteks {ebook_title}, memahami {subtopic_title} dengan baik memastikan pembaca tidak keliru "
                f"saat menemukan variasi atau pengecualian di bab-bab lanjutan."
            )
            rumus_para = (
                f"**Prinsip Kerja dan Kerangka Berpikir:**\n\n"
                f"1. Identifikasi variabel masukan yang relevan dengan {subtopic_title}.\n"
                f"2. Tentukan relasi atau pola antara variabel-variabel tersebut.\n"
                f"3. Terapkan prinsip secara sistematis pada setiap studi kasus.\n"
                f"4. Evaluasi hasil dengan membandingkan terhadap baseline atau referensi tepercaya.\n\n"
                f"Pendekatan ini menjamin konsistensi dan mengurangi risiko kesalahan interpretasi."
            )
            contoh_para = (
                f"**Contoh Praktis:**\n\n{example_text}\n\n"
                f"Setiap contoh di atas menekankan pada tindakan konkret, bukan deskripsi abstrak. "
                f"Pembaca disarankan untuk mencoba meniru langkah-langkah tersebut pada proyek atau latihan pribadi."
            )
            aplikasi_para = (
                f"**Aplikasi Nyata:**\n\n"
                f"1. **Pembelajaran**: Gunakan {subtopic_title} sebagai fondasi untuk memahami materi tingkat lanjut.\n"
                f"2. **Pekerjaan**: Terapkan dalam proyek nyata dengan mengadaptasi langkah sesuai konteks organisasi.\n"
                f"3. **Pengembangan Diri**: Evaluasi hasil penerapan secara berkala untuk menemukan celah perbaikan.\n"
                f"4. **Kesalahan Umum**: Mengabaikan konteks, menggunakan asumsi tanpa validasi, atau melompat ke solusi sebelum memahami masalah.\n\n{safety_note}"
            )

        lines = [
            f"### {subtopic_number} {subtopic_title}",
            "",
            "#### [KONSEP]",
            "",
            concept_para,
            "",
            "#### [ANALOGI]",
            "",
            analogy_para,
            "",
            "#### [RUMUS]",
            "",
            rumus_para,
            "",
            "#### [CONTOH]",
            "",
            contoh_para,
            "",
            "#### [APLIKASI]",
            "",
            aplikasi_para,
            "",
            "---",
            ""
        ]

        text = '\n\n'.join(lines)
        word_count = len(text.split())

        # Jika terlalu pendek, tambahkan paragraf pengayaan agar memenuhi target
        if word_count < min_words:
            extra_needed = min_words - word_count
            extra_lines = [
                "",
                "#### [PENGUATAN]",
                "",
                f"Penguatan tambahan untuk memastikan pemahaman {subtopic_title} mencukupi: "
                f"ulangi langkah analisis dengan menggunakan data berbeda, gambarkan diagram hubungan antar variabel, "
                f"dan diskusikan dengan rekan atau mentor untuk mendapatkan perspektif tambahan. "
                f"Praktik konsisten akan membentuk kebiasaan berpikir sistematis yang diperlukan dalam menyelesaikan masalah kompleks."
            ]
            text = text + '\n\n'.join(extra_lines)

        return text
    
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
        
        # Setup AI client dan Cost Guard
        self.setup_ai_client()
        self.setup_cost_guard()
        
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
        """Menyimpan info fallback dan cost ke file."""
        fallback_info = {
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
            "provider_failed": self.provider_failed,
            "api_available": self.api_available,
            "words_written": self.words_written,
            "cost_denied": self.cost_denied,
            "cost_denied_reason": self.cost_denied_reason
        }
        
        fallback_path = self.output_dir / "fallback_info.json"
        
        with open(fallback_path, 'w', encoding='utf-8') as f:
            json.dump(fallback_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Fallback info disimpan: {fallback_path}")
    
    def save_cost_report(self) -> None:
        """Menyimpan cost report dari WriterAgent."""
        if not self.cost_guard:
            return
        
        cost_report = self.cost_guard.get_report()
        cost_path = self.output_dir / "writer_cost_report.json"
        
        with open(cost_path, 'w', encoding='utf-8') as f:
            json.dump(cost_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Writer cost report disimpan: {cost_path}")
    
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
        self.save_cost_report()
        
        logger.info(f"WriterAgent completed: {self.words_written} kata, fallback={self.fallback_used}")
        
        return content


def run_writer_agent(run_context: RunContext) -> str:
    """Fungsi convenience untuk menjalankan WriterAgent."""
    agent = WriterAgent()
    return agent.execute(run_context)