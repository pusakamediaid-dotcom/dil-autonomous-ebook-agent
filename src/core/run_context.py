"""
DIL Autonomous Ebook Agent - Run Context Module

Melacak execution context dan state dari ebook generation run.
Mendukung workflow_dispatch, key-value, dan GitHub Issue Form Markdown.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from .logger import get_logger

logger = get_logger(__name__)


class RunContext:
    """Context tracker untuk ebook generation runs."""

    def __init__(self):
        """Initialize RunContext dengan environment variables dan default state."""
        self.run_id: str = os.environ.get("GITHUB_RUN_ID", "local_run")
        self.issue_number: Optional[str] = os.environ.get("GITHUB_ISSUE_NUMBER")
        self.issue_title: str = os.environ.get("GITHUB_ISSUE_TITLE", "")
        self.issue_body: str = os.environ.get("GITHUB_ISSUE_BODY", "")

        self.timestamp_start: str = datetime.now().isoformat()
        self.timestamp_end: Optional[str] = None

        self.mode: str = "test"
        self.ebook_title: str = ""
        self.target_audience: str = ""
        self.reading_level: str = "intermediate"
        self.total_chapters: int = 0
        self.content_brief: str = ""
        self.special_instructions: str = ""
        self.target_pages: int = 0
        self.session_number: int = 0
        self.api_preference: str = "auto"
        self.selected_provider: Optional[str] = None
        self.pdf_required: bool = False
        self.approval_given: bool = False
        self.fallback_used: bool = False
        self.fallback_reason: str = ""
        self.total_tokens_used: int = 0
        self.total_usd_spent: float = 0.0
        self.agents_executed: int = 0
        self.agents_failed: int = 0
        self._failed_agents: List[str] = []

        self._parse_workflow_dispatch_inputs()
        if self.issue_body:
            self._parse_issue_body()

        logger.info(
            f"RunContext initialized: mode={self.mode}, "
            f"title={self.ebook_title[:50] if self.ebook_title else 'untitled'}"
        )

    def _parse_workflow_dispatch_inputs(self) -> None:
        """Parse workflow_dispatch inputs dari environment."""
        env_map = {
            "INPUT_MODE": "mode",
            "INPUT_EBOOK_TITLE": "ebook_title",
            "INPUT_TARGET_AUDIENCE": "target_audience",
            "INPUT_READING_LEVEL": "reading_level",
            "INPUT_TOTAL_CHAPTERS": "total_chapters",
            "INPUT_TARGET_PAGES": "target_pages",
            "INPUT_SESSION_NUMBER": "session_number",
            "INPUT_CONTENT_BRIEF": "content_brief",
            "INPUT_SPECIAL_INSTRUCTIONS": "special_instructions",
            "INPUT_API_PREFERENCE": "api_preference",
            "INPUT_PDF_REQUIRED": "pdf_required",
            "INPUT_APPROVAL": "approval_given",
        }
        parsed_any = False
        for env_name, field_name in env_map.items():
            value = os.environ.get(env_name, "")
            if value not in (None, ""):
                self._assign_field(field_name, str(value))
                parsed_any = True
        if parsed_any:
            logger.info("Parsed workflow_dispatch inputs")

    def _normalize_key(self, key: str) -> str:
        """Normalize field label menjadi snake_case sederhana."""
        clean = key.strip().lower()
        replacements = {
            "-": "_",
            " ": "_",
            ":": "",
            "?": "",
            "(opsional)": "",
            "apakah_": "",
        }
        for old, new in replacements.items():
            clean = clean.replace(old, new)
        while "__" in clean:
            clean = clean.replace("__", "_")
        return clean.strip("_")

    def _parse_issue_body(self) -> None:
        """Parse GitHub Issue body dari heading Markdown dan key-value."""
        lines = self.issue_body.splitlines()
        fields: Dict[str, str] = {}
        current_key: Optional[str] = None
        current_value: List[str] = []

        def flush_current() -> None:
            nonlocal current_key, current_value
            if current_key:
                value = "\n".join(current_value).strip()
                if value:
                    fields[current_key] = value
            current_key = None
            current_value = []

        for raw_line in lines:
            stripped = raw_line.strip()

            # Penting: heading issue form harus dibaca sebelum skip komentar '#'.
            if stripped.startswith("### "):
                flush_current()
                current_key = self._normalize_key(stripped[4:])
                current_value = []
                continue

            if current_key:
                if stripped == "---":
                    flush_current()
                    continue
                current_value.append(raw_line.rstrip())
                continue

            if not stripped:
                continue
            if stripped.startswith("#"):
                continue

            if ":" in stripped or "：" in stripped:
                separator = "：" if "：" in stripped else ":"
                key, value = stripped.split(separator, 1)
                fields[self._normalize_key(key)] = value.strip()

        flush_current()

        for key, value in fields.items():
            self._set_field(key, value)

        logger.info(
            f"Parsed issue body fields={len(fields)}, mode={self.mode}, "
            f"title={self.ebook_title[:30] if self.ebook_title else 'untitled'}"
        )

    def _set_field(self, key: str, value: str) -> None:
        """Set field berdasarkan label issue."""
        mapping = {
            "judul_ebook": "ebook_title",
            "ebook_title": "ebook_title",
            "title": "ebook_title",
            "judul": "ebook_title",
            "nama_ebook": "ebook_title",
            "target_pembaca": "target_audience",
            "target_audience": "target_audience",
            "pembaca": "target_audience",
            "target": "target_audience",
            "audience": "target_audience",
            "level_pembaca": "reading_level",
            "reading_level": "reading_level",
            "level": "reading_level",
            "mode_produksi": "mode",
            "production_mode": "mode",
            "mode": "mode",
            "jumlah_bab": "total_chapters",
            "total_chapters": "total_chapters",
            "bab": "total_chapters",
            "chapters": "total_chapters",
            "target_halaman": "target_pages",
            "target_jumlah_halaman": "target_pages",
            "target_pages": "target_pages",
            "halaman": "target_pages",
            "pages": "target_pages",
            "nomor_sesi": "session_number",
            "sesi_ke_berapa": "session_number",
            "session_number": "session_number",
            "session": "session_number",
            "sesi": "session_number",
            "brief_konten": "content_brief",
            "content_brief": "content_brief",
            "brief": "content_brief",
            "deskripsi": "content_brief",
            "aturan_khusus": "special_instructions",
            "special_rules": "special_instructions",
            "special_instructions": "special_instructions",
            "instruksi": "special_instructions",
            "instructions": "special_instructions",
            "preferensi_api_provider": "api_preference",
            "api_preference": "api_preference",
            "api_provider": "api_preference",
            "provider": "api_preference",
            "pdf_diperlukan": "pdf_required",
            "pdf_required": "pdf_required",
            "pdf": "pdf_required",
            "approval_untuk_eksekusi": "approval_given",
            "konfirmasi_approval": "approval_given",
            "approval_required": "approval_given",
            "approval_given": "approval_given",
            "approval": "approval_given",
            "approved": "approval_given",
        }
        target_field = mapping.get(key, key)
        self._assign_field(target_field, value)

    def _bool_value(self, value: str) -> bool:
        """Convert teks ke boolean."""
        value_clean = value.strip().lower()
        true_words = ["true", "yes", "ya", "1", "checked", "y", "t", "on", "setuju"]
        return any(word in value_clean for word in true_words)

    def _int_value(self, value: str, default: int = 0) -> int:
        """Ambil integer pertama dari teks."""
        digits = ""
        for char in value:
            if char.isdigit():
                digits += char
            elif digits:
                break
        if not digits:
            return default
        try:
            return int(digits)
        except ValueError:
            return default

    def _assign_field(self, target_field: str, value: str) -> None:
        """Assign field RunContext dengan konversi aman."""
        value_clean = str(value).strip()
        if value_clean == "":
            return

        if target_field == "mode":
            self.mode = value_clean.lower()
        elif target_field == "ebook_title":
            self.ebook_title = value_clean
        elif target_field == "target_audience":
            self.target_audience = value_clean
        elif target_field == "reading_level":
            self.reading_level = value_clean.lower()
        elif target_field == "content_brief":
            self.content_brief = value_clean
        elif target_field == "special_instructions":
            self.special_instructions = value_clean
        elif target_field == "api_preference":
            self.api_preference = value_clean.lower()
        elif target_field == "selected_provider":
            self.selected_provider = value_clean
        elif target_field == "total_chapters":
            self.total_chapters = self._int_value(value_clean, self.total_chapters)
        elif target_field == "target_pages":
            self.target_pages = self._int_value(value_clean, self.target_pages)
        elif target_field == "session_number":
            self.session_number = self._int_value(value_clean, self.session_number)
        elif target_field == "pdf_required":
            self.pdf_required = self._bool_value(value_clean)
        elif target_field == "approval_given":
            self.approval_given = self._bool_value(value_clean)

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
            "fallback_reason": self.fallback_reason,
        }

    def save_to_file(self, filepath: str) -> None:
        """Save run context ke JSON file."""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"RunContext saved to {output_path}")


def create_run_context_from_issue() -> RunContext:
    """Create RunContext dari GitHub issue environment."""
    return RunContext()
