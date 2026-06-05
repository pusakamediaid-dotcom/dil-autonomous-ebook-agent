"""
DIL Content & Income Agent - Approval Gate Module

Enforces human approval before any publish, promote, or paid API action.
All risky actions default to DRAFT until explicitly approved.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from .logger import get_logger

logger = get_logger(__name__)


class ApprovalGate:
    """
    Gate that requires human approval for risky actions.
    
    Actions like publishing, promoting, or using paid APIs
    are blocked until approved by a human reviewer.
    """
    
    # Actions that ALWAYS require approval
    ALWAYS_REQUIRES_APPROVAL = [
        "publish_content",
        "post_to_social",
        "send_email_campaign",
        "use_paid_api",
        "promote_affiliate_link",
        "submit_to_google",
    ]
    
    # Actions that can proceed without approval
    SAFE_ACTIONS = [
        "research",
        "draft_content",
        "generate_plan",
        "generate_report",
        "validate_content",
        "check_compliance",
    ]
    
    def __init__(self, config_dir: str = "config"):
        """Initialize ApprovalGate."""
        self.config_dir = Path(config_dir)
        self.monetization_rules = self._load_rules()
        self.approval_log: List[Dict[str, Any]] = []
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load monetization rules."""
        rules_path = self.config_dir / "monetization_rules.json"
        try:
            if rules_path.exists():
                with open(rules_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load monetization rules: {e}")
        return {}
    
    def requires_approval(self, action: str) -> bool:
        """
        Check if an action requires human approval.
        
        Args:
            action: The action to check.
            
        Returns:
            True if approval is required.
        """
        if action in self.ALWAYS_REQUIRES_APPROVAL:
            return True
        
        if action in self.SAFE_ACTIONS:
            return False
        
        # Unknown actions require approval by default (safe default)
        logger.warning(f"Unknown action '{action}' - requiring approval by default")
        return True
    
    def is_approved(self, action: str, approval_flag: bool = False) -> bool:
        """
        Check if an action is approved.
        
        Args:
            action: The action to check.
            approval_flag: Whether approval was given in the issue/workflow.
            
        Returns:
            True if action is approved to proceed.
        """
        if not self.requires_approval(action):
            return True
        
        if approval_flag:
            logger.info(f"Action '{action}' approved by human")
            self.approval_log.append({
                "action": action,
                "status": "approved",
                "method": "explicit_approval"
            })
            return True
        
        logger.warning(f"Action '{action}' requires approval but not approved")
        self.approval_log.append({
            "action": action,
            "status": "blocked",
            "method": "no_approval"
        })
        return False
    
    def gate_publish(self, content_type: str, approval_flag: bool = False) -> Dict[str, Any]:
        """
        Gate a publish action.
        
        Args:
            content_type: Type of content being published.
            approval_flag: Whether approval was given.
            
        Returns:
            Dict with 'allowed', 'action', and 'reason'.
        """
        action = f"publish_{content_type}"
        
        if self.is_approved(action, approval_flag):
            return {
                "allowed": True,
                "action": action,
                "status": "approved",
                "reason": "Human approval received"
            }
        
        return {
            "allowed": False,
            "action": action,
            "status": "draft",
            "reason": "Publishing requires human approval. Content saved as draft."
        }
    
    def get_safe_actions(self) -> List[str]:
        """Return list of actions that don't need approval."""
        return self.SAFE_ACTIONS.copy()
    
    def get_blocked_actions(self) -> List[str]:
        """Return list of actions that always need approval."""
        return self.ALWAYS_REQUIRES_APPROVAL.copy()
    
    def get_approval_log(self) -> List[Dict[str, Any]]:
        """Return approval log."""
        return self.approval_log
    
    def get_report(self) -> Dict[str, Any]:
        """Get approval gate report."""
        return {
            "total_actions_checked": len(self.approval_log),
            "approved": sum(1 for a in self.approval_log if a["status"] == "approved"),
            "blocked": sum(1 for a in self.approval_log if a["status"] == "blocked"),
            "log": self.approval_log,
            "auto_post_allowed": False,
            "safe_actions": self.SAFE_ACTIONS,
            "blocked_actions": self.ALWAYS_REQUIRES_APPROVAL
        }


def get_approval_gate() -> ApprovalGate:
    """Get or create global ApprovalGate instance."""
    global _global_approval_gate
    if '_global_approval_gate' not in globals():
        _global_approval_gate = ApprovalGate()
    return _global_approval_gate
