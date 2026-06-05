"""
DIL Autonomous Ebook Agent - Report Builder Module

Builds and saves execution and cost reports.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .logger import get_logger

logger = get_logger(__name__)


class ReportBuilder:
    """
    Builds execution and cost reports for ebook generation runs.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize ReportBuilder.
        
        Args:
            output_dir: Path to output directory.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def build_run_report(
        self,
        run_context: Any,
        agents_executed: List[str],
        agents_failed: List[str],
        output_files: List[str]
    ) -> Dict[str, Any]:
        """
        Build execution run report.
        
        Args:
            run_context: RunContext instance.
            agents_executed: List of executed agent names.
            agents_failed: List of failed agent names.
            output_files: List of output file paths.
        
        Returns:
            Run report dictionary.
        """
        report = {
            "report_type": "run_report",
            "generated_at": datetime.now().isoformat(),
            "run_id": run_context.run_id,
            "issue_number": run_context.issue_number,
            "issue_title": run_context.issue_title,
            "status": "completed" if len(agents_failed) == 0 else "completed_with_errors",
            "mode": run_context.mode,
            "ebook": {
                "title": run_context.ebook_title,
                "target_audience": run_context.target_audience,
                "reading_level": run_context.reading_level,
                "total_chapters": run_context.total_chapters,
                "brief": run_context.content_brief
            },
            "execution": {
                "timestamp_start": run_context.timestamp_start,
                "timestamp_end": run_context.timestamp_end,
                "agents_executed": agents_executed,
                "agents_failed": agents_failed,
                "total_agents": len(agents_executed),
                "failed_count": len(agents_failed)
            },
            "provider": {
                "preference": run_context.api_preference,
                "selected": run_context.selected_provider
            },
            "output_files": output_files,
            "summary": {
                "total_tokens_used": run_context.total_tokens_used,
                "total_cost_usd": round(run_context.total_usd_spent, 6),
                "success": len(agents_failed) == 0
            }
        }
        
        logger.info(f"Built run report for run {run_context.run_id}")
        
        return report
    
    def build_cost_report(
        self,
        cost_guard: Any,
        provider_usage: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build cost analysis report.
        
        Args:
            cost_guard: CostGuard instance.
            provider_usage: Optional per-provider usage breakdown.
        
        Returns:
            Cost report dictionary.
        """
        report = {
            "report_type": "cost_report",
            "generated_at": datetime.now().isoformat(),
            "total_tokens": cost_guard.total_tokens,
            "total_cost_usd": round(cost_guard.total_cost, 6),
            "limits": {
                "max_tokens_per_run": cost_guard.max_tokens_per_run,
                "max_cost_per_run": cost_guard.max_cost_per_run
            },
            "remaining": {
                "tokens_remaining": cost_guard.max_tokens_per_run - cost_guard.total_tokens,
                "cost_remaining": round(
                    cost_guard.max_cost_per_run - cost_guard.total_cost,
                    6
                )
            },
            "utilization": {
                "token_usage_percent": round(
                    (cost_guard.total_tokens / cost_guard.max_tokens_per_run) * 100,
                    2
                ) if cost_guard.max_tokens_per_run > 0 else 0,
                "cost_usage_percent": round(
                    (cost_guard.total_cost / cost_guard.max_cost_per_run) * 100,
                    2
                ) if cost_guard.max_cost_per_run > 0 else 0
            },
            "requests": cost_guard.requests
        }
        
        if provider_usage:
            report["provider_breakdown"] = provider_usage
        
        logger.info(
            f"Built cost report: {cost_guard.total_tokens} tokens, "
            f"${cost_guard.total_cost:.6f}"
        )
        
        return report
    
    def save_run_report(self, report: Dict[str, Any], filepath: str = "run_report.json") -> None:
        """
        Save run report to JSON file.
        
        Args:
            report: Report dictionary.
            filepath: Output filename.
        """
        output_path = self.output_dir / filepath
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Run report saved to {output_path}")
    
    def save_cost_report(self, report: Dict[str, Any], filepath: str = "cost_report.json") -> None:
        """
        Save cost report to JSON file.
        
        Args:
            report: Report dictionary.
            filepath: Output filename.
        """
        output_path = self.output_dir / filepath
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Cost report saved to {output_path}")
    
    def save_artifact_list(self, files: List[str]) -> None:
        """
        Save list of generated artifacts.
        
        Args:
            files: List of artifact file paths.
        """
        artifact_path = self.output_dir / "artifacts_manifest.json"
        
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "artifacts": [
                {
                    "path": str(Path(f).name),
                    "full_path": str(f),
                    "exists": Path(f).exists()
                }
                for f in files
            ]
        }
        
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Artifact manifest saved to {artifact_path}")


def get_report_builder() -> ReportBuilder:
    """Get or create global ReportBuilder instance."""
    global _global_report_builder
    if '_global_report_builder' not in globals():
        _global_report_builder = ReportBuilder()
    return _global_report_builder