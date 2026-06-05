"""
DIL Content & Income Agent - Publishing Validator

Validates publishing plans for safety and compliance.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


class PublishingValidator:
    """Validator for publishing plans."""
    
    MAX_POSTS_PER_DAY = 3
    ALLOWED_PLATFORMS = ["threads", "google", "blog", "manual"]
    ALLOWED_STATUSES = ["draft", "approved", "published", "rejected"]
    
    def validate_schedule_entry(self, entry: Dict[str, Any], index: int) -> List[str]:
        """Validate a single schedule entry."""
        errors = []
        
        if not entry.get("date"):
            errors.append(f"Entry {index}: Tanggal kosong")
        
        if not entry.get("platform"):
            errors.append(f"Entry {index}: Platform kosong")
        elif entry["platform"] not in self.ALLOWED_PLATFORMS:
            errors.append(f"Entry {index}: Platform tidak dikenal: {entry['platform']}")
        
        status = entry.get("status", "")
        if status and status not in self.ALLOWED_STATUSES:
            errors.append(f"Entry {index}: Status tidak valid: {status}")
        
        # Auto-post check
        if entry.get("status") == "published" and not entry.get("approval_required"):
            errors.append(f"Entry {index}: Status 'published' tanpa approval")
        
        return errors
    
    def validate_publishing_plan(self, filepath: str) -> Tuple[bool, List[str]]:
        """Validate publishing plan file."""
        errors = []
        
        path = Path(filepath)
        if not path.exists():
            errors.append(f"File tidak ditemukan: {filepath}")
            return False, errors
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            schedule = data.get("schedule", [])
            
            if not schedule:
                errors.append("Jadwal kosong")
            
            # Check each entry
            for i, entry in enumerate(schedule):
                entry_errors = self.validate_schedule_entry(entry, i)
                errors.extend(entry_errors)
            
            # Check for auto-post
            if data.get("auto_post_allowed"):
                errors.append("auto_post_allowed harus false")
            
            # Check all entries are draft
            non_draft = [e for e in schedule if e.get("status") not in ["draft", ""]]
            if non_draft:
                errors.append(f"Ditemukan {len(non_draft)} entry dengan status bukan 'draft'")
            
            # Check max posts per day
            from collections import Counter
            dates = Counter(e.get("date") for e in schedule)
            for date, count in dates.items():
                if count > self.MAX_POSTS_PER_DAY:
                    errors.append(f"Terlalu banyak posting pada {date}: {count} (maks {self.MAX_POSTS_PER_DAY})")
            
        except json.JSONDecodeError as e:
            errors.append(f"JSON invalid: {e}")
        except Exception as e:
            errors.append(f"Error: {e}")
        
        return len(errors) == 0, errors


def validate_publishing_plan(filepath: str) -> Tuple[bool, List[str]]:
    """Convenience function for publishing plan validation."""
    validator = PublishingValidator()
    return validator.validate_publishing_plan(filepath)
