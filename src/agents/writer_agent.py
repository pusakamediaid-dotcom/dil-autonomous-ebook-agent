"""
DIL Autonomous Ebook Agent - Writer Agent

Generates ebook content based on outline.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger
from core.run_context import RunContext

logger = get_logger(__name__)


class WriterAgent:
    """
    Agent that writes ebook content based on outline structure.
    Each subsection contains: [KONSEP], [ANALOGI], [RUMUS], [CONTOH], [APLIKASI]
    """
    
    def __init__(self):
        """Initialize WriterAgent."""
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.outline: Dict[str, Any] = {}
        self.content: List[str] = []
        self.words_written: int = 0
    
    def load_outline(self, outline_file: str = "output/outline.json") -> Dict[str, Any]:
        """
        Load outline from file.
        
        Args:
            outline_file: Path to outline JSON.
        
        Returns:
            Outline dictionary.
        """
        outline_path = Path(outline_file)
        
        try:
            with open(outline_path, 'r', encoding='utf-8') as f:
                outline = json.load(f)
                logger.info(f"Loaded outline from {outline_path}")
                self.outline = outline
                return outline
        except FileNotFoundError:
            logger.warning(f"Outline not found: {outline_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing outline: {e}")
            return {}
    
    def sanitize_title(self, title: str) -> str:
        """
        Sanitize title for markdown heading.
        
        Args:
            title: Raw title string.
        
        Returns:
            Sanitized title.
        """
        # Remove excessive whitespace
        title = ' '.join(title.split())
        return title
    
    def write_section_header(self, title: str, level: int = 2) -> str:
        """
        Write a markdown section header.
        
        Args:
            title: Section title.
            level: Heading level (1-6).
        
        Returns:
            Markdown heading string.
        """
        return f"{'#' * level} {self.sanitize_title(title)}\n\n"
    
    def write_subsection_content(
        self,
        subsection: Dict[str, Any],
        chapter_num: int,
        section_num: int,
        subsection_num: int
    ) -> str:
        """
        Write content for a single subsection.
        
        Each subsection contains:
        - [KONSEP] - Conceptual explanation
        - [ANALOGI] - Analogy for understanding
        - [RUMUS] - Formula or principle (if applicable)
        - [CONTOH] - Practical example
        - [APLIKASI] - Real-world application
        
        Args:
            subsection: Subsection configuration.
            chapter_num: Chapter number.
            section_num: Section number.
            subsection_num: Subsection number.
        
        Returns:
            Formatted markdown content.
        """
        title = subsection.get("title", "Subtopik")
        content_type = subsection.get("content_type", "konseptual")
        key_concepts = subsection.get("key_concepts", [])
        
        lines = []
        
        # Subsection header
        lines.append(f"## {subsection_num}. {title}\n")
        
        # [KONSEP] section
        lines.append("### [KONSEP]\n")
        concept_text = self._generate_concept(title, content_type, key_concepts)
        lines.append(f"{concept_text}\n")
        
        # [ANALOGI] section
        lines.append("### [ANALOGI]\n")
        analogy_text = self._generate_analogy(title)
        lines.append(f"{analogy_text}\n")
        
        # [RUMUS] section (if applicable)
        if content_type in ["praktikal", "teknis"]:
            lines.append("### [RUMUS]\n")
            lines.append("```\n")
            lines.append(f"Prinsip: {title}\n")
            lines.append("```\n\n")
        
        # [CONTOH] section
        lines.append("### [CONTOH]\n")
        example_text = self._generate_example(title, chapter_num)
        lines.append(f"{example_text}\n")
        
        # [APLIKASI] section
        lines.append("### [APLIKASI]\n")
        application_text = self._generate_application(title, key_concepts)
        lines.append(f"{application_text}\n")
        
        lines.append("---\n\n")
        
        content = ''.join(lines)
        self.words_written += len(content.split())
        
        return content
    
    def _generate_concept(
        self,
        title: str,
        content_type: str,
        key_concepts: List[str]
    ) -> str:
        """
        Generate [KONSEP] content.
        
        Args:
            title: Subsection title.
            content_type: Content type.
            key_concepts: Key concepts to cover.
        
        Returns:
            Generated concept text.
        """
        # Simple template-based generation for MVP
        concept = f"""Dalam konteks **{title}**, kita perlu memahami beberapa hal fundamental:

1. **Definisi**: {title} merujuk pada konsep yang penting dalam pemahaman topik ini.
2. **Prinsip Dasar**: Konsep ini建立在 beberapa prinsip utama yang saling terkait.
3. **Konteks Penggunaan**: {title} применяется dalam berbagai scenario praktis.

Konsep-konsep kunci yang perlu dipahami:
"""
        
        for concept in key_concepts[:5]:
            concept += f"\n- {concept.capitalize()}"
        
        return concept
    
    def _generate_analogy(self, title: str) -> str:
        """
        Generate [ANALOGI] content.
        
        Args:
            title: Subsection title.
        
        Returns:
            Generated analogy text.
        """
        return f"""Bayangkan {title} seperti membangun rumah:

- **Fondasi** = Pemahaman dasar yang kuat
- **Tiang** = Konsep-konsep penopang utama
- **Atap** = Hasil akhir yang melindungi

