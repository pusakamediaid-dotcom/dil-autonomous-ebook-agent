"""
DIL Content & Income Agent - Source Manager Module

Manages data sources for affiliate and news agents.
Ensures only allowed sources are used.
Falls back to manual input when APIs are unavailable.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from .logger import get_logger
from .secret_manager import get_secret_manager

logger = get_logger(__name__)


class SourceManager:
    """
    Manages data sources for monetization agents.
    
    Only allows:
    - Official APIs with valid keys
    - RSS feeds from official media
    - User manual input
    - User CSV uploads
    - Public pages that don't require login
    
    Forbids:
    - Login scraping
    - Cookie-based access
    - Automated browsing
    - Rate-limit abuse
    """
    
    ALLOWED_SOURCE_TYPES = [
        "official_api",
        "rss_feed",
        "google_custom_search",
        "news_api",
        "user_manual_input",
        "user_csv_upload",
        "public_page",
        "official_website",
    ]
    
    FORBIDDEN_SOURCE_TYPES = [
        "login_scraping",
        "cookie_access",
        "automated_browsing",
        "rate_limit_abuse",
        "full_article_copy",
    ]
    
    def __init__(self, config_dir: str = "config"):
        """Initialize SourceManager."""
        self.config_dir = Path(config_dir)
        self.news_sources_config = self._load_news_sources()
        self.affiliate_rules_config = self._load_affiliate_rules()
        self.secret_manager = get_secret_manager()
    
    def _load_news_sources(self) -> Dict[str, Any]:
        """Load news sources config."""
        path = self.config_dir / "news_sources.json"
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load news sources: {e}")
        return {}
    
    def _load_affiliate_rules(self) -> Dict[str, Any]:
        """Load affiliate rules config."""
        path = self.config_dir / "affiliate_rules.json"
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load affiliate rules: {e}")
        return {}
    
    def is_source_allowed(self, source_type: str) -> bool:
        """Check if a source type is allowed."""
        return source_type in self.ALLOWED_SOURCE_TYPES
    
    def is_source_forbidden(self, source_type: str) -> bool:
        """Check if a source type is forbidden."""
        return source_type in self.FORBIDDEN_SOURCE_TYPES
    
    def check_news_api_available(self) -> bool:
        """Check if News API key is available."""
        api_key = os.environ.get("NEWS_API_KEY")
        return bool(api_key and len(api_key) > 0)
    
    def check_google_search_available(self) -> bool:
        """Check if Google Custom Search API is available."""
        api_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
        cse_id = os.environ.get("GOOGLE_CSE_ID")
        return bool(api_key and cse_id and len(api_key) > 0 and len(cse_id) > 0)
    
    def check_tokopedia_api_available(self) -> bool:
        """Check if Tokopedia API is available."""
        api_key = os.environ.get("TOKOPEDIA_API_KEY")
        affiliate_id = os.environ.get("TOKOPEDIA_AFFILIATE_ID")
        return bool(api_key and len(api_key) > 0)
    
    def check_social_posting_available(self) -> bool:
        """Check if social posting API is available."""
        api_key = os.environ.get("SOCIAL_POSTING_API_KEY")
        return bool(api_key and len(api_key) > 0)
    
    def get_available_sources(self) -> Dict[str, Any]:
        """Get summary of available data sources."""
        return {
            "news_api": self.check_news_api_available(),
            "google_custom_search": self.check_google_search_available(),
            "tokopedia_api": self.check_tokopedia_api_available(),
            "social_posting": self.check_social_posting_available(),
            "manual_input": True,  # Always available
            "csv_upload": True,    # Always available
            "mode": "manual_draft" if not any([
                self.check_news_api_available(),
                self.check_google_search_available(),
                self.check_tokopedia_api_available()
            ]) else "api_available"
        }
    
    def get_affiliate_platforms(self) -> List[Dict[str, Any]]:
        """Get configured affiliate platforms."""
        platforms = self.affiliate_rules_config.get("allowed_platforms", [])
        result = []
        for p in platforms:
            has_api = False
            if p["id"] == "tokopedia":
                has_api = self.check_tokopedia_api_available()
            result.append({
                **p,
                "api_available": has_api
            })
        return result
    
    def get_report(self) -> Dict[str, Any]:
        """Get source manager report."""
        available = self.get_available_sources()
        return {
            "available_sources": available,
            "mode": available["mode"],
            "affiliate_platforms": self.get_affiliate_platforms(),
            "allowed_source_types": self.ALLOWED_SOURCE_TYPES,
            "forbidden_source_types": self.FORBIDDEN_SOURCE_TYPES
        }


def get_source_manager() -> SourceManager:
    """Get or create global SourceManager instance."""
    global _global_source_manager
    if '_global_source_manager' not in globals():
        _global_source_manager = SourceManager()
    return _global_source_manager
