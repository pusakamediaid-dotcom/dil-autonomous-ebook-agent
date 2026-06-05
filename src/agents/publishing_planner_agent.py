"""
DIL Content & Income Agent - Publishing Planner Agent

Creates publishing schedules for content.
All entries default to DRAFT status.
No auto-posting without approval.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from core.logger import get_logger
from core.approval_gate import get_approval_gate

logger = get_logger(__name__)


class PublishingPlannerAgent:
    """
    Agent that creates publishing schedules.
    
    All entries default to DRAFT status.
    No auto-posting without human approval.
    
    Rules:
    - Max 3 posts per day
    - Max 15 posts per week
    - 2-hour cooldown between same platform
    - No duplicate content
    - Content variation required
    """
    
    MAX_POSTS_PER_DAY = 3
    MAX_POSTS_PER_WEEK = 15
    PREFERRED_HOURS = ["08:00", "12:00", "18:00", "21:00"]
    TIMEZONE = "Asia/Jakarta"
    
    def __init__(self):
        """Initialize PublishingPlannerAgent."""
        self.output_dir = Path("output/publishing")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.approval_gate = get_approval_gate()
        self.schedule: List[Dict[str, Any]] = []
    
    def load_affiliate_drafts(self) -> List[Dict[str, Any]]:
        """Load affiliate content drafts."""
        drafts = []
        drafts_path = Path("output/affiliate/content_drafts.md")
        
        if drafts_path.exists():
            drafts.append({
                "type": "affiliate",
                "file": "output/affiliate/content_drafts.md",
                "content_type": "affiliate_promotion"
            })
        
        return drafts
    
    def load_news_drafts(self) -> List[Dict[str, Any]]:
        """Load news content drafts."""
        drafts = []
        drafts_path = Path("output/news/news_content_drafts.md")
        
        if drafts_path.exists():
            drafts.append({
                "type": "news",
                "file": "output/news/news_content_drafts.md",
                "content_type": "news_summary"
            })
        
        return drafts
    
    def create_schedule(
        self,
        mode: str = "affiliate_publish_plan",
        platforms: List[str] = None,
        max_posts: int = 3,
        start_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        Create publishing schedule.
        
        Args:
            mode: Publishing mode.
            platforms: Target platforms.
            max_posts: Maximum posts to schedule.
            start_date: Start date (ISO format).
            
        Returns:
            List of scheduled items.
        """
        if platforms is None:
            platforms = ["threads", "blog"]
        
        if start_date:
            base_date = datetime.fromisoformat(start_date)
        else:
            base_date = datetime.now() + timedelta(days=1)
        
        # Limit to max posts per day
        max_posts = min(max_posts, self.MAX_POSTS_PER_DAY)
        
        schedule = []
        
        # Get content files based on mode
        content_items = []
        if "affiliate" in mode:
            content_items = self.load_affiliate_drafts()
        elif "news" in mode:
            content_items = self.load_news_drafts()
        else:
            content_items = self.load_affiliate_drafts() + self.load_news_drafts()
        
        if not content_items:
            # Create placeholder schedule
            content_items = [{
                "type": "placeholder",
                "file": "N/A",
                "content_type": "draft_needed"
            }]
        
        for i, platform in enumerate(platforms[:max_posts]):
            # Use preferred posting hours
            hour_idx = i % len(self.PREFERRED_HOURS)
            time_str = self.PREFERRED_HOURS[hour_idx]
            
            content_item = content_items[i % len(content_items)] if content_items else {}
            
            entry = {
                "date": base_date.strftime("%Y-%m-%d"),
                "time": time_str,
                "platform": platform,
                "content_file": content_item.get("file", "N/A"),
                "content_type": content_item.get("content_type", "draft"),
                "caption": f"[Draft caption untuk {platform}]",
                "link": "",
                "approval_required": True,
                "status": "draft",
                "notes": "Menunggu review dan approval manusia"
            }
            
            schedule.append(entry)
        
        self.schedule = schedule
        logger.info(f"Created schedule with {len(schedule)} entries")
        return schedule
    
    def save_schedule(self, mode: str = "affiliate_publish_plan") -> None:
        """Save publishing schedule to file."""
        output_path = self.output_dir / "publishing_plan.json"
        
        plan = {
            "mode": mode,
            "generated_at": datetime.now().isoformat(),
            "platforms": list(set(e["platform"] for e in self.schedule)),
            "max_posts_per_day": self.MAX_POSTS_PER_DAY,
            "max_posts_per_week": self.MAX_POSTS_PER_WEEK,
            "schedule": self.schedule,
            "warnings": [
                "Semua status adalah DRAFT",
                "Tidak ada auto-posting tanpa approval",
                "Review setiap konten sebelum dipublikasikan",
                "Pastikan affiliate disclosure disertakan",
                "Pastikan sumber berita disertakan"
            ],
            "auto_post_allowed": False,
            "approval_required": True
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Publishing plan saved to {output_path}")
    
    def execute(
        self,
        mode: str = "affiliate_publish_plan",
        platforms: List[str] = None,
        max_posts: int = 3,
        start_date: str = None
    ) -> Dict[str, Any]:
        """
        Execute publishing planning.
        
        Args:
            mode: Publishing mode.
            platforms: Target platforms.
            max_posts: Maximum posts.
            start_date: Start date.
            
        Returns:
            Publishing plan.
        """
        logger.info("PublishingPlannerAgent executing...")
        
        schedule = self.create_schedule(mode, platforms, max_posts, start_date)
        self.save_schedule(mode)
        
        plan = {
            "mode": mode,
            "schedule_count": len(schedule),
            "all_draft": all(e["status"] == "draft" for e in schedule),
            "auto_post_allowed": False
        }
        
        logger.info(f"PublishingPlannerAgent completed: {len(schedule)} entries, all DRAFT")
        return plan


def run_publishing_planner(
    mode: str = "affiliate_publish_plan",
    platforms: List[str] = None,
    max_posts: int = 3,
    start_date: str = None
) -> Dict[str, Any]:
    """Convenience function to run publishing planner."""
    agent = PublishingPlannerAgent()
    return agent.execute(mode, platforms, max_posts, start_date)
