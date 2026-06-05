"""
DIL Autonomous Ebook Agent - Reviewer Agent

Agent otomatis untuk memvalidasi output ebook.
Memeriksa kelengkapan, keamanan, dan kualitas konten.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger

logger = get_logger(__name__)


class ReviewerAgent:
    """
    Agent yang mereview output ebook secara otomatis.
    Menghasilkan review_report.json dengan status dan rekomendasi.
    """
    
    def __init__(self):
        """Inisialisasi ReviewerAgent."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.ebook_path = self.output_dir / "ebook.md"
        self.outline_path = self.output_dir / "outline.json"
        
        self.review_result: Dict[str, Any] = {}
    
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
    
    def load_outline(self) -> Optional[Dict[str, Any]]:
        """Memuat outline."""
        try:
            if self.outline_path.exists():
                with open(self.outline_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error memuat outline: {e}")
            return None
    
    def check_chapters(self, content: str, outline: Dict[str, Any]) -> List[str]:
        """Memeriksa apakah semua bab ada."""
        issues = []
        chapters = outline.get("chapters", [])
        
        for chapter in chapters:
            chapter_num = chapter.get("chapter_number", 0)
            chapter_title = chapter.get("chapter_title", "")
            
            # Cek apakah bab ada di konten
            pattern = rf"Bab\s+{chapter_num}\s*[-—]"
            if not re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Bab {chapter_num} tidak ditemukan di konten")
        
        return issues
    
    def check_five_layers(self, content: str) -> List[str]:
        """Memeriksa apakah setiap subbab memiliki 5 lapisan."""
        issues = []
        required_layers = ["[KONSEP]", "[ANALOGI]", "[RUMUS]", "[CONTOH]", "[APLIKASI]"]
        
        # Cek setiap lapisan
        for layer in required_layers:
            count = content.count(layer)
            if count == 0:
                issues.append(f"Lapisan {layer} tidak ditemukan")
        
        return issues
    
    def check_foreign_text(self, content: str) -> tuple[bool, List[str]]:
        """
        Memeriksa apakah ada teks asing/campur bahasa.
        
        Returns:
            Tuple (detected, list of detected patterns).
        """
        detected = []
        foreign_patterns = [
            (r'[\u4e00-\u9fff]', 'Mandarin/CJK'),
            (r'[\u0400-\u04ff]', 'Cyrillic'),
            (r'[\u0600-\u06ff]', 'Arabic'),
            (r'[\u3040-\u309f\u30a0-\u30ff]', 'Japanese Hiragana/Katakana'),
            (r'[\uac00-\ud7af]', 'Korean Hangul')
        ]
        
        for pattern, name in foreign_patterns:
            matches = re.findall(pattern, content)
            if matches:
                detected.append(f"{name}: {len(matches)} karakter")
        
        return len(detected) > 0, detected
    
    def check_secrets(self, content: str) -> List[str]:
        """Memeriksa apakah ada API key atau secret bocor."""
        issues = []
        
        # Pattern untuk API keys
        secret_patterns = [
            r'sk-[a-zA-Z0-9]{20,}',
            r'ghp_[a-zA-Z0-9]{36,}',
            r'AIza[a-zA-Z0-9_-]{35,}',
            r'[a-zA-Z0-9_-]{40,}--[a-zA-Z0-9_-]{20,}'
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, content)
            if matches:
                issues.append(f"Potential secret detected (pattern tersembunyi)")
        
        return issues
    
    def check_heading_structure(self, content: str) -> List[str]:
        """Memeriksa konsistensi struktur heading."""
        issues = []
        lines = content.split('\n')
        
        last_heading_level = 0
        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                # Tentukan level heading
                level = 0
                for c in line:
                    if c == '#':
                        level += 1
                    else:
                        break
                
                # Heading level harus naik berurutan (tidak boleh loncat)
                # Dari # ke ### langsung tidak diperbolehkan
                if level > last_heading_level + 1 and last_heading_level > 0:
                    issues.append(f"Line {i}: Heading melompat dari level {last_heading_level} ke {level}")
                
                last_heading_level = level
        
        return issues
    
    def check_content_length(self, content: str, min_words: int = 100) -> List[str]:
        """Memeriksa apakah konten tidak terlalu pendek."""
        issues = []
        
        word_count = len(content.split())
        
        if word_count < min_words:
            issues.append(f"Konten terlalu pendek: {word_count} kata (minimal: {min_words})")
        
        return issues
    
    def check_placeholder_text(self, content: str) -> List[str]:
        """Memeriksa apakah ada placeholder mentah."""
        issues = []
        
        placeholder_patterns = [
            (r'lorem\s+ipsum', 'Lorem ipsum terdeteksi'),
            (r'todo', 'TODO terdeteksi'),
            (r'fixme', 'FIXME terdeteksi'),
            (r'placeholder', 'Placeholder terdeteksi'),
            (r'\[.*placeholder.*\]', 'Placeholder dalam kurung siku')
        ]
        
        for pattern, message in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(message)
        
        return issues
    
    def calculate_score(self, issues: List[str], total_checks: int = 7) -> float:
        """
        Menghitung score review (0-100).
        
        Args:
            issues: List issue yang ditemukan.
            total_checks: Total jumlah pemeriksaan.
        
        Returns:
            Score 0-100.
        """
        if total_checks == 0:
            return 100.0
        
        base_score = 100.0
        
        # Pengurangan per issue
        deductions = {
            'secret_leak': 50,      # Major security issue
            'foreign_text': 20,     # Quality issue
            'missing_layers': 15,   # Structure issue
            'heading_error': 10,    # Format issue
            'content_short': 10,    # Quality issue
            'placeholder': 5,       # Minor issue
            'chapter_missing': 15   # Structure issue
        }
        
        for issue in issues:
            issue_lower = issue.lower()
            
            if 'secret' in issue_lower:
                base_score -= deductions['secret_leak']
            elif 'asing' in issue_lower or 'foreign' in issue_lower:
                base_score -= deductions['foreign_text']
            elif 'lapisan' in issue_lower or 'layer' in issue_lower:
                base_score -= deductions['missing_layers']
            elif 'melompat' in issue_lower or 'heading' in issue_lower:
                base_score -= deductions['heading_error']
            elif 'pendek' in issue_lower:
                base_score -= deductions['content_short']
            elif 'placeholder' in issue_lower or 'lorem' in issue_lower:
                base_score -= deductions['placeholder']
            elif 'tidak ditemukan' in issue_lower or 'bab' in issue_lower:
                base_score -= deductions['chapter_missing']
            else:
                base_score -= 5  # Default deduction
        
        return max(0.0, base_score)
    
    def determine_status(self, score: float, issues: List[str]) -> str:
        """Menentukan status berdasarkan score dan issues."""
        secret_leak = any('secret' in i.lower() for i in issues)
        
        if secret_leak:
            return "REJECT"
        
        if score >= 80:
            return "PASS"
        elif score >= 50:
            return "REPAIR"
        else:
            return "REJECT"
    
    def execute_review(self) -> Dict[str, Any]:
        """
        Menjalankan review lengkap.
        
        Returns:
            Dictionary review result.
        """
        logger.info("ReviewerAgent executing...")
        
        all_issues: List[str] = []
        
        # Muat konten
        content = self.load_ebook()
        outline = self.load_outline()
        
        if not content:
            all_issues.append("Ebook file tidak ditemukan atau kosong")
            
            result = {
                "status": "REJECT",
                "score": 0,
                "issues": all_issues,
                "repair_required": False,
                "foreign_text_detected": False,
                "foreign_text_patterns": [],
                "missing_layers": [],
                "heading_errors": [],
                "secret_leak_detected": False,
                "recommendation": "Ebook tidak dapat di-review karena file tidak ada atau kosong."
            }
            
            self.review_result = result
            return result
        
        # Jalankan semua pemeriksaan
        if outline:
            chapter_issues = self.check_chapters(content, outline)
            all_issues.extend(chapter_issues)
        
        layer_issues = self.check_five_layers(content)
        all_issues.extend(layer_issues)
        
        foreign_detected, foreign_patterns = self.check_foreign_text(content)
        
        secret_issues = self.check_secrets(content)
        all_issues.extend(secret_issues)
        
        heading_issues = self.check_heading_structure(content)
        all_issues.extend(heading_issues)
        
        length_issues = self.check_content_length(content)
        all_issues.extend(length_issues)
        
        placeholder_issues = self.check_placeholder_text(content)
        all_issues.extend(placeholder_issues)
        
        # Hitung score
        score = self.calculate_score(all_issues)
        status = self.determine_status(score, all_issues)
        
        # Generate recommendation
        if status == "PASS":
            recommendation = "Ebook siap digunakan. Semua pemeriksaan passed."
        elif status == "REPAIR":
            recommendation = "Ebook perlu perbaikan minor sebelum digunakan. Silakan jalankan Repair Agent."
        else:
            recommendation = "Ebook tidak dapat digunakan karena issue kritikal. Perbaiki terlebih dahulu."
        
        result = {
            "status": status,
            "score": round(score, 2),
            "issues": all_issues,
            "repair_required": status in ["REPAIR", "REJECT"] and not any('secret' in i.lower() for i in all_issues),
            "foreign_text_detected": foreign_detected,
            "foreign_text_patterns": foreign_patterns,
            "missing_layers": layer_issues,
            "heading_errors": heading_issues,
            "secret_leak_detected": len(secret_issues) > 0,
            "recommendation": recommendation
        }
        
        self.review_result = result
        logger.info(f"Review completed: status={status}, score={score}")
        
        return result
    
    def save_review_report(self, output_file: str = "output/review_report.json") -> None:
        """Menyimpan review report ke file."""
        if not self.review_result:
            logger.warning("Tidak ada review result untuk disimpan")
            return
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.review_result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Review report disimpan ke {output_path}")
    
    def execute(self) -> Dict[str, Any]:
        """Menjalankan reviewer agent."""
        result = self.execute_review()
        self.save_review_report()
        
        logger.info("ReviewerAgent completed")
        
        return result


def run_reviewer_agent() -> Dict[str, Any]:
    """Fungsi convenience untuk menjalankan ReviewerAgent."""
    agent = ReviewerAgent()
    return agent.execute()