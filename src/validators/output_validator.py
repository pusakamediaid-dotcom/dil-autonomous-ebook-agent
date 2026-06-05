"""
DIL Autonomous Ebook Agent - Output Validator

Memvalidasi file output yang diharapkan ada.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


class OutputValidator:
    """
    Validator untuk file output.
    Memeriksa apakah file yang diharapkan ada dan tidak kosong.
    """
    
    REQUIRED_OUTPUTS = [
        "task_plan.json",
        "outline.json",
        "ebook.md",
        "run_report.json",
        "cost_report.json"
    ]
    
    OPTIONAL_OUTPUTS = [
        "memory_context.json",
        "routing_decision.json",
        "review_report.json",
        "ebook_repaired.md",
        "error_log.txt"
    ]
    
    def __init__(self, output_dir: str = "output"):
        """
        Inisialisasi OutputValidator.
        
        Args:
            output_dir: Path ke direktori output.
        """
        self.output_dir = Path(output_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_file_exists(self, filename: str) -> Tuple[bool, str]:
        """
        Memeriksa apakah file ada dan tidak kosong.
        
        Args:
            filename: Nama file.
        
        Returns:
            Tuple (exists, message).
        """
        filepath = self.output_dir / filename
        
        if not filepath.exists():
            return False, f"File tidak ditemukan: {filename}"
        
        # Cek apakah file kosong
        if filepath.stat().st_size == 0:
            return False, f"File kosong: {filename}"
        
        return True, f"OK: {filename}"
    
    def validate_required_outputs(self) -> Tuple[bool, List[str]]:
        """
        Memvalidasi semua output wajib.
        
        Returns:
            Tuple (all_exist, list errors).
        """
        self.errors = []
        
        for filename in self.REQUIRED_OUTPUTS:
            exists, message = self.validate_file_exists(filename)
            if not exists:
                self.errors.append(message)
        
        return len(self.errors) == 0, self.errors
    
    def validate_optional_outputs(self) -> Dict[str, bool]:
        """
        Memvalidasi output opsional.
        
        Returns:
            Dictionary dengan status setiap file.
        """
        results = {}
        
        for filename in self.OPTIONAL_OUTPUTS:
            exists, _ = self.validate_file_exists(filename)
            results[filename] = exists
        
        return results
    
    def validate_json_content(self, filename: str) -> Tuple[bool, str]:
        """
        Memvalidasi bahwa file JSON memiliki konten valid.
        
        Args:
            filename: Nama file JSON.
        
        Returns:
            Tuple (is_valid, message).
        """
        filepath = self.output_dir / filename
        
        if not filepath.exists():
            return False, f"File tidak ditemukan"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
            return True, f"JSON valid: {filename}"
        except json.JSONDecodeError as e:
            return False, f"JSON invalid: {filename} - {str(e)}"
        except Exception as e:
            return False, f"Error: {filename} - {str(e)}"
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Memvalidasi semua output.
        
        Returns:
            Dictionary hasil validasi lengkap.
        """
        required_ok, required_errors = self.validate_required_outputs()
        optional_status = self.validate_optional_outputs()
        
        # Validasi JSON content
        json_files = ["task_plan.json", "outline.json", "run_report.json", "cost_report.json"]
        json_valid = {}
        
        for filename in json_files:
            is_valid, _ = self.validate_json_content(filename)
            json_valid[filename] = is_valid
        
        return {
            "all_required_present": required_ok,
            "required_errors": required_errors,
            "optional_status": optional_status,
            "json_valid": json_valid,
            "summary": {
                "required_count": len(self.REQUIRED_OUTPUTS),
                "required_found": len(self.REQUIRED_OUTPUTS) - len(required_errors),
                "optional_count": len(self.OPTIONAL_OUTPUTS),
                "optional_found": sum(optional_status.values())
            }
        }


def validate_outputs(output_dir: str = "output") -> Dict[str, Any]:
    """
    Fungsi convenience untuk validasi output.
    
    Args:
        output_dir: Path ke direktori output.
    
    Returns:
        Dictionary hasil validasi.
    """
    validator = OutputValidator(output_dir)
    return validator.validate_all()