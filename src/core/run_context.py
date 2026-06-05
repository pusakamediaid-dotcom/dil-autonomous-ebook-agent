"""
DIL Autonomous Ebook Agent - Run Context Module

Tracks the execution context and state of an ebook generation run.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from .logger import get_logger

logger = get_logger(__name__)


class RunContext:
    """
    Context tracker for ebook generation runs.
    Captures environment variables and tracks execution state.
    """
    
    def __init__(self):
        """Initialize RunContext with environment variables and default state."""
        # GitHub Actions environment variables
        self.run_id: str = os.environ.get("GITHUB_RUN_ID", "local_run")
        self.issue_number: Optional[str] = os.environ.get("GITHUB_ISSUE_NUMBER")
        self.issue_title: str = os.environ.get("GITHUB_ISSUE_TITLE", "")
        self.issue_body: str = os.environ.get("GITHUB_ISSUE_BODY", "")
        
        # Timestamps
        self.timestamp_start: str = datetime.now().isoformat()
        self.timestamp_end: Optional[str] = None
        
        # Execution mode
        self.mode: str = "test"  # Default mode
        
        # Ebook metadata
        self.ebook_title: str = ""
        self.target_audience: str = ""
        self.reading_level: str = "intermediate"
        self.total_chapters: int = 0
        self.content_brief: str = ""
        
        # API preferences
        self.api_preference: str = ""
        self.selected_provider: Optional[str] = None
        
        # PDF flag
        self.pdf_required: bool = False
        
        # Approval flag
        self.approval_given: bool = False
        
        # Usage tracking
        self.total_tokens_used: int = 0
        self.total_usd_spent: float = 0.0
        
        # Agent execution tracking
        self.agents_executed: int = 0
        self.agents_failed: int = 0
        self._failed_agents: List[str] = []
        
        # Parse issue body if available
        self._parse_issue_body()
        
        logger.info(f"RunContext initialized for run {self.run_id}")
    
    def _parse_issue_body(self) -> None:
        """Parse issue body to extract ebook parameters."""
        if not self.issue_body:
            logger.debug("No issue body to parse")
            return
        
        lines = self.issue_body.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Parse key: value pairs (handles both : and ：)
            if ':' in line:
                parts = line.split(':', 1)
            elif '：' in line:
                parts = line.split('：', 1)
            else:
                continue
            
            key = parts[0].strip().lower().replace(' ', '_')
            value = parts[1].strip() if len(parts) > 1 else ""
            
            if key in ['ebook_title', 'title', 'judul']:
                self.ebook_title = value
            elif key in ['target_audience', 'target_pembaca', 'pembaca']:
                self.target_audience = value
            elif key in ['reading_level', 'level', 'level_pembaca']:
                self.reading_level = value
            elif key in ['mode', 'mode_produksi', 'production_mode']:
                self.mode = value.lower()
            elif key in ['total_chapters', 'chapters', 'jumlah_bab', 'bab']:
                try:
                    self.total_chapters = int(value)
                except ValueError:
                    pass
            elif key in ['content_brief', 'brief', 'deskripsi']:
                self.content_brief = value
            elif key in ['api_preference', 'api_provider', 'provider']:
                self.api_preference = value
            elif key in ['pdf_required', 'pdf']:
                self.pdf_required = value.lower() in ['true', 'yes', '1', 'ya']
            elif key in ['approval', 'approved']:
                self.approval_given = value.lower() in ['true', 'yes', '1', 'ya']
        
        logger.debug(f"Parsed issue body - title: {self.ebook_title}, mode: {self.mode}")
    
    def mark_agent_done(self, agent_name: str) -> None:
        """
        Mark an agent as successfully completed.
        
        Args:
            agent_name: Name of the agent.
        """
        self.agents_executed += 1
        logger.info(f"Agent completed: {agent_name} ({self.agents_executed} total)")
    
    def mark_agent_failed(self, agent_name: str) -> None:
        """
        Mark an agent as failed.
        
        Args:
            agent_name: Name of the failed agent.
        """
        self.agents_failed += 1
        self._failed_agents.append(agent_name)
        logger.error(f"Agent failed: {agent_name} ({self.agents_failed} total)")
    
    def add_cost(self, tokens: int, cost_usd: float) -> None:
        """
        Add token usage and cost to the running total.
        
        Args:
            tokens: Number of tokens used.
            cost_usd: Cost in USD.
        """
        self.total_tokens_used += tokens
        self.total_usd_spent += cost_usd
        logger.debug(f"Added cost: {tokens} tokens, ${cost_usd:.4f}")
    
    def finalize(self) -> None:
        """Mark run as finalized with end timestamp."""
        self.timestamp_end = datetime.now().isoformat()
        logger.info(f"Run finalized - tokens: {self.total_tokens_used}, cost: ${self.total_usd_spent:.4f}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert RunContext to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the run context.
        """
        return {
            "run_id": self.run_id,
            "issue_number": self.issue_number,
            "issue_title": self.issue_title,
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
            "mode": self.mode,
            "ebook_title": self.ebook_title,
            "target_audience": self.target_audience,
            "reading_level": self.reading_level,
            "total_chapters": self.total_chapters,
            "content_brief": self.content_brief,
            "api_preference": self.api_preference,
            "pdf_required": self.pdf_required,
            "approval_given": self.approval_given,
            "selected_provider": self.selected_provider,
            "total_tokens_used": self.total_tokens_used,
            "total_usd_spent": round(self.total_usd_spent, 6),
            "agents_executed": self.agents_executed,
            "agents_failed": self.agents_failed,
            "failed_agents": self._failed_agents
        }
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save run context to JSON file.
        
        Args:
            filepath: Path to output file.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"RunContext saved to {filepath}")


def create_run_context_from_issue() -> RunContext:
    """
    Create RunContext from GitHub issue environment.
    
    Returns:
        Initialized RunContext instance.
    """
    return RunContext()