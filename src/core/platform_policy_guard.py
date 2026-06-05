"""
DIL Content & Income Agent - Platform Policy Guard Module

Enforces platform-specific policies to prevent violations.
Ensures all actions comply with terms of service.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from .logger import get_logger

logger = get_logger(__name__)


class PlatformPolicyGuard:
    """
    Guard that enforces platform-specific policies.
    
    Prevents:
    - Login scraping
    - Rate limit abuse
    - Content that violates platform rules
    - Spam posting
    - Unauthorized API access
    """
    
    PLATFORM_POLICIES = {
        "tokopedia": {
            "max_requests_per_minute": 10,
            "login_scraping_forbidden": True,
            "automated_browsing_forbidden": True,
            "affiliate_disclosure_required": True,
            "data_sources_allowed": ["official_api", "public_page", "manual_input"],
        },
        "shopee": {
            "max_requests_per_minute": 10,
            "login_scraping_forbidden": True,
            "automated_browsing_forbidden": True,
            "affiliate_disclosure_required": True,
            "data_sources_allowed": ["official_api", "public_page", "manual_input"],
        },
        "threads": {
            "max_posts_per_day": 3,
            "auto_post_forbidden": True,
            "spam_forbidden": True,
            "disclosure_required": True,
        },
        "google": {
            "max_posts_per_day": 5,
            "auto_post_forbidden": True,
            "quality_content_required": True,
            "source_citation_required": True,
        },
        "blog": {
            "max_posts_per_day": 3,
            "auto_post_forbidden": True,
            "quality_content_required": True,
        },
    }
    
    GLOBAL_FORBIDDEN = [
        "login_scraping",
        "cookie_stealing",
        "automated_browsing",
        "rate_limit_abuse",
        "spam_posting",
        "spam_commenting",
        "spam_dm",
        "fake_news",
        "hate_speech",
        "copyright_violation",
        "full_article_copy",
    ]
    
    def __init__(self, config_dir: str = "config"):
        """Initialize PlatformPolicyGuard."""
        self.config_dir = Path(config_dir)
        self.violations: List[Dict[str, Any]] = []
    
    def check_action_allowed(self, platform: str, action: str) -> Dict[str, Any]:
        """
        Check if an action is allowed on a platform.
        
        Args:
            platform: Platform identifier.
            action: Action to check.
            
        Returns:
            Dict with 'allowed', 'reason'.
        """
        # Check global forbidden actions
        if action in self.GLOBAL_FORBIDDEN:
            violation = {
                "platform": platform,
                "action": action,
                "status": "blocked",
                "reason": f"Action '{action}' is globally forbidden"
            }
            self.violations.append(violation)
            logger.warning(f"Policy violation: {action} on {platform}")
            return {"allowed": False, "reason": violation["reason"]}
        
        # Check platform-specific policies
        policy = self.PLATFORM_POLICIES.get(platform, {})
        
        if action == "login_scraping" and policy.get("login_scraping_forbidden"):
            violation = {
                "platform": platform,
                "action": action,
                "status": "blocked",
                "reason": f"Login scraping is forbidden on {platform}"
            }
            self.violations.append(violation)
            return {"allowed": False, "reason": violation["reason"]}
        
        if action == "auto_post" and policy.get("auto_post_forbidden"):
            violation = {
                "platform": platform,
                "action": action,
                "status": "blocked",
                "reason": f"Auto-posting is forbidden on {platform}"
            }
            self.violations.append(violation)
            return {"allowed": False, "reason": violation["reason"]}
        
        if action == "spam" and policy.get("spam_forbidden"):
            violation = {
                "platform": platform,
                "action": action,
                "status": "blocked",
                "reason": f"Spam is forbidden on {platform}"
            }
            self.violations.append(violation)
            return {"allowed": False, "reason": violation["reason"]}
        
        return {"allowed": True, "reason": "Action permitted"}
    
    def check_data_source_allowed(self, platform: str, source_type: str) -> Dict[str, Any]:
        """
        Check if a data source is allowed for a platform.
        
        Args:
            platform: Platform identifier.
            source_type: Type of data source.
            
        Returns:
            Dict with 'allowed', 'reason'.
        """
        if source_type in ["login_scraping", "cookie_access", "automated_browsing"]:
            return {
                "allowed": False,
                "reason": f"Source type '{source_type}' is forbidden on all platforms"
            }
        
        policy = self.PLATFORM_POLICIES.get(platform, {})
        allowed_sources = policy.get("data_sources_allowed", ["manual_input"])
        
        if source_type in allowed_sources:
            return {"allowed": True, "reason": "Source type permitted"}
        
        return {
            "allowed": False,
            "reason": f"Source type '{source_type}' not allowed for {platform}. Allowed: {allowed_sources}"
        }
    
    def check_content_policy(self, platform: str, content: str) -> Dict[str, Any]:
        """
        Check if content complies with platform policy.
        
        Args:
            platform: Platform identifier.
            content: Content to check.
            
        Returns:
            Dict with 'compliant', 'issues'.
        """
        issues = []
        
        # Check for forbidden patterns
        forbidden_patterns = {
            "login credentials request": r"(?:password|kata sandi|login)\s*(?:akun|account)",
            "guaranteed income": r"(?:jaminan|pasti|guaranteed)\s*(?:uang|income|penghasilan)",
            "aggressive buy": r"(?:beli sekarang|membeli sekarang|buy now)\s*(?:!!+|⚠️)",
        }
        
        import re
        for pattern_name, pattern in forbidden_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Forbidden pattern: {pattern_name}")
        
        policy = self.PLATFORM_POLICIES.get(platform, {})
        
        # Check max content length
        max_chars = policy.get("max_chars")
        if max_chars and len(content) > max_chars:
            issues.append(f"Content exceeds max length ({len(content)} > {max_chars})")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues
        }
    
    def get_violations(self) -> List[Dict[str, Any]]:
        """Get list of violations."""
        return self.violations
    
    def get_report(self) -> Dict[str, Any]:
        """Get platform policy guard report."""
        return {
            "total_violations": len(self.violations),
            "violations": self.violations,
            "global_forbidden": self.GLOBAL_FORBIDDEN,
            "platforms_monitored": list(self.PLATFORM_POLICIES.keys())
        }


def get_platform_policy_guard() -> PlatformPolicyGuard:
    """Get or create global PlatformPolicyGuard instance."""
    global _global_platform_policy_guard
    if '_global_platform_policy_guard' not in globals():
        _global_platform_policy_guard = PlatformPolicyGuard()
    return _global_platform_policy_guard
