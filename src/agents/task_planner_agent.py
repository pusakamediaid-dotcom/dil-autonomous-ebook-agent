"""
DIL Autonomous Ebook Agent - Task Planner Agent

Plans and structures ebook generation tasks based on issue content.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger
from core.run_context import RunContext
from core.task_schema import create_task_plan

logger = get_logger(__name__)


class TaskPlannerAgent:
    """
    Agent that plans ebook generation tasks.
    Analyzes issue content and creates structured task plans.
    """
    
    def __init__(self):
        """Initialize TaskPlannerAgent."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.task_plan: Dict[str, Any] = {}
    
    def analyze_issue(self, run_context: RunContext) -> Dict[str, Any]:
        """
        Analyze issue content to extract task parameters.
        
        Args:
            run_context: Current run context.
        
        Returns:
            Analysis dictionary.
        """
        analysis = {
            "title": run_context.ebook_title or "Untitled Ebook",
            "target": run_context.target_audience or "General Audience",
            "level": run_context.reading_level or "intermediate",
            "mode": run_context.mode or "test",
            "brief": run_context.content_brief or "",
            "chapters_requested": run_context.total_chapters or 1,
            "has_pdf": run_context.pdf_required,
            "has_approval": run_context.approval_given
        }
        
        logger.info(f"Issue analyzed: {analysis['title']}, mode={analysis['mode']}")
        
        return analysis
    
    def generate_chapters(
        self,
        title: str,
        brief: str,
        count: int,
        mode: str
    ) -> List[Dict[str, Any]]:
        """
        Generate chapter structure based on mode.
        
        For test mode: generates minimum viable structure.
        
        Args:
            title: Ebook title.
            brief: Content brief.
            count: Number of chapters.
            mode: Execution mode.
        
        Returns:
            List of chapter configurations.
        """
        chapters = []
        
        # In test mode, limit to 1 chapter with 2-3 subtopics
        if mode == "test":
            count = 1
        
        # Generate chapters
        for i in range(1, count + 1):
            if i == 1:
                chapter_title = f"Pengenalan {title}"
                description = f"Berkenalan dengan konsep dasar dan pentingnya {title}"
                subtopics = [
                    "Definisi dan Konsep Dasar",
                    "Latar Belakang dan Konteks",
                    "Manfaat dan Tujuan"
                ]
            else:
                chapter_title = f"Bab {i}: Topik Utama {i-1}"
                description = f"Penjelasan mendalam tentang aspek {i-1}"
                subtopics = [
                    "Teori dan Prinsip",
                    "Implementasi Praktis",
                    "Studi Kasus"
                ]
            
            # Limit subtopics in test mode
            if mode == "test":
                subtopics = subtopics[:2]
            
            chapter = {
                "number": i,
                "title": chapter_title,
                "description": description,
                "subtopics": subtopics,
                "estimated_words": 800 if mode == "test" else 1500,
                "priority": i
            }
            
            chapters.append(chapter)
        
        logger.info(f"Generated {len(chapters)} chapters for mode={mode}")
        
        return chapters
    
    def estimate_cost(
        self,
        chapters: List[Dict[str, Any]],
        mode: str
    ) -> Dict[str, Any]:
        """
        Estimate cost for generating chapters.
        
        Args:
            chapters: List of chapter configurations.
            mode: Execution mode.
        
        Returns:
            Cost estimation dictionary.
        """
        # Estimate based on words
        total_words = sum(c.get("estimated_words", 500) for c in chapters)
        
        # Rough token estimate: ~1.33 tokens per word
        tokens_per_word = 1.33
        estimated_tokens = int(total_words * tokens_per_word)
        
        # Add overhead for prompts
        prompt_overhead = estimated_tokens // 4
        
        min_tokens = estimated_tokens + prompt_overhead
        max_tokens = min_tokens + (min_tokens // 2)
        
        # Assume average cost of $0.001 per 1K tokens
        avg_cost_per_1k = 0.001
        estimated_cost = (max_tokens / 1000) * avg_cost_per_1k
        
        return {
            "min_tokens": min_tokens,
            "max_tokens": max_tokens,
            "estimated_cost_usd": round(estimated_cost, 6)
        }
    
    def create_plan(self, run_context: RunContext) -> Dict[str, Any]:
        """
        Create complete task plan.
        
        Args:
            run_context: Current run context.
        
        Returns:
            Task plan dictionary.
        """
        analysis = self.analyze_issue(run_context)
        
        chapters = self.generate_chapters(
            title=analysis["title"],
            brief=analysis["brief"],
            count=analysis["chapters_requested"],
            mode=analysis["mode"]
        )
        
        cost_estimate = self.estimate_cost(chapters, analysis["mode"])
        
        # Provider selection (placeholder - will be filled by RouterAgent)
        provider_selection = {
            "preferred": run_context.api_preference or "auto",
            "fallback": "provider_1",
            "reason": "Will be determined by router based on availability"
        }
        
        plan = create_task_plan(
            run_id=run_context.run_id,
            mode=analysis["mode"],
            ebook_title=analysis["title"],
            target_audience=analysis["target"],
            reading_level=analysis["level"],
            chapters=chapters,
            provider_selection=provider_selection,
            cost_estimate=cost_estimate
        )
        
        self.task_plan = plan
        logger.info(f"Task plan created: {len(chapters)} chapters, mode={analysis['mode']}")
        
        return plan
    
    def save_plan(self, output_file: str = "output/task_plan.json") -> None:
        """
        Save task plan to JSON file.
        
        Args:
            output_file: Output file path.
        """
        if not self.task_plan:
            logger.warning("No task plan to save - run create_plan first")
            return
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.task_plan, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Task plan saved to {output_path}")
    
    def execute(self, run_context: RunContext) -> Dict[str, Any]:
        """
        Execute task planner agent.
        
        Args:
            run_context: Current run context.
        
        Returns:
            Task plan dictionary.
        """
        logger.info("TaskPlannerAgent executing...")
        
        plan = self.create_plan(run_context)
        self.save_plan()
        
        logger.info("TaskPlannerAgent completed")
        
        return plan


def run_task_planner(run_context: RunContext) -> Dict[str, Any]:
    """
    Convenience function to run TaskPlannerAgent.
    
    Args:
        run_context: Current run context.
    
    Returns:
        Task plan dictionary.
    """
    agent = TaskPlannerAgent()
    return agent.execute(run_context)