"""
DIL Autonomous Ebook Agent - Markdown Validator

Memvalidasi format Markdown dan struktur ebook.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


class MarkdownValidator:
    """
    Validator untuk file Markdown.
    Memeriksa heading structure dan 5 lapisan.
    """
    
    REQUIRED_LAYERS = ["[KONSEP]", "[ANALOGI]", "[RUMUS]", "[CONTOH]", "[APLIKASI]"]
    
    def __init__(self):
        """Inisialisasi MarkdownValidator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load_content(self, filepath: str) -> Optional[str]:
        """Memuat konten dari file."""
        try:
            path = Path(filepath)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"Error memuat file: {e}")
            return None
    
    def validate_heading_structure(self, content: str) -> Tuple[bool, List[str]]:
        """
        Memvalidasi struktur heading.
        Memastikan tidak ada level yang melompat.
        
        Args:
            content: Konten markdown.
        
        Returns:
            Tuple (is_valid, list errors).
        """
        self.errors = []
        lines = content.split('\n')
        
        last_level = 0
        in_code_block = False
        
        for i, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                continue
            
            if line.startswith('#'):
                # Hitung level heading
                level = 0
                for char in line:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                # Validasi level berurutan
                # Level boleh sama atau naik 1 level
                # Tidak boleh turun lebih dari 1 level secara langsung
                if last_level > 0:
                    if level > last_level + 1:
                        self.errors.append(
                            f"Line {i}: Heading melompat dari H{last_level} ke H{level}"
                        )
                
                last_level = level
        
        return len(self.errors) == 0, self.errors
    
    def validate_five_layers(self, content: str) -> Tuple[bool, List[str]]:
        """
        Memvalidasi keberadaan 5 lapisan wajib.
        
        Args:
            content: Konten markdown.
        
        Returns:
            Tuple (is_valid, list errors).
        """
        self.errors = []
        
        for layer in self.REQUIRED_LAYERS:
            count = content.count(layer)
            if count == 0:
                self.errors.append(f"Lapisan wajib tidak ada: {layer}")
            elif count < 3:  # Minimal 3 instance
                self.warnings.append(f"Lapisan {layer} hanya muncul {count} kali (minimal 3)")
        
        return len(self.errors) == 0, self.errors
    
    def validate_headings_exist(self, content: str) -> Tuple[bool, List[str]]:
        """
        Memvalidasi bahwa minimal ada heading H1 dan H2.
        
        Args:
            content: Konten markdown.
        
        Returns:
            Tuple (is_valid, list errors).
        """
        self.errors = []
        
        # Cek H1
        if not re.search(r'^#\s+', content, re.MULTILINE):
            self.errors.append("Tidak ada heading H1 (# Judul)")
        
        # Cek H2
        if not re.search(r'^##\s+', content, re.MULTILINE):
            self.errors.append("Tidak ada heading H2 (## Bab)")
        
        return len(self.errors) == 0, self.errors
    
    def validate_code_blocks(self, content: str) -> Tuple[bool, List[str]]:
        """
        Memvalidasi code blocks.
        
        Args:
            content: Konten markdown.
        
        Returns:
            Tuple (is_valid, list errors).
        """
        self.errors = []
        
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        for block in code_blocks:
            if block.count('```') != 2:
                self.errors.append("Code block tidak ditutup dengan ```")
        
        return len(self.errors) == 0, self.errors
    
    def validate_links(self, content: str) -> Tuple[bool, List[str]]:
        """
        Memvalidasi format link markdown.
        
        Args:
            content: Konten markdown.
        
        Returns:
            Tuple (is_valid, list warnings).
        """
        self.warnings = []
        
        # Cek broken links (placeholder)
        broken_link_patterns = [
            r'\[.*\]\(\s*\)',  # Empty link
            r'\[.*\]\(#\)',    # Hash link
        ]
        
        for pattern in broken_link_patterns:
            matches = re.findall(pattern, content)
            if matches:
                self.warnings.append(f"Found {len(matches)} potentially broken link(s)")
        
        return True, self.warnings
    
    def validate_file(self, filepath: str) -> Dict[str, Any]:
        """
        Memvalidasi file markdown lengkap.
        
        Args:
            filepath: Path ke file markdown.
        
        Returns:
            Dictionary hasil validasi.
        """
        content = self.load_content(filepath)
        
        if not content:
            return {
                "is_valid": False,
                "errors": ["File tidak dapat dimuat"],
                "warnings": []
            }
        
        results = {
            "heading_structure": self.validate_heading_structure(content),
            "five_layers": self.validate_five_layers(content),
            "headings_exist": self.validate_headings_exist(content),
            "code_blocks": self.validate_code_blocks(content),
            "links": self.validate_links(content)
        }
        
        all_errors = []
        all_warnings = []
        
        for check, (is_valid, messages) in results.items():
            if not is_valid:
                all_errors.extend(messages)
            all_warnings.extend(messages)
        
        return {
            "is_valid": len(all_errors) == 0,
            "errors": all_errors,
            "warnings": list(set(all_warnings)),
            "checks": {k: {"passed": v[0], "messages": v[1]} for k, v in results.items()}
        }


def validate_markdown_file(filepath: str) -> Dict[str, Any]:
    """
    Fungsi convenience untuk validasi markdown.
    
    Args:
        filepath: Path ke file.
    
    Returns:
        Dictionary hasil validasi.
    """
    validator = MarkdownValidator()
    return validator.validate_file(filepath)