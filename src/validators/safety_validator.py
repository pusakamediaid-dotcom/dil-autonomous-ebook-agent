"""
DIL Autonomous Ebook Agent - Safety Validator

Memvalidasi keamanan konten - mendeteksi secret leak dan konten berbahaya.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


class SafetyValidator:
    """
    Validator untuk keamanan konten.
    Mendeteksi API keys, secrets, dan konten berbahaya.
    """
    
    SECRET_PATTERNS = [
        # API Keys
        (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API Key terdeteksi'),
        (r'ghp_[a-zA-Z0-9]{36,}', 'GitHub Personal Access Token terdeteksi'),
        (r'gho_[a-zA-Z0-9]{36,}', 'GitHub OAuth Token terdeteksi'),
        (r'ghs_[a-zA-Z0-9]{36,}', 'GitHub Server Access Token terdeteksi'),
        (r'ghu_[a-zA-Z0-9]{36,}', 'GitHub User Access Token terdeteksi'),
        (r'AIza[a-zA-Z0-9_-]{35,}', 'Google API Key terdeteksi'),
        (r'[a-zA-Z0-9_-]{40,}--[a-zA-Z0-9_-]{20,}', 'Potential API Key terdeteksi'),
        
        # Bearer tokens
        (r'Bearer\s+[a-zA-Z0-9_-]{20,}', 'Bearer Token terdeteksi'),
        
        # Generic long strings that look like keys
        (r'[a-zA-Z0-9]{60,}', 'Long alphanumeric string (potential key) terdeteksi'),
    ]
    
    DANGEROUS_PATTERNS = [
        # Credentials in URL
        (r'https?://[^:]+:[^@]+@', 'Credentials in URL terdeteksi'),
        
        # SQL injection hints
        (r';\s*drop\s+table', 'Potentially dangerous SQL pattern'),
        (r';\s*delete\s+from', 'Potentially dangerous SQL pattern'),
        
        # Command injection hints
        (r';\s*rm\s+-rf', 'Potentially dangerous command'),
        (r';\s*del\s+/', 'Potentially dangerous command'),
    ]
    
    def __init__(self):
        """Inisialisasi SafetyValidator."""
        self.findings: List[Dict[str, str]] = []
    
    def check_file(self, filepath: str) -> Dict[str, Any]:
        """
        Memeriksa file untuk secret dan konten berbahaya.
        
        Args:
            filepath: Path ke file.
        
        Returns:
            Dictionary hasil pemeriksaan.
        """
        self.findings = []
        
        try:
            path = Path(filepath)
            
            if not path.exists():
                return {
                    "is_safe": True,
                    "findings": [],
                    "error": "File tidak ditemukan"
                }
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.check_content(content, path.name)
            
        except Exception as e:
            logger.error(f"Error memeriksa file: {e}")
            return {
                "is_safe": False,
                "findings": [],
                "error": str(e)
            }
    
    def check_content(self, content: str, filename: str = "unknown") -> Dict[str, Any]:
        """
        Memeriksa konten untuk secret dan konten berbahaya.
        
        Args:
            content: Konten yang akan diperiksa.
            filename: Nama file (untuk reporting).
        
        Returns:
            Dictionary hasil pemeriksaan.
        """
        self.findings = []
        
        # Check secret patterns
        for pattern, message in self.SECRET_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                for match in matches[:3]:  # Batasi 3 temuan per pattern
                    self.findings.append({
                        "type": "secret",
                        "severity": "high",
                        "pattern": pattern,
                        "message": message,
                        "file": filename,
                        "preview": self._mask_preview(match)
                    })
        
        # Check dangerous patterns
        for pattern, message in self.DANGEROUS_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                self.findings.append({
                    "type": "dangerous",
                    "severity": "critical",
                    "pattern": pattern,
                    "message": message,
                    "file": filename,
                    "preview": "[pattern tersembunyi]"
                })
        
        is_safe = len(self.findings) == 0
        
        return {
            "is_safe": is_safe,
            "findings": self.findings,
            "secrets_found": sum(1 for f in self.findings if f["type"] == "secret"),
            "dangerous_found": sum(1 for f in self.findings if f["type"] == "dangerous")
        }
    
    def _mask_preview(self, text: str) -> str:
        """
        Membuat preview yang di-mask untuk logging.
        
        Args:
            text: Teks asli.
        
        Returns:
            Teks yang sudah di-mask.
        """
        if len(text) <= 8:
            return "[SHORT_MASKED]"
        
        return text[:4] + "****" + text[-4:]
    
    def check_output_directory(self, output_dir: str = "output") -> Dict[str, Any]:
        """
        Memeriksa semua file di direktori output.
        
        Args:
            output_dir: Path ke direktori output.
        
        Returns:
            Dictionary hasil pemeriksaan.
        """
        results = {
            "files_checked": 0,
            "files_with_issues": 0,
            "total_findings": 0,
            "issues_by_file": {}
        }
        
        path = Path(output_dir)
        
        if not path.exists():
            return {
                **results,
                "error": "Direktori tidak ditemukan"
            }
        
        for filepath in path.rglob("*"):
            if filepath.is_file() and not filepath.name.startswith('.'):
                result = self.check_file(str(filepath))
                
                if not result.get("is_safe", True):
                    results["files_with_issues"] += 1
                    results["total_findings"] += len(result.get("findings", []))
                    results["issues_by_file"][filepath.name] = result.get("findings", [])
                
                results["files_checked"] += 1
        
        return results


def check_content_safety(content: str, filename: str = "unknown") -> Dict[str, Any]:
    """
    Fungsi convenience untuk pemeriksaan keamanan.
    
    Args:
        content: Konten yang akan diperiksa.
        filename: Nama file.
    
    Returns:
        Dictionary hasil pemeriksaan.
    """
    validator = SafetyValidator()
    return validator.check_content(content, filename)


def check_file_safety(filepath: str) -> Dict[str, Any]:
    """
    Fungsi convenience untuk pemeriksaan file.
    
    Args:
        filepath: Path ke file.
    
    Returns:
        Dictionary hasil pemeriksaan.
    """
    validator = SafetyValidator()
    return validator.check_file(filepath)