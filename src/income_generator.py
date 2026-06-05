"""
DIL Content & Income Agent - Income Generator (Orchestrator)

Main entry point for affiliate and news agent workflows.
Orchestrates all income-related agents.
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.logger import get_logger
from core.cost_guard import CostGuard
from core.approval_gate import get_approval_gate
from core.source_manager import get_source_manager
from core.report_builder import ReportBuilder

from agents.affiliate_commerce_agent import AffiliateCommerceAgent
from agents.affiliate_product_research_agent import AffiliateProductResearchAgent
from agents.affiliate_content_agent import AffiliateContentAgent
from agents.news_research_agent import NewsResearchAgent
from agents.news_content_agent import NewsContentAgent
from agents.publishing_planner_agent import PublishingPlannerAgent
from agents.compliance_agent import ComplianceAgent

from validators.affiliate_validator import AffiliateValidator
from validators.news_validator import NewsValidator
from validators.publishing_validator import PublishingValidator

logger = get_logger(__name__)

SUPPORTED_MODES = [
    "affiliate_research",
    "affiliate_content",
    "affiliate_publish_plan",
    "news_research",
    "news_content",
    "news_publish_plan",
    "income_report",
]


class IncomeGenerator:
    """
    Orchestrator for income-related agent workflows.
    
    Supported modes:
    - affiliate_research: Research products for affiliate promotion
    - affiliate_content: Create affiliate content drafts
    - affiliate_publish_plan: Create affiliate publishing schedule
    - news_research: Research news from official sources
    - news_content: Create news content drafts
    - news_publish_plan: Create news publishing schedule
    - income_report: Generate income potential report
    """
    
    def __init__(self):
        """Initialize IncomeGenerator."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        (self.output_dir / "affiliate").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "news").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "publishing").mkdir(parents=True, exist_ok=True)
        
        self.cost_guard = CostGuard()
        self.approval_gate = get_approval_gate()
        self.source_manager = get_source_manager()
        self.report_builder = ReportBuilder()
        
        # State
        self.mode: str = ""
        self.niche: str = ""
        self.target_audience: str = ""
        self.platform: str = "manual"
        self.content_brief: str = ""
        self.manual_links: List[str] = []
        self.manual_items: List[Dict[str, Any]] = []
        self.manual_products: List[Dict[str, Any]] = None
        self.topic: str = ""
        self.approval: bool = False
        
        self.agents_executed: List[str] = []
        self.agents_failed: List[str] = []
        self.warnings: List[str] = []
    
    def parse_inputs(self) -> None:
        """Parse inputs from environment variables (GitHub Actions)."""
        # Mode
        self.mode = os.environ.get("INPUT_INCOME_MODE", "").strip()
        if not self.mode:
            self.mode = os.environ.get("INPUT_MODE", "affiliate_research").strip()
        
        # Common inputs
        self.niche = os.environ.get("INPUT_NICHE", "").strip()
        self.target_audience = os.environ.get("INPUT_TARGET_AUDIENCE", "").strip()
        self.platform = os.environ.get("INPUT_PLATFORM", "manual").strip()
        self.content_brief = os.environ.get("INPUT_CONTENT_BRIEF", "").strip()
        self.topic = os.environ.get("INPUT_TOPIC", "").strip()
        self.approval = os.environ.get("INPUT_APPROVAL", "").lower() in ["true", "yes", "1"]
        
        # Manual inputs
        manual_links_str = os.environ.get("INPUT_MANUAL_LINKS", "").strip()
        if manual_links_str:
            self.manual_links = [l.strip() for l in manual_links_str.split(",") if l.strip()]
        
        logger.info(f"Inputs parsed: mode={self.mode}, niche='{self.niche[:30]}', platform={self.platform}")
    
    def run_affiliate_research(self) -> Dict[str, Any]:
        """Run affiliate research mode."""
        logger.info("=== AFFILIATE RESEARCH MODE ===")
        
        if not self.niche:
            self.niche = "Produk digital, perlengkapan belajar, alat kerja kreator pemula"
            self.warnings.append("Niche tidak diisi - menggunakan default")
        
        if not self.target_audience:
            self.target_audience = "Pelajar, mahasiswa, guru, kreator pemula, penjual ebook"
            self.warnings.append("Target audiens tidak diisi - menggunakan default")
        
        agent = AffiliateCommerceAgent()
        result = agent.execute(
            niche=self.niche,
            target_audience=self.target_audience,
            platform=self.platform,
            content_brief=self.content_brief,
            manual_products=self.manual_products,
            approval=self.approval
        )
        
        self.agents_executed.extend(result.get("agents_executed", []))
        self.agents_failed.extend(result.get("agents_failed", []))
        
        return result
    
    def run_affiliate_content(self) -> Dict[str, Any]:
        """Run affiliate content creation mode."""
        logger.info("=== AFFILIATE CONTENT MODE ===")
        
        agent = AffiliateContentAgent()
        content = agent.execute(self.manual_products)
        
        if content:
            self.agents_executed.append("affiliate_content")
        else:
            self.agents_failed.append("affiliate_content")
        
        # Run compliance
        compliance = ComplianceAgent()
        report = compliance.execute_affiliate_compliance(content, self.manual_products)
        compliance.save_compliance_report(report, "affiliate")
        self.agents_executed.append("compliance")
        
        return {
            "status": "SUCCESS" if content else "FAILED",
            "content_created": bool(content),
            "compliance_status": report.get("status"),
            "compliance_score": report.get("score")
        }
    
    def run_affiliate_publish_plan(self) -> Dict[str, Any]:
        """Run affiliate publish planning mode."""
        logger.info("=== AFFILIATE PUBLISH PLAN MODE ===")
        
        agent = PublishingPlannerAgent()
        plan = agent.execute(
            mode="affiliate_publish_plan",
            platforms=["threads", "blog"],
            max_posts=3
        )
        
        self.agents_executed.append("publishing_planner")
        return plan
    
    def run_news_research(self) -> Dict[str, Any]:
        """Run news research mode."""
        logger.info("=== NEWS RESEARCH MODE ===")
        
        if not self.topic:
            self.topic = "Berita teknologi dunia, AI, pendidikan digital, dan ekonomi kreator"
            self.warnings.append("Topik tidak diisi - menggunakan default")
        
        agent = NewsResearchAgent()
        report = agent.execute(
            topic=self.topic,
            manual_links=self.manual_links if self.manual_links else None,
            content_brief=self.content_brief
        )
        
        self.agents_executed.append("news_research")
        return report
    
    def run_news_content(self) -> Dict[str, Any]:
        """Run news content creation mode."""
        logger.info("=== NEWS CONTENT MODE ===")
        
        # Load research data
        research_data = None
        research_path = Path("output/news/news_research_report.json")
        if research_path.exists():
            try:
                with open(research_path, 'r', encoding='utf-8') as f:
                    research_data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load research data: {e}")
        
        agent = NewsContentAgent()
        content = agent.execute(research_data)
        
        if content:
            self.agents_executed.append("news_content")
        else:
            self.agents_failed.append("news_content")
        
        # Run compliance
        compliance = ComplianceAgent()
        sources = research_data.get("sources", []) if research_data else []
        report = compliance.execute_news_compliance(content, sources)
        compliance.save_compliance_report(report, "news")
        self.agents_executed.append("compliance")
        
        return {
            "status": "SUCCESS" if content else "FAILED",
            "content_created": bool(content),
            "compliance_status": report.get("status"),
            "compliance_score": report.get("score")
        }
    
    def run_news_publish_plan(self) -> Dict[str, Any]:
        """Run news publish planning mode."""
        logger.info("=== NEWS PUBLISH PLAN MODE ===")
        
        agent = PublishingPlannerAgent()
        plan = agent.execute(
            mode="news_publish_plan",
            platforms=["threads", "blog"],
            max_posts=3
        )
        
        self.agents_executed.append("publishing_planner")
        return plan
    
    def run_income_report(self) -> Dict[str, Any]:
        """Run income report generation mode."""
        logger.info("=== INCOME REPORT MODE ===")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "mode": "income_report",
            "summary": {
                "affiliate_products_researched": 0,
                "affiliate_drafts_created": 0,
                "news_items_researched": 0,
                "news_drafts_created": 0,
                "publishing_schedules_created": 0,
            },
            "potential": {
                "description": "Laporan ini berisi ringkasan potensi penghasilan dari konten yang sudah dibuat.",
                "note": "Semua angka adalah estimasi. Penghasilan aktual tergantung kualitas konten, traffic, dan konversi."
            },
            "next_steps": [
                "Review semua draft konten",
                "Verifikasi affiliate links",
                "Publikasikan konten yang sudah di-approve",
                "Monitor performa secara manual",
                "Optimasi berdasarkan data"
            ]
        }
        
        # Check existing outputs
        affiliate_dir = Path("output/affiliate")
        news_dir = Path("output/news")
        publishing_dir = Path("output/publishing")
        
        if (affiliate_dir / "product_candidates.json").exists():
            with open(affiliate_dir / "product_candidates.json", 'r') as f:
                data = json.load(f)
                report["summary"]["affiliate_products_researched"] = len(data.get("products", []))
        
        if (affiliate_dir / "content_drafts.md").exists():
            report["summary"]["affiliate_drafts_created"] = 1
        
        if (news_dir / "news_research_report.json").exists():
            with open(news_dir / "news_research_report.json", 'r') as f:
                data = json.load(f)
                report["summary"]["news_items_researched"] = len(data.get("sources", []))
        
        if (news_dir / "news_content_drafts.md").exists():
            report["summary"]["news_drafts_created"] = 1
        
        if (publishing_dir / "publishing_plan.json").exists():
            report["summary"]["publishing_schedules_created"] = 1
        
        # Save report
        output_path = self.output_dir / "income_report.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.agents_executed.append("income_report")
        
        logger.info("Income report generated")
        return report
    
    def run(self) -> Dict[str, Any]:
        """Execute the income generator workflow."""
        logger.info("=" * 50)
        logger.info("DIL INCOME AGENT - STARTING")
        logger.info("=" * 50)
        
        self.parse_inputs()
        
        if self.mode not in SUPPORTED_MODES:
            logger.error(f"Mode tidak didukung: {self.mode}")
            return {
                "status": "FAILED",
                "error": f"Mode '{self.mode}' tidak didukung. Mode yang tersedia: {SUPPORTED_MODES}"
            }
        
        result = {}
        
        try:
            if self.mode == "affiliate_research":
                result = self.run_affiliate_research()
            elif self.mode == "affiliate_content":
                result = self.run_affiliate_content()
            elif self.mode == "affiliate_publish_plan":
                result = self.run_affiliate_publish_plan()
            elif self.mode == "news_research":
                result = self.run_news_research()
            elif self.mode == "news_content":
                result = self.run_news_content()
            elif self.mode == "news_publish_plan":
                result = self.run_news_publish_plan()
            elif self.mode == "income_report":
                result = self.run_income_report()
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            result = {"status": "FAILED", "error": str(e)}
            self.agents_failed.append(self.mode)
        
        # Determine final status
        if len(self.agents_failed) == 0:
            final_status = "SUCCESS"
        elif len(self.agents_executed) > 0:
            final_status = "PARTIAL_SUCCESS"
        else:
            final_status = "FAILED"
        
        # Build final result
        final_result = {
            "status": final_status,
            "mode": self.mode,
            "agents_executed": self.agents_executed,
            "agents_failed": self.agents_failed,
            "warnings": self.warnings,
            "auto_post_allowed": False,
            "approval_required": True,
            "source_report": self.source_manager.get_report(),
            **result
        }
        
        # Save run report
        self.save_run_report(final_result)
        self.save_cost_report()
        
        logger.info("=" * 50)
        logger.info(f"DIL INCOME AGENT - COMPLETED: {final_status}")
        logger.info("=" * 50)
        
        return final_result
    
    def save_run_report(self, result: Dict[str, Any]) -> None:
        """Save run report."""
        output_path = self.output_dir / "run_report.json"
        
        report = {
            "report_type": "income_agent_run_report",
            "generated_at": datetime.now().isoformat(),
            **result
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Run report saved to {output_path}")
    
    def save_cost_report(self) -> None:
        """Save cost report."""
        output_path = self.output_dir / "cost_report.json"
        
        report = self.cost_guard.get_report()
        report["mode"] = self.mode
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Cost report saved to {output_path}")


def main():
    """Main entry point."""
    try:
        generator = IncomeGenerator()
        result = generator.run()
        
        print("\n" + "=" * 50)
        print("INCOME AGENT RESULT")
        print("=" * 50)
        print(f"Status: {result.get('status')}")
        print(f"Mode: {result.get('mode')}")
        print(f"Agents executed: {result.get('agents_executed', [])}")
        print(f"Agents failed: {result.get('agents_failed', [])}")
        print(f"Warnings: {len(result.get('warnings', []))}")
        print(f"Auto-post allowed: {result.get('auto_post_allowed')}")
        print("=" * 50)
        
        status = result.get('status', 'FAILED')
        if status in ['SUCCESS', 'PARTIAL_SUCCESS']:
            sys.exit(0)
        else:
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
