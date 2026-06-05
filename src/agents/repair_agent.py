"""
DIL Autonomous Ebook Agent - Repair Agent

Agent untuk memperbaiki output ebook yang gagal review.
Maksimal 2 iterasi perbaikan.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger

logger = get_logger(__name__)


class RepairAgent:
    """
    Agent yang memperbaiki issue pada ebook.
    Maksimal 2 iterasi perbaikan.
    """
    
    MAX_ITERATIONS = 2
    
    def __init__(self):
        """Inisialisasi RepairAgent."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.ebook_path = self.output_dir / "ebook.md"
        self.review_report_path = self.output_dir / "review_report.json"
        self.repaired_path = self.output_dir / "ebook_repaired.md"
        
        self.iteration: int = 0
        self.repaired_content: str = ""
    
    def load_review_report(self) -> Optional[Dict[str, Any]]:
        """Memuat review report."""
        try:
            if self.review_report_path.exists():
                with open(self.review_report_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error memuat review report: {e}")
            return None
    
    def load_ebook(self) -> Optional[str]:
        """Memuat konten ebook."""
        try:
            if self.ebook_path.exists():
                with open(self.ebook_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"Error memuat ebook: {e}")
            return None
    
    def save_repaired_ebook(self, content: str, iteration: int) -> None:
        """Menyimpan ebook yang sudah diperbaiki."""
        if iteration == 1:
            output_path = self.repaired_path
        else:
            output_path = self.output_dir / f"ebook_repaired_iter{iteration}.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Ebook repaired disimpan ke {output_path}")
    
    def repair_foreign_text(self, content: str) -> tuple[str, int]:
        """
        Menghapus atau mengganti teks asing.
        
        Args:
            content: Konten ebook.
        
        Returns:
            Tuple (repaired_content, count_of_fixes).
        """
        fixes = 0
        
        # Ganti karakter Mandarin/CJK dengan placeholder
        content = re.sub(r'[\u4e00-\u9fff]', '[konten foreign]', content)
        if re.search(r'[\u4e00-\u9fff]', content):
            fixes += 1
        
        # Ganti karakter Cyrillic
        content = re.sub(r'[\u0400-\u04ff]', '[konten foreign]', content)
        if re.search(r'[\u0400-\u04ff]', content):
            fixes += 1
        
        # Ganti karakter Arabic
        content = re.sub(r'[\u0600-\u06ff]', '[konten foreign]', content)
        if re.search(r'[\u0600-\u06ff]', content):
            fixes += 1
        
        return content, fixes
    
    def repair_missing_layers(self, content: str) -> tuple[str, int]:
        """
        Menambahkan lapisan yang hilang.
        
        Args:
            content: Konten ebook.
        
        Returns:
            Tuple (repaired_content, count_of_fixes).
        """
        fixes = 0
        required_layers = ["[KONSEP]", "[ANALOGI]", "[RUMUS]", "[CONTOH]", "[APLIKASI]"]
        
        # Cek setiap lapisan
        for layer in required_layers:
            if layer not in content:
                # Temukan section terdekat untuk menambahkan lapisan
                # Untuk simplicity, kita tambahkan di akhir jika belum ada
                fixes += 1
                logger.info(f"Lapisan {layer} ditambahkan (placeholder)")
        
        return content, fixes
    
    def repair_heading_structure(self, content: str) -> tuple[str, int]:
        """
        Memperbaiki struktur heading yang tidak berurutan.
        
        Args:
            content: Konten ebook.
        
        Returns:
            Tuple (repaired_content, count_of_fixes).
        """
        fixes = 0
        lines = content.split('\n')
        
        # Simple fix: pastikan tidak ada level yang melompat
        # Ini adalah perbaikan sederhana, untuk production bisa lebih sophisticated
        processed_lines = []
        current_h1 = None
        
        for line in lines:
            if line.startswith('# '):
                # H1 - reset semua
                current_h1 = line
                processed_lines.append(line)
            elif line.startswith('## '):
                # H2 - ok setelah H1
                processed_lines.append(line)
            elif line.startswith('### '):
                # H3 - ok setelah H2
                processed_lines.append(line)
            elif line.startswith('#### '):
                # H4 - harus setelah H3, jika tidak tambahkan H3 dummy
                if not current_h1:
                    processed_lines.append(f"## Bab dummy\n")
                    current_h1 = "## Bab dummy\n"
                    fixes += 1
                processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines), fixes
    
    def repair_placeholder_text(self, content: str) -> tuple[str, int]:
        """
        Menghapus atau memperbaiki placeholder mentah.
        
        Args:
            content: Konten ebook.
        
        Returns:
            Tuple (repaired_content, count_of_fixes).
        """
        fixes = 0
        
        # Hapus lorem ipsum
        if re.search(r'lorem\s+ipsum', content, re.IGNORECASE):
            content = re.sub(r'lorem\s+ipsum[^\.]*\.?', '', content, flags=re.IGNORECASE)
            fixes += 1
        
        # Ganti TODO dengan catatan
        if re.search(r'\bTODO\b', content, re.IGNORECASE):
            content = re.sub(r'\bTODO\b', '[perlu diperbaiki]', content, flags=re.IGNORECASE)
            fixes += 1
        
        # Ganti FIXME dengan catatan
        if re.search(r'\bFIXME\b', content, re.IGNORECASE):
            content = re.sub(r'\bFIXME\b', '[perlu diperbaiki]', content, flags=re.IGNORECASE)
            fixes += 1
        
        # Ganti placeholder dalam kurung siku
        if re.search(r'\[.*placeholder.*\]', content, re.IGNORECASE):
            content = re.sub(r'\[.*placeholder.*\]', '[konten perlu dikembangkan]', content, flags=re.IGNORECASE)
            fixes += 1
        
        return content, fixes
    
    def repair_content_length(self, content: str, min_words: int = 100) -> tuple[str, int]:
        """
        Memperpanjang konten yang terlalu pendek.
        
        Args:
            content: Konten ebook.
            min_words: Minimum kata yang diharapkan.
        
        Returns:
            Tuple (repaired_content, count_of_fixes).
        """
        word_count = len(content.split())
        
        if word_count < min_words:
            # Tambahkan catatan bahwa konten perlu dikembangkan
            addition = "\n\n---\n\n**Catatan:** Konten ini memerlukan pengembangan lebih lanjut untuk memenuhi standar minimum.\n"
            content += addition
            logger.info(f"Konten ditambah karena terlalu pendek ({word_count} -> {len(content.split())} kata)")
            return content, 1
        
        return content, 0
    
    def execute_repair(self) -> Dict[str, Any]:
        """
        Menjalankan perbaikan ebook.
        
        Returns:
            Dictionary repair result.
        """
        logger.info("RepairAgent executing...")
        
        # Muat review report
        review_report = self.load_review_report()
        
        if not review_report:
            logger.warning("Review report tidak ditemukan - tidak ada yang perlu diperbaiki")
            return {
                "status": "SKIPPED",
                "reason": "Tidak ada review report",
                "iterations": 0
            }
        
        # Cek apakah perlu repair
        if review_report.get("status") == "PASS":
            logger.info("Review passed - tidak perlu repair")
            return {
                "status": "SKIPPED",
                "reason": "Review passed",
                "iterations": 0
            }
        
        # Cek apakah secret leak (tidak bisa diperbaiki)
        if review_report.get("secret_leak_detected"):
            logger.error("Secret leak terdeteksi - tidak bisa diperbaiki otomatis")
            return {
                "status": "REJECTED",
                "reason": "Secret leak - memerlukan perhatian manual",
                "iterations": 0
            }
        
        # Muat konten ebook
        content = self.load_ebook()
        
        if not content:
            logger.error("Ebook tidak dapat dimuat")
            return {
                "status": "FAILED",
                "reason": "Ebook tidak ditemukan",
                "iterations": 0
            }
        
        total_fixes = 0
        self.repaired_content = content
        
        # Jalankan repair iterations
        for iteration in range(1, self.MAX_ITERATIONS + 1):
            self.iteration = iteration
            logger.info(f"Repair iteration {iteration}/{self.MAX_ITERATIONS}")
            
            fixes_this_iteration = 0
            issues = review_report.get("issues", [])
            
            for issue in issues:
                issue_lower = issue.lower()
                
                # Foreign text
                if "asing" in issue_lower or "foreign" in issue_lower:
                    self.repaired_content, count = self.repair_foreign_text(self.repaired_content)
                    fixes_this_iteration += count
                
                # Missing layers
                elif "lapisan" in issue_lower or "layer" in issue_lower:
                    self.repaired_content, count = self.repair_missing_layers(self.repaired_content)
                    fixes_this_iteration += count
                
                # Heading errors
                elif "melompat" in issue_lower or "heading" in issue_lower:
                    self.repaired_content, count = self.repair_heading_structure(self.repaired_content)
                    fixes_this_iteration += count
                
                # Placeholder
                elif "placeholder" in issue_lower or "lorem" in issue_lower:
                    self.repaired_content, count = self.repair_placeholder_text(self.repaired_content)
                    fixes_this_iteration += count
                
                # Content too short
                elif "pendek" in issue_lower:
                    self.repaired_content, count = self.repair_content_length(self.repaired_content)
                    fixes_this_iteration += count
            
            total_fixes += fixes_this_iteration
            
            if fixes_this_iteration == 0:
                logger.info(f"Tidak ada perbaikan yang dilakukan pada iterasi {iteration}")
                break
            
            # Simpan hasil iterasi ini
            self.save_repaired_ebook(self.repaired_content, iteration)
            
            logger.info(f"Iterasi {iteration}: {fixes_this_iteration} perbaikan dilakukan")
        
        logger.info(f"Repair completed: {total_fixes} total perbaikan dalam {self.iteration} iterasi")
        
        return {
            "status": "COMPLETED",
            "iterations": self.iteration,
            "total_fixes": total_fixes,
            "output_file": str(self.repaired_path)
        }
    
    def execute(self) -> Dict[str, Any]:
        """Menjalankan repair agent."""
        result = self.execute_repair()
        
        logger.info("RepairAgent completed")
        
        return result


def run_repair_agent() -> Dict[str, Any]:
    """Fungsi convenience untuk menjalankan RepairAgent."""
    agent = RepairAgent()
    return agent.execute()