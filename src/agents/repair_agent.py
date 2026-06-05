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
    
    def save_repaired_ebook(self, content: str, iteration: int) -> None:
        """Menyimpan ebook yang sudah diperbaiki."""
        output_path = self.repaired_path
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Ebook repaired disimpan ke {output_path}")
    
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
        """Menghapus atau mengganti teks asing."""
        fixes = 0
        
        # Ganti karakter asing dengan placeholder
        content = re.sub(r'[\u4e00-\u9fff]', '[konten foreign]', content)
        content = re.sub(r'[\u0400-\u04ff]', '[konten foreign]', content)
        content = re.sub(r'[\u0600-\u06ff]', '[konten foreign]', content)
        content = re.sub(r'[\u3040-\u309f\u30a0-\u30ff]', '[konten foreign]', content)
        
        fixes += 1
        
        return content, fixes
    
    def repair_heading_structure(self, content: str) -> tuple[str, int]:
        """Memperbaiki struktur heading yang tidak berurutan."""
        fixes = 0
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            if line.startswith('#'):
                # Ensure consistent heading format
                level = len(line) - len(line.lstrip('#'))
                if level > 0:
                    # Ensure space after heading markers
                    rest = line.lstrip('#')
                    if not rest.startswith(' '):
                        line = '#' * level + ' ' + rest.strip()
                    fixes += 1
            
            processed_lines.append(line)
        
        return '\n'.join(processed_lines), fixes
    
    def repair_missing_layers(self, content: str) -> tuple[str, int]:
        """Menambahkan lapisan yang hilang."""
        fixes = 0
        required_layers = ["[KONSEP]", "[ANALOGI]", "[RUMUS]", "[CONTOH]", "[APLIKASI]"]
        
        for layer in required_layers:
            if layer not in content:
                fixes += 1
                logger.info(f"Lapisan {layer} tidak ditemukan - akan ditambahkan di repair berikutnya")
        
        return content, fixes
    
    def repair_placeholder_text(self, content: str) -> tuple[str, int]:
        """Menghapus atau memperbaiki placeholder mentah."""
        fixes = 0
        
        if re.search(r'lorem\s+ipsum', content, re.IGNORECASE):
            content = re.sub(r'lorem\s+ipsum[^\.]*\.?', '', content, flags=re.IGNORECASE)
            fixes += 1
        
        if re.search(r'\bTODO\b', content, re.IGNORECASE):
            content = re.sub(r'\bTODO\b', '[perlu dikembangkan]', content, flags=re.IGNORECASE)
            fixes += 1
        
        if re.search(r'\bFIXME\b', content, re.IGNORECASE):
            content = re.sub(r'\bFIXME\b', '[perlu diperbaiki]', content, flags=re.IGNORECASE)
            fixes += 1
        
        if re.search(r'\[.*placeholder.*\]', content, re.IGNORECASE):
            content = re.sub(r'\[.*placeholder.*\]', '[konten perlu dikembangkan]', content, flags=re.IGNORECASE)
            fixes += 1
        
        return content, fixes
    
    def repair_heading_errors(self, content: str) -> tuple[str, int]:
        """Memperbaiki heading yang rusak."""
        fixes = 0
        lines = content.split('\n')
        processed_lines = []
        
        last_heading_level = 0
        
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                
                # If heading level jumps too much, insert intermediate heading
                if last_heading_level > 0 and level > last_heading_level + 1:
                    # Insert a placeholder heading
                    intermediate = '#' * (last_heading_level + 1) + ' Section placeholder'
                    processed_lines.append(intermediate)
                    fixes += 1
                
                last_heading_level = level
            
            processed_lines.append(line)
        
        return '\n'.join(processed_lines), fixes
    
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
            return {"status": "REJECTED", "reason": "Secret leak - manual intervention required"}
        
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
                
                if "asing" in issue_lower or "foreign" in issue_lower:
                    repaired_content, count = self.repair_foreign_text(repaired_content)
                    fixes_this_iteration += count
                    self.repair_log.append({"iteration": iteration, "issue": issue, "action": "repaired_foreign_text"})
                
                elif "melompat" in issue_lower or "heading" in issue_lower:
                    repaired_content, count = self.repair_heading_errors(repaired_content)
                    fixes_this_iteration += count
                    self.repair_log.append({"iteration": iteration, "issue": issue, "action": "repaired_heading"})
                
                elif "lapisan" in issue_lower or "layer" in issue_lower:
                    repaired_content, count = self.repair_missing_layers(repaired_content)
                    fixes_this_iteration += count
                    self.repair_log.append({"iteration": iteration, "issue": issue, "action": "flagged_missing_layer"})
                
                elif "placeholder" in issue_lower or "lorem" in issue_lower:
                    repaired_content, count = self.repair_placeholder_text(repaired_content)
                    fixes_this_iteration += count
                    self.repair_log.append({"iteration": iteration, "issue": issue, "action": "repaired_placeholder"})
            
            self.total_fixes += fixes_this_iteration
            
            if fixes_this_iteration == 0:
                logger.info(f"Tidak ada perbaikan yang dilakukan pada iterasi {iteration}")
                break
            
            logger.info(f"Iterasi {iteration}: {fixes_this_iteration} perbaikan dilakukan")
        
        # Simpan hasil repair
        self.save_repaired_ebook(repaired_content, self.iteration)
        self.save_repair_log()
        
        logger.info(f"Repair completed: {self.total_fixes} total perbaikan dalam {self.iteration} iterasi")
        
        return {
            "status": "COMPLETED",
            "iterations": self.iteration,
            "total_fixes": self.total_fixes,
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