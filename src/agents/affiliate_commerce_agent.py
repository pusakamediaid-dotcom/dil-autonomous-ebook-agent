"""
DIL Content & Income Agent - Affiliate Commerce Agent (Orchestrator)

Main orchestrator for affiliate commerce workflow.
Coordinates research, content creation, compliance, and planning.
All publishing requires human approval.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.logger import get_logger
from core.approval_gate import get_approval_gate
from core.source_manager import get_source_manager
from core.cost_guard import CostGuard

from agents.affiliate_product_research_agent import AffiliateProductResearchAgent
from agents.affiliate_content_agent import AffiliateContentAgent
from agents.compliance_agent import ComplianceAgent
from agents.publishing_planner_agent import PublishingPlannerAgent

logger = get_logger(__name__)


class AffiliateCommerceAgent:
    """
    Orchestrator for affiliate commerce workflow.
    
    Workflow:
    1. Read input from issue or workflow_dispatch
    2. Read target niche and audience
    3. Call Product Research Agent
    4. Call Content Agent
    5. Call Compliance Agent
    6. Call Publishing Planner
    7. Generate reports
    8. No auto-posting without approval
    """
    
    def __init__(self):
        """Initialize AffiliateCommerceAgent."""
        self.output_dir = Path("output/affiliate")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.approval_gate = get_approval_gate()
        self.source_manager = get_source_manager()
        self.cost_guard = CostGuard()
        
        # Sub-agents
        self.research_agent = AffiliateProductResearchAgent()
        self.content_agent = AffiliateContentAgent()
        self.compliance_agent = ComplianceAgent()
        self.planner_agent = PublishingPlannerAgent()
        
        # State
        self.niche: str = ""
        self.target_audience: str = ""
        self.platform: str = "tokopedia"
        self.content_brief: str = ""
        self.products: List[Dict[str, Any]] = []
        self.agents_executed: List[str] = []
        self.agents_failed: List[str] = []
    
    def execute_research(self, manual_products: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute product research phase."""
        logger.info("=== AFFILIATE RESEARCH PHASE ===")
        
        try:
            report = self.research_agent.execute(
                niche=self.niche,
                target_audience=self.target_audience,
                platform=self.platform,
                manual_products=manual_products,
                content_brief=self.content_brief
            )
            self.products = report.get("products", [])
            self.agents_executed.append("affiliate_product_research")
            return report
        except Exception as e:
            logger.error(f"Research phase failed: {e}")
            self.agents_failed.append("affiliate_product_research")
            return {"status": "failed", "error": str(e)}
    
    def execute_content_creation(self) -> str:
        """Execute content creation phase."""
        logger.info("=== AFFILIATE CONTENT PHASE ===")
        
        try:
            markdown = self.content_agent.execute(self.products)
            self.agents_executed.append("affiliate_content")
            return markdown
        except Exception as e:
            logger.error(f"Content phase failed: {e}")
            self.agents_failed.append("affiliate_content")
            return ""
    
    def execute_compliance_check(self, content: str) -> Dict[str, Any]:
        """Execute compliance check phase."""
        logger.info("=== AFFILIATE COMPLIANCE PHASE ===")
        
        try:
            report = self.compliance_agent.execute_affiliate_compliance(content, self.products)
            self.compliance_agent.save_compliance_report(report, "affiliate")
            self.agents_executed.append("compliance")
            return report
        except Exception as e:
            logger.error(f"Compliance phase failed: {e}")
            self.agents_failed.append("compliance")
            return {"status": "ERROR", "score": 0}
    
    def execute_publish_planning(self) -> Dict[str, Any]:
        """Execute publish planning phase."""
        logger.info("=== AFFILIATE PUBLISH PLAN PHASE ===")
        
        try:
            plan = self.planner_agent.execute(
                mode="affiliate_publish_plan",
                platforms=["threads", "blog"],
                max_posts=3
            )
            self.agents_executed.append("publishing_planner")
            return plan
        except Exception as e:
            logger.error(f"Publish planning phase failed: {e}")
            self.agents_failed.append("publishing_planner")
            return {"status": "failed", "error": str(e)}
    
    def execute(
        self,
        niche: str,
        target_audience: str,
        platform: str = "tokopedia",
        content_brief: str = "",
        manual_products: List[Dict[str, Any]] = None,
        approval: bool = False
    ) -> Dict[str, Any]:
        """
        Execute full affiliate commerce workflow.
        
        Args:
            niche: Target niche.
            target_audience: Target audience.
            platform: Target platform.
            content_brief: Content brief.
            manual_products: Manual product input.
            approval: Whether approval is given.
            
        Returns:
            Execution result.
        """
        logger.info("=" * 50)
        logger.info("AFFILIATE COMMERCE AGENT - STARTING")
        logger.info("=" * 50)
        
        self.niche = niche
        self.target_audience = target_audience
        self.platform = platform
        self.content_brief = content_brief
        
        # Phase 1: Research
        research_report = self.execute_research(manual_products)
        
        # Phase 2: Content Creation
        content = self.execute_content_creation()
        
        # Phase 3: Compliance Check
        compliance_report = self.execute_compliance_check(content)
        
        # Phase 4: Publish Planning
        publish_plan = self.execute_publish_planning()
        
        # Determine status
        if len(self.agents_failed) == 0:
            status = "SUCCESS"
        elif compliance_report.get("status") == "REJECT":
            status = "COMPLIANCE_REJECTED"
        else:
            status = "PARTIAL_SUCCESS"
        
        result = {
            "status": status,
            "mode": "affiliate_research",
            "niche": self.niche,
            "target_audience": self.target_audience,
            "platform": self.platform,
            "agents_executed": self.agents_executed,
            "agents_failed": self.agents_failed,
            "products_found": len(self.products),
            "compliance_status": compliance_report.get("status"),
            "compliance_score": compliance_report.get("score"),
            "publish_plan_count": len(publish_plan.get("schedule", [])),
            "auto_post_allowed": False,
            "approval_required": True
        }
        
        logger.info("=" * 50)
        logger.info(f"AFFILIATE COMMERCE AGENT - COMPLETED: {status}")
        logger.info("=" * 50)
        
        return result


def run_affiliate_commerce(
    niche: str,
    target_audience: str,
    platform: str = "tokopedia",
    content_brief: str = "",
    manual_products: List[Dict[str, Any]] = None,
    approval: bool = False
) -> Dict[str, Any]:
    """Convenience function to run affiliate commerce workflow."""
    agent = AffiliateCommerceAgent()
    return agent.execute(niche, target_audience, platform, content_brief, manual_products, approval)
