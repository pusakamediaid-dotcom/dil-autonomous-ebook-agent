"""
DIL Autonomous Ebook Agent - Outline Agent

Menghasilkan outline ebook terstruktur berdasarkan task plans.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger
from core.run_context import RunContext

logger = get_logger(__name__)


class OutlineAgent:
    """Agent yang menghasilkan outline ebook detail."""

    def __init__(self):
        """Inisialisasi OutlineAgent."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.outline: Dict[str, Any] = {}

    def load_task_plan(self, plan_file: str = "output/task_plan.json") -> Dict[str, Any]:
        """Memuat task plan dari file."""
        plan_path = Path(plan_file)
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                plan = json.load(f)
                logger.info(f"Loaded task plan dari {plan_path}")
                return plan
        except FileNotFoundError:
            logger.warning(f"Task plan tidak ditemukan: {plan_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing task plan: {e}")
            return {}

    def generate_chapter_outline(self, chapter_config: Dict[str, Any], mode: str = "test") -> Dict[str, Any]:
        """Menghasilkan outline detail untuk satu bab."""
        chapter_number = chapter_config.get("number", 1)
        chapter_title = chapter_config.get("title", f"Bab {chapter_number}")
        subtopics = chapter_config.get("subtopics", [])

        if mode == "test":
            subtopics = subtopics[:2]
        elif mode == "session":
            subtopics = subtopics[:4]
        elif mode == "full":
            subtopics = subtopics[:6]

        sections = []
        required_layers = ["KONSEP", "ANALOGI", "RUMUS", "CONTOH", "APLIKASI"]

        for i, subtopic in enumerate(subtopics, 1):
            subtopic_number = f"{chapter_number}.{i}"
            subsection = {
                "subtopic_number": subtopic_number,
                "subtopic_title": subtopic,
                "required_layers": required_layers,
                "visual_note": "Diagram dapat dibuat pada tahap HTML/PDF jika diperlukan",
                "estimated_words": 300 if mode == "test" else 500,
            }
            section = {
                "title": subtopic,
                "description": f"Penjelasan mendalam tentang {subtopic}",
                "subsections": [subsection],
            }
            sections.append(section)

        total_words = sum(
            sum(s.get("estimated_words", 300) for s in section.get("subsections", []))
            for section in sections
        )

        return {
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "description": chapter_config.get("description", ""),
            "learning_objectives": self._generate_learning_objectives(chapter_title, subtopics),
            "sections": sections,
            "estimated_words": total_words,
        }

    def _generate_learning_objectives(self, title: str, subtopics: List[str]) -> List[str]:
        """Menghasilkan learning objectives untuk bab."""
        return [
            f"Memahami konsep dasar {title}",
            f"Mampu menjelaskan {', '.join(subtopics[:2])}",
        ]

    def generate_outline(self, task_plan: Dict[str, Any], mode: Optional[str] = None) -> Dict[str, Any]:
        """Menghasilkan outline lengkap dari task plan."""
        ebook_title = task_plan.get("ebook_title", "Untitled Ebook")
        chapters_config = task_plan.get("chapters", [])
        execution_mode = mode or task_plan.get("mode", "test")

        logger.info(f"Generating outline untuk '{ebook_title}', mode={execution_mode}")

        if execution_mode == "test":
            chapters_config = chapters_config[:1]
        elif execution_mode == "session":
            chapters_config = chapters_config[:4]

        chapter_outlines = [
            self.generate_chapter_outline(chapter_config, execution_mode)
            for chapter_config in chapters_config
        ]

        total_sections = sum(len(c.get("sections", [])) for c in chapter_outlines)
        total_subsections = sum(
            sum(len(s.get("subsections", [])) for s in c.get("sections", []))
            for c in chapter_outlines
        )
        total_words = sum(c.get("estimated_words", 0) for c in chapter_outlines)

        outline = {
            "schema_version": "1.1",
            "ebook_title": ebook_title,
            "target_audience": task_plan.get("target_audience", ""),
            "reading_level": task_plan.get("reading_level", "intermediate"),
            "mode": execution_mode,
            "total_chapters": len(chapter_outlines),
            "chapters": chapter_outlines,
            "metadata": {
                "total_chapters": len(chapter_outlines),
                "total_sections": total_sections,
                "total_subsections": total_subsections,
                "total_estimated_words": total_words,
            },
        }

        self.outline = outline
        logger.info(f"Outline generated: {len(chapter_outlines)} chapters, {total_subsections} subsections")
        return outline

    def validate_outline(self) -> tuple[bool, List[str]]:
        """Memvalidasi outline yang dihasilkan."""
        errors: List[str] = []
        if not self.outline:
            return False, ["Outline kosong"]
        if "ebook_title" not in self.outline:
            errors.append("Missing ebook_title")
        if "chapters" not in self.outline:
            errors.append("Missing chapters")
        elif not isinstance(self.outline["chapters"], list):
            errors.append("Chapters harus berupa list")
        elif len(self.outline["chapters"]) == 0:
            errors.append("Minimal harus ada 1 bab")

        for i, chapter in enumerate(self.outline.get("chapters", [])):
            if "chapter_title" not in chapter:
                errors.append(f"Bab {i + 1} missing chapter_title")
            if "sections" not in chapter:
                errors.append(f"Bab {i + 1} missing sections")
            for j, section in enumerate(chapter.get("sections", [])):
                for k, subsection in enumerate(section.get("subsections", [])):
                    required = subsection.get("required_layers", [])
                    if len(required) != 5:
                        errors.append(f"Bab {i + 1}, Section {j + 1}, Subsection {k + 1}: harus punya 5 lapisan")
        return len(errors) == 0, errors

    def save_outline(self, output_file: str = "output/outline.json") -> None:
        """Menyimpan outline ke file JSON."""
        if not self.outline:
            logger.warning("Tidak ada outline untuk disimpan - jalankan generate_outline terlebih dahulu")
            return
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.outline, f, indent=2, ensure_ascii=False)
        logger.info(f"Outline disimpan ke {output_path}")

    def execute(self, run_context: RunContext) -> Dict[str, Any]:
        """Menjalankan outline agent."""
        logger.info("OutlineAgent executing...")
        task_plan = self.load_task_plan()
        if not task_plan:
            logger.error("Tidak ada task plan tersedia - membuat outline minimal dari run context")
            task_plan = {
                "ebook_title": run_context.ebook_title or "Untitled Ebook",
                "target_audience": run_context.target_audience or "General",
                "reading_level": run_context.reading_level or "intermediate",
                "mode": run_context.mode or "test",
                "chapters": [
                    {
                        "number": 1,
                        "title": f"Bab 1 — Pengenalan {run_context.ebook_title or 'Topik'}",
                        "description": "Pengenalan konsep dasar",
                        "subtopics": ["Konsep Dasar", "Implementasi"],
                    }
                ],
            }
        outline = self.generate_outline(task_plan)
        is_valid, errors = self.validate_outline()
        if not is_valid:
            logger.warning(f"Outline validation errors: {errors}")
        self.save_outline()
        logger.info("OutlineAgent completed")
        return outline


def run_outline_agent(run_context: RunContext) -> Dict[str, Any]:
    """Fungsi convenience untuk menjalankan OutlineAgent."""
    agent = OutlineAgent()
    return agent.execute(run_context)