Dengan memahami analogi ini, kita bisa melihat bagaimana {title} berfungsi secara keseluruhan. seperti bagian-bagian rumah yang bekerja sama untuk menciptakan struktur yang kokoh."""
    
    def _generate_example(self, title: str, chapter_num: int) -> str:
        """
        Generate [CONTOH] content.
        
        Args:
            title: Subsection title.
            chapter_num: Chapter number.
        
        Returns:
            Generated example text.
        """
        return f"""**Contoh Praktis {title}:**

Misalnya, dalam proyek pengembangan ebook ini, kita bisa melihat implementasi dari {title}:

```
Langkah 1: Identifikasi kebutuhan
Langkah 2: Susun struktur
Langkah 3: Implementasi bertahap
Langkah 4: Review dan evaluasi
```

Contoh ini menunjukkan bagaimana {title} diterapkan dalam workflow nyata untuk menghasilkan hasil yang optimal."""
    
    def _generate_application(
        self,
        title: str,
        key_concepts: List[str]
    ) -> str:
        """
        Generate [APLIKASI] content.
        
        Args:
            title: Subsection title.
            key_concepts: Key concepts.
        
        Returns:
            Generated application text.
        """
        applications = []
        
        for concept in key_concepts[:3]:
            applications.append(f"- **{concept.capitalize()}**: Digunakan dalam scenario nyata untuk peningkatan pemahaman")
        
        return f"""**Penerapan dalam Kehidupan Nyata:**

{chr(10).join(applications)}

Dengan memahami aplikasi praktis dari {title}, kita dapat mengaplikasikan pengetahuan ini dalam berbagai konteks dan situasi."""
    
    def write_chapter(self, chapter: Dict[str, Any], mode: str = "test") -> str:
        """
        Write complete chapter content.
        
        Args:
            chapter: Chapter configuration.
            mode: Execution mode.
        
        Returns:
            Chapter markdown content.
        """
        lines = []
        
        # Chapter header
        chapter_num = chapter.get("number", 1)
        chapter_title = chapter.get("title", f"Chapter {chapter_num}")
        description = chapter.get("description", "")
        
        lines.append(f"# Chapter {chapter_num}: {chapter_title}\n\n")
        
        if description:
            lines.append(f"> *{description}*\n\n")
        
        # Sections
        sections = chapter.get("sections", [])
        total_subsections = 0
        
        for section_idx, section in enumerate(sections, 1):
            section_title = section.get("title", f"Section {section_idx}")
            
            lines.append(f"## {section_idx}. {section_title}\n\n")
            
            if "description" in section:
                lines.append(f"_{section.get('description')}_\n\n")
            
            # Subsections
            subsections = section.get("subsections", [])
            
            for subsection_idx, subsection in enumerate(subsections, 1):
                global_idx = total_subsections + subsection_idx
                content = self.write_subsection_content(
                    subsection,
                    chapter_num,
                    section_idx,
                    global_idx
                )
                lines.append(content)
            
            total_subsections += len(subsections)
        
        return ''.join(lines)
    
    def write_ebook(self, run_context: RunContext) -> str:
        """
        Write complete ebook content.
        
        Args:
            run_context: Current run context.
        
        Returns:
            Complete ebook markdown content.
        """
        chapters = self.outline.get("chapters", [])
        mode = run_context.mode
        
        lines = []
        
        # Title page
        lines.append(f"# {self.outline.get('ebook_title', 'Untitled Ebook')}\n\n")
        lines.append(f"**Target Audience:** {run_context.target_audience}\n\n")
        lines.append(f"**Reading Level:** {run_context.reading_level}\n\n")
        lines.append(f"**Generated:** {run_context.timestamp_start}\n\n")
        lines.append("---\n\n")
        
        # Table of contents (simple)
        lines.append("# Table of Contents\n\n")
        for i, chapter in enumerate(chapters, 1):
            lines.append(f"{i}. [{chapter.get('title', f'Chapter {i}')}](#chapter-{i})\n")
        lines.append("\n---\n\n")
        
        # Chapters
        for chapter in chapters:
            chapter_content = self.write_chapter(chapter, mode)
            lines.append(chapter_content)
        
        # Summary/Conclusion
        lines.append("# Ringkasan\n\n")
        lines.append("Dalam ebook ini, kita telah membahas konsep-konsep penting ")
        lines.append("yang diperlukan untuk memahami topik secara komprehensif.\n\n")
        
        return ''.join(lines)
    
    def save_ebook(self, output_file: str = "output/ebook.md") -> None:
        """
        Save ebook content to markdown file.
        
        Args:
            output_file: Output file path.
        """
        if not self.content:
            logger.warning("No content to save - run write_ebook first")
            return
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        content_str = ''.join(self.content) if isinstance(self.content, list) else self.content
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content_str)
        
        logger.info(f"Ebook saved to {output_path} ({self.words_written} words)")
    
    def execute(self, run_context: RunContext) -> str:
        """
        Execute writer agent.
        
        Args:
            run_context: Current run context.
        
        Returns:
            Ebook content string.
        """
        logger.info("WriterAgent executing...")
        
        # Load outline
        outline = self.load_outline()
        
        if not outline:
            logger.error("No outline available - cannot write ebook")
            return ""
        
        # Write ebook
        content = self.write_ebook(run_context)
        self.content = content
        
        # Save
        self.save_ebook()
        
        logger.info(f"WriterAgent completed - wrote {self.words_written} words")
        
        return content


def run_writer_agent(run_context: RunContext) -> str:
    """
    Convenience function to run WriterAgent.
    
    Args:
        run_context: Current run context.
    
    Returns:
        Ebook content string.
    """
    agent = WriterAgent()
    return agent.execute(run_context)