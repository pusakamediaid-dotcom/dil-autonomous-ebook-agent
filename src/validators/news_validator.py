"""
DIL Content & Income Agent - News Validator

Validates news content for source attribution, accuracy, and compliance.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


class NewsValidator:
    """Validator for news content and sources."""
    
    def validate_source(self, source: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single news source entry."""
        errors = []
        
        if not source.get("title"):
            errors.append("Judul berita kosong")
        
        if not source.get("source_name"):
            errors.append("Nama sumber kosong")
        
        if not source.get("url") and source.get("source_type") != "template":
            errors.append("URL sumber kosong")
        
        return len(errors) == 0, errors
    
    def validate_research_report(self, filepath: str) -> Tuple[bool, List[str]]:
        """Validate news research report."""
        errors = []
        
        path = Path(filepath)
        if not path.exists():
            errors.append(f"File tidak ditemukan: {filepath}")
            return False, errors
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data.get("topic"):
                errors.append("Topik kosong")
            
            sources = data.get("sources", [])
            if not sources:
                errors.append("Tidak ada sumber berita")
            
            for i, source in enumerate(sources):
                if source.get("source_type") == "template":
                    continue
                ok, src_errors = self.validate_source(source)
                for err in src_errors:
                    errors.append(f"Sumber {i+1}: {err}")
            
        except json.JSONDecodeError as e:
            errors.append(f"JSON invalid: {e}")
        except Exception as e:
            errors.append(f"Error: {e}")
        
        return len(errors) == 0, errors
    
    def validate_content_drafts(self, filepath: str) -> Tuple[bool, List[str]]:
        """Validate news content drafts."""
        errors = []
        
        path = Path(filepath)
        if not path.exists():
            errors.append(f"File tidak ditemukan: {filepath}")
            return False, errors
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for source attribution
            has_source = bool(re.search(r'(?:sumber|source|referensi)\s*:', content, re.IGNORECASE))
            if not has_source:
                errors.append("Atribusi sumber tidak ditemukan")
            
            # Check for summary label
            has_label = bool(re.search(r'(?:ringkasan|summary|analisis)', content, re.IGNORECASE))
            if not has_label:
                errors.append("Label ringkasan/analisis tidak ditemukan")
            
            # Check for required sections
            required = ["Ringkasan", "Sumber"]
            for section in required:
                if section.lower() not in content.lower():
                    errors.append(f"Section '{section}' tidak ditemukan")
            
        except Exception as e:
            errors.append(f"Error: {e}")
        
        return len(errors) == 0, errors
    
    def check_full_copy_risk(self, content: str, max_words: int = 500) -> List[str]:
        """Check for full article copy risk."""
        warnings = []
        
        word_count = len(content.split())
        if word_count > max_words:
            warnings.append(f"Konten panjang ({word_count} kata) - pastikan bukan salinan penuh")
        
        return warnings


def validate_news_research(filepath: str) -> Tuple[bool, List[str]]:
    """Convenience function for news research validation."""
    validator = NewsValidator()
    return validator.validate_research_report(filepath)


def validate_news_content(filepath: str) -> Tuple[bool, List[str]]:
    """Convenience function for news content validation."""
    validator = NewsValidator()
    return validator.validate_content_drafts(filepath)
