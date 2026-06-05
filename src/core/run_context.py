"""
DIL Autonomous Ebook Agent - Run Context Module

Melacak execution context dan state dari ebook generation run.
Mendukung 3 format input: key-value, GitHub Issue Form Markdown, dan workflow_dispatch.
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
    Context tracker untuk ebook generation runs.
    Membaca environment variables dan parse berbagai format input.
    """
    
    def __init__(self):
        """Initialize RunContext dengan environment variables dan default state."""
        # GitHub Actions environment variables
        self.run_id: str = os.environ.get("GITHUB_RUN_ID", "local_run")
        self.issue_number: Optional[str] = os.environ.get("GITHUB_ISSUE_NUMBER")
        self.issue_title: str = os.environ.get("GITHUB_ISSUE_TITLE", "")
        self.issue_body: str = os.environ.get("GITHUB_ISSUE_BODY", "")
        
        # Timestamps
        self.timestamp_start: str = datetime.now().isoformat()
        self.timestamp_end: Optional[str] = None
        
        # Execution mode
        self.mode: str = "test"
        
        # Ebook metadata
        self.ebook_title: str = ""
        self.target_audience: str = ""
        self.reading_level: str = "intermediate"
        self.total_chapters: int = 0
        self.content_brief: str = ""
        
        # New fields
        self.special_instructions: str = ""
        self.target_pages: int = 0
        self.session_number: int = 0
        
        # API preferences
        self.api_preference: str = ""
        self.selected_provider: Optional[str] = None
        
        # PDF flag
        self.pdf_required: bool = False
        
        # Approval flag
        self.approval_given: bool = False
        
        # Fallback tracking
        self.fallback_used: bool = False
        self.fallback_reason: str = ""
        
        # Usage tracking
        self.total_tokens_used: int = 0
        self.total_usd_spent: float = 0.0
        
        # Agent execution tracking
        self.agents_executed: int = 0
        self.agents_failed: int = 0
        self._failed_agents: List[str] = []
        
        # Check for workflow_dispatch inputs first
        self._parse_workflow_dispatch_inputs()
        
        # Parse issue body if available
        if self.issue_body and not self.ebook_title:
            self._parse_issue_body()
        
        logger.info(f"RunContext initialized: mode={self.mode}, title={self.ebook_title[:50] if self.ebook_title else 'untitled'}")
    
    def _parse_workflow_dispatch_inputs(self) -> None:
        """Parse workflow_dispatch inputs dari environment."""
        # Check INPUT_MODE first (from workflow_dispatch)
        input_mode = os.environ.get("INPUT_MODE", "")
        if input_mode:
            self.mode = input_mode.lower()
        
        # Check for manual inputs from workflow_dispatch
        input_title = os.environ.get("INPUT_EBOOK_TITLE", "")
        if input_title:
            self.ebook_title = input_title
        
        input_target = os.environ.get("INPUT_TARGET_AUDIENCE", "")
        if input_target:
            self.target_audience = input_target
        
        input_level = os.environ.get("INPUT_READING_LEVEL", "")
        if input_level:
            self.reading_level = input_level.lower()
        
        input_chapters = os.environ.get("INPUT_TOTAL_CHAPTERS", "")
        if input_chapters:
            try:
                self.total_chapters = int(input_chapters)
            except ValueError:
                pass
        
        input_brief = os.environ.get("INPUT_CONTENT_BRIEF", "")
        if input_brief:
            self.content_brief = input_brief
        
        input_api_pref = os.environ.get("INPUT_API_PREFERENCE", "")
        if input_api_pref:
            self.api_preference = input_api_pref
        
        input_approval = os.environ.get("INPUT_APPROVAL", "")
        if input_approval:
            self.approval_given = input_approval.lower() in ["true", "1", "yes"]
        
        input_special = os.environ.get("INPUT_SPECIAL_INSTRUCTIONS", "")
        if input_special:
            self.special_instructions = input_special
        
        input_pages = os.environ.get("INPUT_TARGET_PAGES", "")
        if input_pages:
            try:
                self.target_pages = int(input_pages)
            except ValueError:
                pass
        
        input_session = os.environ.get("INPUT_SESSION_NUMBER", "")
        if input_session:
            try:
                self.session_number = int(input_session)
            except ValueError:
                pass
        
        if input_mode or input_title:
            logger.info("Parsed workflow_dispatch inputs")
    
    def _parse_issue_body(self) -> None:
        """
        Parse issue body dari 3 format:
        1. Key-value format: Judul Ebook: ...
        2. GitHub Issue Form Markdown: ### Judul Ebook
        3. Mix format
        """
        if not self.issue_body:
            logger.debug("No issue body to parse")
            return
        
        lines = self.issue_body.split('\n')
        
        i = 0
        current_key = ""
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Format 2: GitHub Issue Form Markdown (### Judul Ebook)
            if line.startswith('### '):
                current_key = line[4:].strip().lower().replace(' ', '_')
                # Move to next line to get the value
                i += 1
                if i < len(lines):
                    value_line = lines[i].strip()
                    # Skip checkbox and dropdown lines
                    while i < len(lines) and (value_line.startswith('-') or value_line.startswith('[') or not value_line):
                        i += 1
                        if i < len(lines):
                            value_line = lines[i].strip()
                    
                    if value_line and not value_line.startswith('#') and not value_line.startswith('---'):
                        self._set_field(current_key, value_line)
                i += 1
                continue
            
            # Format 1: Key-value format (Judul Ebook: value)
            if ':' in line:
                # Handle both : and ： (full-width colon)
                if '：' in line:
                    parts = line.split('：', 1)
                else:
                    parts = line.split(':', 1)
                
                key = parts[0].strip().lower().replace(' ', '_')
                value = parts[1].strip() if len(parts) > 1 else ""
                
                self._set_field(key, value)
            
            i += 1
        
        logger.debug(f"Parsed issue body: mode={self.mode}, title={self.ebook_title[:30] if self.ebook_title else 'untitled'}")
    
    def _set_field(self, key: str, value: str) -> None:
        """Set field berdasarkan key name."""
        key_lower = key.lower()
        
        # Map key variations
        if key_lower in ['ebook_title', 'title', 'judul', 'nama_ebook']:
            self.ebook_title = value
        elif key_lower in ['target_audience', 'target_pembaca', 'pembaca']:
            self.target_audience = value
        elif key_lower in ['reading_level', 'level', 'level_pembaca']:
            self.reading_level = value.lower()
        elif key_lower in ['mode', 'mode_produksi', 'production_mode']:
            self.mode = value.lower()
        elif key_lower in ['total_chapters', 'chapters', 'jumlah_bab', 'bab']:
            try:
                self.total_chapters = int(value)
            except ValueError:
                pass
        elif key_lower in ['content_brief', 'brief', 'deskripsi']:
            self.content_brief = value
        elif key_lower in ['api_preference', 'api_provider', 'provider']:
            self.api_preference = value.lower()
        elif key_lower in ['pdf_required', 'pdf']:
            self.pdf_required = value.lower() in ['true', 'yes', '1', 'ya']
        elif key_lower in ['approval', 'approved', 'approval_given']:
            self.approval_given = value.lower() in ['true', 'yes', '1', 'ya']
        elif key_lower in ['special_instructions', 'aturan_khusus', 'instruksi']:
            self.special_instructions = value
        elif key_lower in ['target_pages', 'halaman', 'pages']:
            try:
                self.target_pages = int(value)
            except ValueError:
                pass
        elif key_lower in ['session_number', 'session', 'nomor_sesi']:
            try:
                self.session_number = int(value)
            except ValueError:
                pass
    
    def mark_agent_done(self, agent_name: str) -> None:
        """Mark agent sebagai successfully completed."""
        self.agents_executed += 1
        logger.info(f"Agent completed: {agent_name} ({self.agents_executed} total)")
    
    def mark_agent_failed(self, agent_name: str) -> None:
        """Mark agent sebagai failed."""
        self.agents_failed += 1
        self._failed_agents.append(agent_name)
        logger.error(f"Agent failed: {agent_name} ({self.agents_failed} total)")
    
    def add_cost(self, tokens: int, cost_usd: float) -> None:
        """Add token usage dan cost ke running total."""
        self.total_tokens_used += tokens
        self.total_usd_spent += cost_usd
        logger.debug(f"Added cost: {tokens} tokens, ${cost_usd:.6f}")
    
    def set_fallback(self, reason: str) -> None:
        """Set fallback info."""
        self.fallback_used = True
        self.fallback_reason = reason
        logger.info(f"Fallback set: {reason}")
    
    def finalize(self) -> None:
        """Mark run sebagai finalized dengan end timestamp."""
        self.timestamp_end = datetime.now().isoformat()
        logger.info(f"Run finalized: tokens={self.total_tokens_used}, cost=${self.total_usd_spent:.6f}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert RunContext ke dictionary untuk JSON serialization."""
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
            "special_instructions": self.special_instructions,
            "target_pages": self.target_pages,
            "session_number": self.session_number,
            "api_preference": self.api_preference,
            "pdf_required": self.pdf_required,
            "approval_given": self.approval_given,
            "selected_provider": self.selected_provider,
            "total_tokens_used": self.total_tokens_used,
            "total_usd_spent": round(self.total_usd_spent, 6),
            "agents_executed": self.agents_executed,
            "agents_failed": self.agents_failed,
            "failed_agents": self._failed_agents,
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason
        }
    
    def save_to_file(self, filepath: str) -> None:
        """Save run context ke JSON file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"RunContext saved to {filepath}")


def create_run_context_from_issue() -> RunContext:
    """Create RunContext dari GitHub issue environment."""
    return RunContext()