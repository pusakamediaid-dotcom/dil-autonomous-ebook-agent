"""
DIL Autonomous Ebook Agent - JSON Validator

Memvalidasi file JSON untuk memastikan format yang benar.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


class JSONValidator:
    """
    Validator untuk file JSON.
    Memeriksa validitas JSON dan struktur yang diharapkan.
    """
    
    def __init__(self):
        """Inisialisasi JSONValidator."""
        self.errors: List[str] = []
    
    def validate_file(self, filepath: str) -> Tuple[bool, List[str]]:
        """
        Memvalidasi file JSON.
        
        Args:
            filepath: Path ke file JSON.
        
        Returns:
            Tuple (is_valid, list errors).
        """
        self.errors = []
        
        try:
            path = Path(filepath)
            
            if not path.exists():
                self.errors.append(f"File tidak ditemukan: {filepath}")
                return False, self.errors
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"JSON valid: {filepath}")
            return True, []
            
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON decode error: {str(e)}")
            logger.error(f"JSON invalid: {filepath} - {str(e)}")
            return False, self.errors
        except Exception as e:
            self.errors.append(f"Error membaca file: {str(e)}")
            logger.error(f"Error: {filepath} - {str(e)}")
            return False, self.errors
    
    def validate_schema(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Memvalidasi schema JSON.
        
        Args:
            data: Data JSON.
            required_fields: List field yang harus ada.
        
        Returns:
            Tuple (is_valid, list errors).
        """
        self.errors = []
        
        for field in required_fields:
            if field not in data:
                self.errors.append(f"Field wajib tidak ada: {field}")
        
        return len(self.errors) == 0, self.errors
    
    def validate_task_plan(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Memvalidasi task plan JSON."""
        required_fields = [
            "schema_version",
            "run_id",
            "mode",
            "ebook_title",
            "chapters"
        ]
        
        is_valid, errors = self.validate_schema(data, required_fields)
        
        if is_valid and not isinstance(data.get("chapters"), list):
            errors.append("'chapters' harus berupa list")
            is_valid = False
        
        return is_valid, errors
    
    def validate_outline(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Memvalidasi outline JSON."""
        required_fields = [
            "schema_version",
            "ebook_title",
            "chapters",
            "total_chapters"
        ]
        
        is_valid, errors = self.validate_schema(data, required_fields)
        
        if is_valid:
            chapters = data.get("chapters", [])
            if len(chapters) == 0:
                errors.append("Minimal harus ada 1 bab")
                is_valid = False
        
        return is_valid, errors
    
    def validate_run_report(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Memvalidasi run report JSON."""
        required_fields = [
            "report_type",
            "status",
            "execution"
        ]
        
        return self.validate_schema(data, required_fields)


def validate_json_file(filepath: str) -> Tuple[bool, List[str]]:
    """
    Fungsi convenience untuk validasi JSON.
    
    Args:
        filepath: Path ke file.
    
    Returns:
        Tuple (is_valid, list errors).
    """
    validator = JSONValidator()
    return validator.validate_file(filepath)


def validate_json_schema(
    data: Dict[str, Any],
    schema_type: str
) -> Tuple[bool, List[str]]:
    """
    Fungsi convenience untuk validasi schema JSON.
    
    Args:
        data: Data JSON.
        schema_type: Tipe schema (task_plan, outline, run_report).
    
    Returns:
        Tuple (is_valid, list errors).
    """
    validator = JSONValidator()
    
    if schema_type == "task_plan":
        return validator.validate_task_plan(data)
    elif schema_type == "outline":
        return validator.validate_outline(data)
    elif schema_type == "run_report":
        return validator.validate_run_report(data)
    else:
        return True, []