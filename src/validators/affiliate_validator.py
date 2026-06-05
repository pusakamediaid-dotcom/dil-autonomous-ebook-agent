"""
DIL Content & Income Agent - Affiliate Validator

Validates affiliate content for compliance and quality.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


class AffiliateValidator:
    """Validator for affiliate content and products."""
    
    REQUIRED_DISCLOSURE_KEYWORDS = ["affiliate", "komisi", "tautan"]
    
    def validate_product(self, product: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single product entry."""
        errors = []
        
        required_fields = ["product_name", "why_recommended", "target_buyer"]
        for field in required_fields:
            if not product.get(field):
                errors.append(f"Field '{field}' kosong")
        
        # Check for forbidden products
        forbidden = ["palsu", "counterfeit", "illegal", "narkoba", "senjata"]
        name_lower = product.get("product_name", "").lower()
        for kw in forbidden:
            if kw in name_lower:
                errors.append(f"Produk mengandung kata terlarang: {kw}")
        
        return len(errors) == 0, errors
    
    def validate_disclosure(self, content: str) -> Tuple[bool, List[str]]:
        """Validate that affiliate disclosure is present."""
        errors = []
        
        has_disclosure = any(
            kw in content.lower() for kw in self.REQUIRED_DISCLOSURE_KEYWORDS
        )
        
        if not has_disclosure:
            errors.append("Affiliate disclosure tidak ditemukan")
        
        return len(errors) == 0, errors
    
    def validate_content_drafts(self, filepath: str) -> Tuple[bool, List[str]]:
        """Validate content drafts file."""
        errors = []
        
        path = Path(filepath)
        if not path.exists():
            errors.append(f"File tidak ditemukan: {filepath}")
            return False, errors
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for disclosure
            disc_ok, disc_errors = self.validate_disclosure(content)
            errors.extend(disc_errors)
            
            # Check for required sections
            required_sections = ["Draft Threads", "CTA", "Disclosure", "Risiko"]
            for section in required_sections:
                if section.lower() not in content.lower():
                    errors.append(f"Section '{section}' tidak ditemukan")
            
        except Exception as e:
            errors.append(f"Error membaca file: {e}")
        
        return len(errors) == 0, errors
    
    def validate_product_candidates(self, filepath: str) -> Tuple[bool, List[str]]:
        """Validate product candidates JSON file."""
        errors = []
        
        path = Path(filepath)
        if not path.exists():
            errors.append(f"File tidak ditemukan: {filepath}")
            return False, errors
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            products = data.get("products", [])
            if not products:
                errors.append("Tidak ada produk dalam file")
            
            for i, product in enumerate(products):
                ok, prod_errors = self.validate_product(product)
                for err in prod_errors:
                    errors.append(f"Produk {i+1}: {err}")
            
        except json.JSONDecodeError as e:
            errors.append(f"JSON invalid: {e}")
        except Exception as e:
            errors.append(f"Error: {e}")
        
        return len(errors) == 0, errors


def validate_affiliate_content(filepath: str) -> Tuple[bool, List[str]]:
    """Convenience function for affiliate content validation."""
    validator = AffiliateValidator()
    return validator.validate_content_drafts(filepath)


def validate_product_candidates(filepath: str) -> Tuple[bool, List[str]]:
    """Convenience function for product candidates validation."""
    validator = AffiliateValidator()
    return validator.validate_product_candidates(filepath)
