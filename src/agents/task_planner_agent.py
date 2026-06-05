"""
DIL Autonomous Ebook Agent - Task Planner Agent

Plans and structures ebook generation tasks based on issue content.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from core.logger import get_logger
from core.run_context import RunContext
from core.task_schema import create_task_plan

logger = get_logger(__name__)


class TaskPlannerAgent:
    """Agent that plans ebook generation tasks."""

    def __init__(self):
        """Initialize TaskPlannerAgent."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.task_plan: Dict[str, Any] = {}

    def analyze_issue(self, run_context: RunContext) -> Dict[str, Any]:
        """Analyze issue content to extract task parameters."""
        analysis = {
            "title": run_context.ebook_title or "Untitled Ebook",
            "target": run_context.target_audience or "General Audience",
            "level": run_context.reading_level or "intermediate",
            "mode": run_context.mode or "test",
            "brief": run_context.content_brief or "",
            "chapters_requested": run_context.total_chapters or 1,
            "has_pdf": run_context.pdf_required,
            "has_approval": run_context.approval_given,
        }
        logger.info(f"Issue analyzed: {analysis['title']}, mode={analysis['mode']}")
        return analysis

    def _normalize_chapter_count(self, count: int, mode: str) -> int:
        """Normalize chapter count for safe execution modes."""
        if mode == "test":
            return 1
        if mode == "session":
            if count < 3:
                logger.info("Session mode requires at least 3 chapters; adjusted upward")
                return 3
            if count > 4:
                logger.info("Session mode allows max 4 chapters; adjusted downward")
                return 4
        return max(1, count)

    def _base_subtopics(self, index: int, title: str, brief: str) -> List[str]:
        """Create at least 3 practical subtopics for each chapter."""
        if index == 1:
            return [
                "Definisi dan Konsep Dasar",
                "Latar Belakang dan Konteks Praktis",
                "Manfaat, Tujuan, dan Kesalahan Umum",
            ]
        return [
            f"Prinsip Utama Topik {index - 1}",
            f"Langkah Praktis Topik {index - 1}",
            f"Contoh Penerapan Topik {index - 1}",
        ]

    def generate_chapters(self, title: str, brief: str, count: int, mode: str) -> List[Dict[str, Any]]:
        """Generate chapter structure based on mode."""
        chapters: List[Dict[str, Any]] = []
        count = self._normalize_chapter_count(count, mode)

        for i in range(1, count + 1):
            if i == 1:
                chapter_title = f"Pengenalan {title}"
                description = f"Berkenalan dengan konsep dasar dan pentingnya {title}"
            else:
                chapter_title = f"Bab {i}: Topik Utama {i - 1}"
                description = f"Penjelasan mendalam tentang aspek {i - 1}"

            subtopics = self._base_subtopics(i, title, brief)

            if mode == "test":
                subtopics = subtopics[:2]
            elif mode == "session":
                # Session mode must keep at least 3 subtopics per chapter.
                subtopics = subtopics[:4]
                while len(subtopics) < 3:
                    subtopics.append(f"Pendalaman Praktis {len(subtopics) + 1}")

            chapters.append({
                "number": i,
                "title": chapter_title,
                "description": description,
                "subtopics": subtopics,
                "estimated_words": 800 if mode == "test" else 1500,
                "priority": i,
            })

        logger.info(f"Generated {len(chapters)} chapters for mode={mode}")
        return chapters

    def estimate_cost(self, chapters: List[Dict[str, Any]], mode: str) -> Dict[str, Any]:
        """Estimate cost for generating chapters."""
        total_words = sum(c.get("estimated_words", 500) for c in chapters)
        estimated_tokens = int(total_words * 1.33)
        prompt_overhead = estimated_tokens // 4
        min_tokens = estimated_tokens + prompt_overhead
        max_tokens = min_tokens + (min_tokens // 2)
        estimated_cost = (max_tokens / 1000) * 0.001
        return {
            "min_tokens": min_tokens,
            "max_tokens": max_tokens,
            "estimated_cost_usd": round(estimated_cost, 6),
        }

    def create_plan(self, run_context: RunContext) -> Dict[str, Any]:
        """Create complete task plan."""
        analysis = self.analyze_issue(run_context)
        chapters = self.generate_chapters(
            title=analysis["title"],
            brief=analysis["brief"],
            count=analysis["chapters_requested"],
            mode=analysis["mode"],
        )
        cost_estimate = self.estimate_cost(chapters, analysis["mode"])

        provider_selection = {
            "preferred": run_context.api_preference or "auto",
            "fallback": "provider_1",
            "reason": "Will be determined by router based on availability",
        }

        plan = create_task_plan(
            run_id=run_context.run_id,
            mode=analysis["mode"],
            ebook_title=analysis["title"],
            target_audience=analysis["target"],
            reading_level=analysis["level"],
            chapters=chapters,
            provider_selection=provider_selection,
            cost_estimate=cost_estimate,
        )

        self.task_plan = plan
        logger.info(f"Task plan created: {len(chapters)} chapters, mode={analysis['mode']}")
        return plan

    def save_plan(self, output_file: str = "output/task_plan.json") -> None:
        """Save task plan to JSON file."""
        if not self.task_plan:
            logger.warning("No task plan to save - run create_plan first")
            return
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.task_plan, f, indent=2, ensure_ascii=False)
        logger.info(f"Task plan saved to {output_path}")

    def execute(self, run_context: RunContext) -> Dict[str, Any]:
        """Execute task planner agent."""
        logger.info("TaskPlannerAgent executing...")
        plan = self.create_plan(run_context)
        self.save_plan()
        logger.info("TaskPlannerAgent completed")
        return plan


def run_task_planner(run_context: RunContext) -> Dict[str, Any]:
    """Convenience function to run TaskPlannerAgent."""
    agent = TaskPlannerAgent()
    return agent.execute(run_context)
