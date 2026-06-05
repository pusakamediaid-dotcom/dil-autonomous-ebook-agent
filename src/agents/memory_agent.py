"""
DIL Autonomous Ebook Agent - Memory Agent

Loads project documentation and context for agent execution.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger
from core.run_context import RunContext

logger = get_logger(__name__)


class MemoryAgent:
    """
    Agent that loads project documentation and context.
    Reads docs and memory files to build context for other agents.
    """
    
    def __init__(self, docs_dir: str = "docs", memory_dir: str = "memory"):
        """
        Initialize MemoryAgent.
        
        Args:
            docs_dir: Path to docs directory.
            memory_dir: Path to memory directory.
        """
        self.docs_dir = Path(docs_dir)
        self.memory_dir = Path(memory_dir)
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.docs_loaded: Dict[str, str] = {}
        self.memory_loaded: Dict[str, str] = {}
        self.context: Dict[str, Any] = {}
    
    def load_doc(self, filename: str) -> Optional[str]:
        """
        Load a documentation file.
        
        Args:
            filename: Name of the doc file.
        
        Returns:
            File content or None if not found.
        """
        filepath = self.docs_dir / filename
        
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.docs_loaded[filename] = content
                    logger.info(f"Loaded doc: {filename} ({len(content)} chars)")
                    return content
            else:
                logger.warning(f"Doc file not found: {filepath}")
                return None
        except Exception as e:
            logger.error(f"Error loading doc {filename}: {e}")
            return None
    
    def load_memory(self, filename: str) -> Optional[str]:
        """
        Load a memory file.
        
        Args:
            filename: Name of the memory file.
        
        Returns:
            File content or None if not found.
        """
        filepath = self.memory_dir / filename
        
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.memory_loaded[filename] = content
                    logger.info(f"Loaded memory: {filename} ({len(content)} chars)")
                    return content
            else:
                logger.debug(f"Memory file not found (will create): {filepath}")
                return None
        except Exception as e:
            logger.error(f"Error loading memory {filename}: {e}")
            return None
    
    def build_context(self, run_context: RunContext) -> Dict[str, Any]:
        """
        Build context from all loaded documents and memory.
        
        Args:
            run_context: Current run context.
        
        Returns:
            Context dictionary.
        """
        context = {
            "run_id": run_context.run_id,
            "ebook_title": run_context.ebook_title,
            "target_audience": run_context.target_audience,
            "reading_level": run_context.reading_level,
            "mode": run_context.mode,
            "docs": {},
            "memory": {},
            "style_rules": [],
            "terminology": {},
            "safety_rules": [],
            "decision_history": [],
            "error_history": []
        }
        
        # Load PROJECT_BIBLE
        bible = self.load_doc("PROJECT_BIBLE.md")
        if bible:
            context["docs"]["PROJECT_BIBLE"] = bible[:2000]  # First 2000 chars for context
        
        # Load STYLE_GUIDE
        style_guide = self.load_doc("STYLE_GUIDE.md")
        if style_guide:
            context["docs"]["STYLE_GUIDE"] = style_guide[:2000]
            # Extract key style rules
            context["style_rules"] = self._extract_style_rules(style_guide)
        
        # Load TERMINOLOGY_RULES
        terminology = self.load_doc("TERMINOLOGY_RULES.md")
        if terminology:
            context["docs"]["TERMINOLOGY_RULES"] = terminology[:2000]
            context["terminology"] = self._parse_terminology(terminology)
        
        # Load SAFETY_RULES
        safety = self.load_doc("SAFETY_RULES.md")
        if safety:
            context["docs"]["SAFETY_RULES"] = safety[:2000]
            context["safety_rules"] = self._extract_safety_rules(safety)
        
        # Load DECISION_LOG
        decision_log = self.load_memory("DECISION_LOG.md")
        if decision_log:
            context["memory"]["DECISION_LOG"] = decision_log[:1000]
            context["decision_history"] = self._parse_decision_log(decision_log)
        
        # Load ERROR_HISTORY
        error_history = self.load_memory("ERROR_HISTORY.md")
        if error_history:
            context["memory"]["ERROR_HISTORY"] = error_history[:1000]
            context["error_history"] = self._parse_error_history(error_history)
        
        self.context = context
        logger.info(f"Context built with {len(self.docs_loaded)} docs, {len(self.memory_loaded)} memory files")
        
        return context
    
    def _extract_style_rules(self, content: str) -> List[str]:
        """Extract key style rules from style guide."""
        rules = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('*'):
                rules.append(line.lstrip('-* '))
        
        return rules[:10]  # Return first 10 rules
    
    def _parse_terminology(self, content: str) -> Dict[str, str]:
        """Parse terminology rules into key-value pairs."""
        terminology = {}
        lines = content.split('\n')
        
        for line in lines:
            if '→' in line or '->' in line:
                parts = line.replace('→', '->').split('->')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    terminology[key] = value
        
        return terminology
    
    def _extract_safety_rules(self, content: str) -> List[str]:
        """Extract safety rules from safety document."""
        rules = []
        lines = content.split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith('#'):
                if any(keyword in line.lower() for keyword in ['harus', 'must', 'jangan', 'never', '禁止']):
                    rules.append(line.strip())
        
        return rules[:10]  # Return first 10 rules
    
    def _parse_decision_log(self, content: str) -> List[Dict[str, str]]:
        """Parse decision log into structured entries."""
        entries = []
        lines = content.split('\n')
        
        for line in lines:
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    entries.append({
                        "date": parts[0],
                        "decision": parts[1],
                        "reason": parts[2] if len(parts) > 2 else ""
                    })
        
        return entries[-5:]  # Return last 5 entries
    
    def _parse_error_history(self, content: str) -> List[Dict[str, str]]:
        """Parse error history into structured entries."""
        entries = []
        lines = content.split('\n')
        
        for line in lines:
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    entries.append({
                        "date": parts[0],
                        "error": parts[1],
                        "solution": parts[2] if len(parts) > 2 else ""
                    })
        
        return entries[-5:]  # Return last 5 entries
    
    def save_context(self, output_file: str = "output/memory_context.json") -> None:
        """
        Save context to JSON file.
        
        Args:
            output_file: Output file path.
        """
        if not self.context:
            logger.warning("No context to save - run build_context first")
            return
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.context, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Memory context saved to {output_path}")
    
    def execute(self, run_context: RunContext) -> Dict[str, Any]:
        """
        Execute memory agent - load docs, build context, save.
        
        Args:
            run_context: Current run context.
        
        Returns:
            Context dictionary.
        """
        logger.info("MemoryAgent executing...")
        
        context = self.build_context(run_context)
        self.save_context()
        
        logger.info(f"MemoryAgent completed - loaded {len(self.docs_loaded)} docs, {len(self.memory_loaded)} memory files")
        
        return context


def run_memory_agent(run_context: RunContext) -> Dict[str, Any]:
    """
    Convenience function to run MemoryAgent.
    
    Args:
        run_context: Current run context.
    
    Returns:
        Context dictionary.
    """
    agent = MemoryAgent()
    return agent.execute(run_context)