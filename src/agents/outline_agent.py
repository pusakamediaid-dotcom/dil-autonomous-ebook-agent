"""
DIL Autonomous Ebook Agent - Outline Agent

Generates structured ebook outlines based on task plans.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger
from core.run_context import RunContext
from core.task_schema import create_outline

logger = get_logger(__name__)


class OutlineAgent:
    """
    Agent that generates detailed ebook outlines.
    Creates structured chapter/section/subsection layouts.
    """
    
    def __init__(self):
        """Initialize OutlineAgent."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.outline: Dict[str, Any] = {}
    
    def load_task_plan(self, plan_file: str = "output/task_plan.json") -> Dict[str, Any]:
        """
        Load task plan from file.
        
        Args:
            plan_file: Path to task plan JSON.
        
        Returns:
            Task plan dictionary.
        """
        plan_path = Path(plan_file)
        
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan = json.load(f)
                logger.info(f"Loaded task plan from {plan_path}")
                return plan
        except FileNotFoundError:
            logger.warning(f"Task plan not found: {plan_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing task plan: {e}")
            return {}
    
    def generate_chapter_outline(
        self,
        chapter_config: Dict[str, Any],
        mode: str = "test"
    ) -> Dict[str, Any]:
        """
        Generate detailed outline for a single chapter.
        
        Args:
            chapter_config: Chapter configuration from task plan.
            mode: Execution mode.
        
        Returns:
            Detailed chapter outline.
        """
        chapter_number = chapter_config.get("number", 1)
        chapter_title = chapter_config.get("title", f"Chapter {chapter_number}")
        subtopics = chapter_config.get("subtopics", [])
        
        # In test mode, limit sections
        if mode == "test":
            subtopics = subtopics[:2]
        
        sections = []
        
        for i, subtopic in enumerate(subtopics, 1):
            # Create subsections for each subtopic
            subsections = [
                {
                    "title": f"Pengertian {subtopic}",
                    "content_type": "konseptual",
                    "key_concepts": [subtopic, "definisi", "konsep dasar"],
                    "estimated_words": 200
                },
                {
                    "title": f"Contoh {subtopic}",
                    "content_type": "praktikal",
                    "key_concepts": ["contoh", "ilustrasi", "studi kasus"],
                    "estimated_words": 250
                },
                {
                    "title": f"Aplikasi {subtopic}",
                    "content_type": "praktikal",
                    "key_concepts": ["implementasi", "penerapan", "praktik"],
                    "estimated_words": 200
                }
            ]
            
            # In test mode, reduce subsections
            if mode == "test":
                subsections = subsections[:2]
            
            section = {
                "title": subtopic,
                "description": f"Penjelasan mendalam tentang {subtopic}",
                "subsections": subsections
            }
            
            sections.append(section)
        
        # Estimate total words
        total_words = sum(
            sum(s.get("estimated_words", 200) for s in section.get("subsections", []))
            for section in sections
        )
        
        chapter_outline = {
            "number": chapter_number,
            "title": chapter_title,
            "description": chapter_config.get("description", ""),
            "sections": sections,
            "estimated_words": total_words
        }
        
        return chapter_outline
    
    def generate_outline(
        self,
        task_plan: Dict[str, Any],
        mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete outline from task plan.
        
        Args:
            task_plan: Task plan dictionary.
            mode: Execution mode (defaults to task plan mode).
        
        Returns:
            Complete outline dictionary.
        """
        ebook_title = task_plan.get("ebook_title", "Untitled Ebook")
        chapters_config = task_plan.get("chapters", [])
        execution_mode = mode or task_plan.get("mode", "test")
        
        logger.info(f"Generating outline for '{ebook_title}', mode={execution_mode}")
        
        chapter_outlines = []
        
        for chapter_config in chapters_config:
            outline = self.generate_chapter_outline(chapter_config, execution_mode)
            chapter_outlines.append(outline)
        
        outline = create_outline(ebook_title, chapter_outlines)
        
        self.outline = outline
        logger.info(f"Outline generated: {len(chapter_outlines)} chapters")
        
        return outline
    
    def validate_outline(self) -> tuple[bool, List[str]]:
        """
        Validate the generated outline.
        
        Returns:
            Tuple of (is_valid, list of errors).
        """
        errors = []
        
        if not self.outline:
            errors.append("Outline is empty")
            return False, errors
        
        if "ebook_title" not in self.outline:
            errors.append("Missing ebook_title")
        
        if "chapters" not in self.outline:
            errors.append("Missing chapters")
        elif not isinstance(self.outline["chapters"], list):
            errors.append("Chapters must be a list")
        elif len(self.outline["chapters"]) == 0:
            errors.append("At least one chapter required")
        
        # Validate each chapter
        for i, chapter in enumerate(self.outline.get("chapters", [])):
            if "title" not in chapter:
                errors.append(f"Chapter {i+1} missing title")
            if "sections" not in chapter:
                errors.append(f"Chapter {i+1} missing sections")
        
        return len(errors) == 0, errors
    
    def save_outline(self, output_file: str = "output/outline.json") -> None:
        """
        Save outline to JSON file.
        
        Args:
            output_file: Output file path.
        """
        if not self.outline:
            logger.warning("No outline to save - run generate_outline first")
            return
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.outline, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Outline saved to {output_path}")
    
    def execute(self, run_context: RunContext) -> Dict[str, Any]:
        """
        Execute outline agent.
        
        Args:
            run_context: Current run context.
        
        Returns:
            Outline dictionary.
        """
        logger.info("OutlineAgent executing...")
        
        # Load task plan
        task_plan = self.load_task_plan()
        
        if not task_plan:
            logger.error("No task plan available - cannot generate outline")
            # Create minimal outline from run context
            task_plan = {
                "ebook_title": run_context.ebook_title,
                "chapters": [{"number": 1, "title": f"Pengenalan {run_context.ebook_title}"}],
                "mode": run_context.mode
            }
        
        # Generate outline
        outline = self.generate_outline(task_plan)
        
        # Validate
        is_valid, errors = self.validate_outline()
        if not is_valid:
            logger.warning(f"Outline validation errors: {errors}")
        
        # Save
        self.save_outline()
        
        logger.info("OutlineAgent completed")
        
        return outline


def run_outline_agent(run_context: RunContext) -> Dict[str, Any]:
    """
    Convenience function to run OutlineAgent.
    
    Args:
        run_context: Current run context.
    
    Returns:
        Outline dictionary.
    """
    agent = OutlineAgent()
    return agent.execute(run_context)