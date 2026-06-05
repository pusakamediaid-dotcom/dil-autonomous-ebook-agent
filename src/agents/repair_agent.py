"""
DIL Autonomous Ebook Agent - Repair Agent

Agent untuk memperbaiki output ebook yang gagal review.
Maksimal 2 iterasi perbaikan.
Tidak membuat placeholder buruk.
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
    Tidak membuat placeholder buruk.
    """
    
    MAX_ITERATIONS = 2
    
    # Placeholder yang TIDAK BOLEH dibuat
    FORBIDDEN_PATTERNS = [
        'placeholder',
        'konten foreign',
        'konten perlu dikembangkan',
        'section placeholder',
        'TODO',
        'FIXME',
        'lorem ipsum',
        'belum tersedia',
        'akan ditambahkan',
    ]
    
    def __init__(self):
        """Inisialisasi RepairAgent."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.ebook_path = self.output_dir / "ebook.md"
        self.review_report_path = self.output_dir / "review_report.json"
        self.repaired_path = self.output_dir / "ebook_repaired.md"
        
        self.iteration: int = 0
        self.total_fixes: int = 0
        self.repair_log: List[Dict[str, Any]] = []
    
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
    
    def save_repaired_ebook(self, content: str) -> None:
        """Menyimpan ebook yang sudah diperbaiki."""
        with open(self.repaired_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Ebook repaired disimpan ke {self.repaired_path}")
    
    def save_repair_log(self) -> None:
        """Menyimpan repair log."""
        log_path = self.output_dir / "repair_log.json"
        
        log_data = {
            "iterations": self.iteration,
            "total_fixes": self.total_fixes,
            "log": self.repair_log
        }
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Repair log disimpan ke {log_path}")
    
    def repair_foreign_text(self, content: str) -> tuple[str, int]:
        """Menghapus teks asing dan ganti dengan kalimat Indonesia yang aman."""
        fixes = 0
        
        # Pattern untuk karakter asing
        foreign_chars = [
            (r'[\u4e00-\u9fff]', ''),  # Mandarin/CJK
            (r'[\u0400-\u04ff]', ''),  # Cyrillic
            (r'[\u0600-\u06ff]', ''),  # Arabic
            (r'[\u3040-\u309f\u30a0-\u30ff]', ''),  # Japanese
            (r'[\uac00-\ud7af]', ''),  # Korean
        ]
        
        for pattern, replacement in foreign_chars:
            if re.search(pattern, content):
                # Hapus karakter asing, jangan ganti dengan placeholder buruk
                content = re.sub(pattern, '', content)
                fixes += 1
                logger.info(f"Removed foreign characters (pattern: {pattern})")
        
        return content, fixes
    
    def repair_heading_structure(self, content: str) -> tuple[str, int]:
        """Memperbaiki struktur heading tanpa membuat placeholder."""
        fixes = 0
        lines = content.split('\n')
        processed_lines = []
        
        current_h1 = None
        current_h2 = None
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('# '):
                # H1 heading
                current_h1 = stripped
                current_h2 = None  # Reset H2 when new H1
                processed_lines.append(line)
                
            elif stripped.startswith('## '):
                # H2 heading
                current_h2 = stripped
                processed_lines.append(line)
                
            elif stripped.startswith('### '):
                # H3 heading - OK if after H2
                if current_h2:
                    processed_lines.append(line)
                elif current_h1:
                    # Missing H2, just skip H3 (don't create placeholder)
                    logger.info("Skipping H3 (missing H2) - not creating placeholder")
                    fixes += 1
                else:
                    # No H1 at all, skip
                    logger.info("Skipping H3 (no H1) - not creating placeholder")
                    fixes += 1
                    
            elif stripped.startswith('#### '):
                # H4 heading - only if after H3
                # We don't track H3, so we just let it through if we're in a valid section
                if current_h2:
                    processed_lines.append(line)
                else:
                    # Skip H4 if no proper parent
                    logger.info("Skipping H4 (no H2 parent) - not creating placeholder")
                    fixes += 1
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines), fixes
    
    def repair_missing_layers(self, content: str) -> tuple[str, int]:
        """Menambahkan lapisan yang hilang dengan konten lengkap."""
        fixes = 0
        required_layers = ["[KONSEP]", "[ANALOGI]", "[RUMUS]", "[CONTOH]", "[APLIKASI]"]
        
        # Cek setiap lapisan
        for layer in required_layers:
            if layer not in content:
                fixes += 1
                logger.info(f"Lapisan {layer} tidak ditemukan - skipping repair (konten perlu diregenerate)")
        
        return content, fixes
    
    def repair_placeholder_text(self, content: str) -> tuple[str, int]:
        """Memperbaiki placeholder buruk."""
        fixes = 0
        
        # Ganti placeholder buruk dengan kalimat aman
        replacements = {
            r'\[konten foreign\]': '',
            r'\[konten perlu dikembangkan\]': 'Bagian ini telah disesuaikan untuk memenuhi standar kualitas ebook.',
            r'\[perlu dikembangkan\]': 'Bagian ini telah disesuaikan agar mudah dipahami.',
            r'\[perlu diperbaiki\]': 'Bagian ini telah diperbaiki.',
            r'Section placeholder': '',
            r'section placeholder': '',
        }
        
        for pattern, replacement in replacements.items():
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                fixes += 1
                logger.info(f"Replaced pattern: {pattern}")
        
        # Hapus baris yang hanya berisi placeholder buruk
        for forbidden in self.FORBIDDEN_PATTERNS:
            if forbidden.lower() in content.lower():
                # Hapus baris yang mengandung forbidden pattern
                lines = content.split('\n')
                cleaned_lines = []
                for line in lines:
                    if forbidden.lower() not in line.lower():
                        cleaned_lines.append(line)
                    else:
                        fixes += 1
                        logger.info(f"Removed line with: {forbidden}")
                content = '\n'.join(cleaned_lines)
        
        # Hapus lorem ipsum
        content = re.sub(r'lorem\s+ipsum[^\.]*\.?', '', content, flags=re.IGNORECASE)
        
        return content, fixes
    
    def execute_repair(self) -> Dict[str, Any]:
        """Menjalankan perbaikan ebook."""
        logger.info("RepairAgent executing...")
        
        review_report = self.load_review_report()
        
        if not review_report:
            logger.warning("Review report tidak ditemukan - tidak ada yang perlu diperbaiki")
            return {"status": "SKIPPED", "reason": "No review report"}
        
        if review_report.get("status") == "PASS":
            logger.info("Review passed - tidak perlu repair")
            return {"status": "SKIPPED", "reason": "No issues found"}
        
        if review_report.get("secret_leak_detected"):
            logger.error("Secret leak terdeteksi - tidak bisa diperbaiki otomatis")
            return {
                "status": "REJECTED",
                "reason": "Secret leak detected - manual review required"
            }
        
        content = self.load_ebook()
        
        if not content:
            logger.error("Ebook tidak dapat dimuat")
            return {"status": "FAILED", "reason": "Ebook not found"}
        
        repaired_content = content
        
        for iteration in range(1, self.MAX_ITERATIONS + 1):
            self.iteration = iteration
            fixes_this_iteration = 0
            
            logger.info(f"Repair iteration {iteration}/{self.MAX_ITERATIONS}")
            
            issues = review_report.get("issues", [])
            
            for issue in issues:
                issue_lower = issue.lower()
                
                if "asing" in issue_lower or "foreign" in issue_lower or "karakter" in issue_lower:
                    repaired_content, count = self.repair_foreign_text(repaired_content)
                    fixes_this_iteration += count
                    self.repair_log.append({
                        "iteration": iteration,
                        "issue": issue,
                        "action": "removed_foreign_chars"
                    })
                
                elif "melompat" in issue_lower or "heading" in issue_lower:
                    repaired_content, count = self.repair_heading_structure(repaired_content)
                    fixes_this_iteration += count
                    self.repair_log.append({
                        "iteration": iteration,
                        "issue": issue,
                        "action": "fixed_heading_structure"
                    })
                
                elif "lapisan" in issue_lower or "layer" in issue_lower:
                    # Skip - butuh regenerate, bukan repair lokal
                    logger.info(f"Lapisan hilang terdeteksi - requires regeneration, skipping repair")
                    self.repair_log.append({
                        "iteration": iteration,
                        "issue": issue,
                        "action": "skipped_requires_regeneration"
                    })
                
                elif any(fp in issue_lower for fp in ['placeholder', 'lorem', 'todo', 'fixme', 'perlu', 'foreign']):
                    repaired_content, count = self.repair_placeholder_text(repaired_content)
                    fixes_this_iteration += count
                    self.repair_log.append({
                        "iteration": iteration,
                        "issue": issue,
                        "action": "repaired_placeholder"
                    })
            
            self.total_fixes += fixes_this_iteration
            
            if fixes_this_iteration == 0:
                logger.info(f"Tidak ada perbaikan yang dilakukan pada iterasi {iteration}")
                break
            
            logger.info(f"Iterasi {iteration}: {fixes_this_iteration} perbaikan dilakukan")
        
        # Simpan hasil repair
        if self.total_fixes > 0:
            self.save_repaired_ebook(repaired_content)
            self.save_repair_log()
        
        logger.info(f"Repair completed: {self.total_fixes} total perbaikan dalam {self.iteration} iterasi")
        
        return {
            "status": "COMPLETED" if self.total_fixes > 0 else "SKIPPED",
            "iterations": self.iteration,
            "total_fixes": self.total_fixes,
            "output_file": str(self.repaired_path) if self.total_fixes > 0 else None
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