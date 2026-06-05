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
        
        # Parse issue body if available and no inputs from dispatch
        if self.issue_body and not self.ebook_title:
            self._parse_issue_body()
        
        logger.info(f"RunContext initialized: mode={self.mode}, title={self.ebook_title[:50] if self.ebook_title else 'untitled'}")
    
    def _parse_workflow_dispatch_inputs(self) -> None:
        """Parse workflow_dispatch inputs dari environment."""
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
            self.approval_given = input_approval.lower() in ["true", "1", "yes", "checked"]
        
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
        
        input_pdf = os.environ.get("INPUT_PDF_REQUIRED", "")
        if input_pdf:
            self.pdf_required = input_pdf.lower() in ["true", "1", "yes", "checked"]
        
        if input_mode or input_title:
            logger.info("Parsed workflow_dispatch inputs")
    
    def _parse_issue_body(self) -> None:
        """
        Parse issue body dari 3 format:
        1. Key-value format: Judul Ebook: ...
        2. GitHub Issue Form Markdown: ### Judul Ebook ...
        3. Mix format
        """
        if not self.issue_body:
            logger.debug("No issue body to parse")
            return
        
        lines = self.issue_body.split('\n')
        
        i = 0
        current_key = ""
        current_value_lines = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                i += 1
                continue
            
            # Format: GitHub Issue Form Markdown (### Judul Ebook)
            if line.startswith('### '):
                # Save previous field if exists
                if current_key and current_value_lines:
                    value = '\n'.join(current_value_lines).strip()
                    self._set_field(current_key, value)
                    current_value_lines = []
                
                # Extract key from "### Judul Ebook"
                current_key = line[4:].strip().lower().replace(' ', '_')
                i += 1
                
                # Collect value lines until next heading or separator
                while i < len(lines):
                    next_line = lines[i].strip()
                    
                    # Stop at next heading
                    if next_line.startswith('### '):
                        break
                    
                    # Stop at separator
                    if next_line == '---' or next_line.startswith('---'):
                        break
                    
                    # Skip checkbox, dropdown options, and empty markers
                    if next_line.startswith('- [ ]') or next_line.startswith('- [x]'):
                        i += 1
                        continue
                    
                    if next_line.startswith('- '):
                        # Check if it's a dropdown option (single line with dash)
                        # These are just options, not the actual value
                        if i + 1 < len(lines):
                            next_next = lines[i + 1].strip() if i + 1 < len(lines) else ""
                            # If next line is also a dropdown, skip these
                            if next_next.startswith('- '):
                                i += 1
                                continue
                        # If it's a list item that's not an option, add it
                        if not (next_line.startswith('- [ ]') or next_line.startswith('- [x]')):
                            current_value_lines.append(next_line)
                        i += 1
                        continue
                    
                    # Add non-empty lines
                    if next_line:
                        current_value_lines.append(next_line)
                    
                    i += 1
                
                continue
            
            # Format: Key-value (Judul Ebook: value)
            if ':' in line and not line.startswith('['):
                if '：' in line:
                    parts = line.split('：', 1)
                else:
                    parts = line.split(':', 1)
                
                key = parts[0].strip().lower().replace(' ', '_')
                value = parts[1].strip() if len(parts) > 1 else ""
                
                # If value is empty and we have previous value lines, use them
                if not value and current_value_lines:
                    value = '\n'.join(current_value_lines).strip()
                    current_value_lines = []
                
                self._set_field(key, value)
            
            i += 1
        
        # Save last field
        if current_key and current_value_lines:
            value = '\n'.join(current_value_lines).strip()
            self._set_field(current_key, value)
        
        logger.debug(f"Parsed issue body: mode={self.mode}, title={self.ebook_title[:30] if self.ebook_title else 'untitled'}")
    
    def _set_field(self, key: str, value: str) -> None:
        """Set field berdasarkan key name dengan mapping lengkap."""
        key_lower = key.lower()
        
        # Mapping lengkap untuk semua variasi key
        mapping = {
            # Judul Ebook variations
            'judul_ebook': 'ebook_title',
            'ebook_title': 'ebook_title',
            'title': 'ebook_title',
            'judul': 'ebook_title',
            'nama_ebook': 'ebook_title',
            
            # Target Pembaca variations
            'target_pembaca': 'target_audience',
            'target_audience': 'target_audience',
            'pembaca': 'target_audience',
            'target': 'target_audience',
            'audience': 'target_audience',
            
            # Level Pembaca variations
            'level_pembaca': 'reading_level',
            'reading_level': 'reading_level',
            'level': 'reading_level',
            
            # Mode variations
            'mode_produksi': 'mode',
            'mode': 'mode',
            'production_mode': 'mode',
            
            # Jumlah Bab variations
            'jumlah_bab': 'total_chapters',
            'total_chapters': 'total_chapters',
            'bab': 'total_chapters',
            'chapters': 'total_chapters',
            
            # Target Halaman variations
            'target_halaman': 'target_pages',
            'target_pages': 'target_pages',
            'halaman': 'target_pages',
            'pages': 'target_pages',
            
            # Nomor Sesi variations
            'nomor_sesi': 'session_number',
            'session_number': 'session_number',
            'session': 'session_number',
            'sesi': 'session_number',
            
            # Brief Konten variations
            'brief_konten': 'content_brief',
            'content_brief': 'content_brief',
            'brief': 'content_brief',
            'deskripsi': 'content_brief',
            
            # Special Instructions variations
            'aturan_khusus': 'special_instructions',
            'special_instructions': 'special_instructions',
            'instruksi': 'special_instructions',
            'instructions': 'special_instructions',
            
            # API Preference variations
            'preferensi_api_provider': 'api_preference',
            'api_preference': 'api_preference',
            'api_provider': 'api_preference',
            'provider': 'api_preference',
            
            # PDF variations
            'pdf_diperlukan': 'pdf_required',
            'pdf_required': 'pdf_required',
            'pdf': 'pdf_required',
            
            # Approval variations
            'approval_untuk_eksekusi': 'approval_given',
            'approval_given': 'approval_given',
            'approval': 'approval_given',
            'approved': 'approval_given',
        }
        
        target_field = mapping.get(key_lower, key_lower)
        
        # Convert value if needed
        value_clean = value.strip()
        
        # Handle boolean fields
        if target_field in ['pdf_required', 'approval_given']:
            value_clean = value_clean.lower()
            bool_true = ['true', 'yes', 'ya', '1', 'checked', 'y', 't', 'on']
            if target_field == 'pdf_required':
                self.pdf_required = value_clean in bool_true
            elif target_field == 'approval_given':
                self.approval_given = value_clean in bool_true
            return
        
        # Handle integer fields
        if target_field in ['total_chapters', 'target_pages', 'session_number']:
            try:
                int_val = int(value_clean)
                if target_field == 'total_chapters':
                    self.total_chapters = int_val
                elif target_field == 'target_pages':
                    self.target_pages = int_val
                elif target_field == 'session_number':
                    self.session_number = int_val
            except ValueError:
                pass
            return
        
        # Handle string fields
        if target_field == 'mode':
            self.mode = value_clean.lower()
        elif target_field == 'ebook_title':
            self.ebook_title = value_clean
        elif target_field == 'target_audience':
            self.target_audience = value_clean
        elif target_field == 'reading_level':
            self.reading_level = value_clean.lower()
        elif target_field == 'content_brief':
            self.content_brief = value_clean
        elif target_field == 'special_instructions':
            self.special_instructions = value_clean
        elif target_field == 'api_preference':
            self.api_preference = value_clean.lower()
    
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