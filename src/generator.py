"""
DIL Autonomous Ebook Agent - Generator (MVP)

Entry point utama untuk workflow generasi ebook.
Mengorkestrasi semua agent dan menghasilkan output final.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.logger import get_logger
from core.run_context import create_run_context_from_issue
from core.cost_guard import CostGuard
from core.report_builder import ReportBuilder

from agents.memory_agent import run_memory_agent
from agents.task_planner_agent import run_task_planner
from agents.router_agent import run_router_agent
from agents.outline_agent import run_outline_agent
from agents.writer_agent import run_writer_agent
from agents.reviewer_agent import run_reviewer_agent
from agents.repair_agent import run_repair_agent

from validators.json_validator import validate_json_file
from validators.markdown_validator import validate_markdown_file
from validators.output_validator import validate_outputs
from validators.safety_validator import check_file_safety

logger = get_logger(__name__)


class EbookGenerator:
    """
    Generator utama yang mengorkestrasi workflow generasi ebook.
    
    Alur:
    1. Setup RunContext
    2. Run MemoryAgent
    3. Run TaskPlannerAgent
    4. If mode planning -> selesai
    5. Cek approval gate
    6. Run RouterAgent
    7. Run OutlineAgent
    8. Run WriterAgent (dengan Cost Guard)
    9. Validate ebook.md
    10. Run ReviewerAgent
    11. If status REPAIR -> Run RepairAgent
    12. Run OutputValidator
    13. Create reports
    """
    
    def __init__(self):
        """Inisialisasi EbookGenerator."""
        self.run_context = None
        self.cost_guard = None
        self.report_builder = None
        
        self.agents_executed: List[str] = []
        self.agents_failed: List[str] = []
        self.fallback_used: bool = False
        self.fallback_reason: str = ""
        self.provider_used: str = ""
        self.warnings: List[str] = []
        
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("EbookGenerator initialized")
    
    def setup(self) -> None:
        """Setup komponen generator."""
        self.run_context = create_run_context_from_issue()
        logger.info(f"RunContext created: mode={self.run_context.mode}")
        
        self.cost_guard = CostGuard()
        logger.info("CostGuard initialized")
        
        self.report_builder = ReportBuilder()
        logger.info("ReportBuilder initialized")
    
    def validate_approval_gate(self) -> bool:
        """Validasi approval untuk mode besar."""
        mode = self.run_context.mode
        
        if mode in ["planning", "test", "session", "review", "repair"]:
            return True
        
        if mode in ["full", "html", "pdf"]:
            if not self.run_context.approval_given:
                logger.error(f"Mode {mode} memerlukan approval. Pipeline berhenti.")
                self.warnings.append(f"Mode {mode} requires approval")
                return False
            return True
        
        return True
    
    def run_memory_phase(self) -> Dict[str, Any]:
        """Fase memory agent."""
        logger.info("=== MEMORY PHASE ===")
        
        try:
            context = run_memory_agent(self.run_context)
            self.agents_executed.append("memory_agent")
            self.run_context.mark_agent_done("memory_agent")
            logger.info("Memory phase completed successfully")
            return context
        except Exception as e:
            logger.error(f"Memory phase failed: {e}")
            self.agents_failed.append("memory_agent")
            self.run_context.mark_agent_failed("memory_agent")
            return {}
    
    def run_planning_phase(self) -> Dict[str, Any]:
        """Fase task planner."""
        logger.info("=== PLANNING PHASE ===")
        
        try:
            plan = run_task_planner(self.run_context)
            self.agents_executed.append("task_planner_agent")
            self.run_context.mark_agent_done("task_planner_agent")
            logger.info("Planning phase completed successfully")
            return plan
        except Exception as e:
            logger.error(f"Planning phase failed: {e}")
            self.agents_failed.append("task_planner_agent")
            self.run_context.mark_agent_failed("task_planner_agent")
            return {}
    
    def run_routing_phase(self) -> Dict[str, Any]:
        """Fase router agent."""
        logger.info("=== ROUTING PHASE ===")
        
        try:
            decision = run_router_agent(self.run_context)
            
            if decision.get("status") == "failed":
                logger.warning(f"Routing failed: {decision.get('reason')}")
                self.agents_failed.append("router_agent")
                self.run_context.mark_agent_failed("router_agent")
                self.fallback_used = True
                self.fallback_reason = "No provider available"
                self.run_context.set_fallback(self.fallback_reason)
            else:
                self.agents_executed.append("router_agent")
                self.run_context.mark_agent_done("router_agent")
                self.provider_used = decision.get("selected_provider_name", "unknown")
                logger.info(f"Routing completed: provider={self.provider_used}")
            
            return decision
        except Exception as e:
            logger.error(f"Routing phase failed: {e}")
            self.agents_failed.append("router_agent")
            self.run_context.mark_agent_failed("router_agent")
            self.fallback_used = True
            self.fallback_reason = f"Router exception: {str(e)}"
            return {"status": "failed", "reason": str(e)}
    
    def run_outline_phase(self) -> Dict[str, Any]:
        """Fase outline agent."""
        logger.info("=== OUTLINE PHASE ===")
        
        try:
            outline = run_outline_agent(self.run_context)
            self.agents_executed.append("outline_agent")
            self.run_context.mark_agent_done("outline_agent")
            logger.info("Outline phase completed successfully")
            return outline
        except Exception as e:
            logger.error(f"Outline phase failed: {e}")
            self.agents_failed.append("outline_agent")
            self.run_context.mark_agent_failed("outline_agent")
            return {}
    
    def validate_outline(self) -> bool:
        """Validasi outline.json."""
        logger.info("=== VALIDATING OUTLINE ===")
        
        outline_path = self.output_dir / "outline.json"
        
        if not outline_path.exists():
            logger.error("outline.json tidak ditemukan")
            return False
        
        is_valid, errors = validate_json_file(str(outline_path))
        
        if not is_valid:
            logger.warning(f"Outline validation issues: {errors}")
        
        logger.info("Outline validation completed")
        return True
    
    def run_writing_phase(self) -> str:
        """Fase writer agent."""
        logger.info("=== WRITING PHASE ===")
        
        try:
            content = run_writer_agent(self.run_context)
            self.agents_executed.append("writer_agent")
            self.run_context.mark_agent_done("writer_agent")
            
            # Check fallback info from writer
            fallback_info_path = self.output_dir / "fallback_info.json"
            if fallback_info_path.exists():
                with open(fallback_info_path, 'r', encoding='utf-8') as f:
                    fallback_info = json.load(f)
                    if fallback_info.get("fallback_used"):
                        self.fallback_used = True
                        self.fallback_reason = fallback_info.get("fallback_reason", "")
                        logger.info(f"Writer used fallback: {self.fallback_reason}")
            
            word_count = len(content.split()) if content else 0
            logger.info(f"Writing phase completed - {word_count} words")
            
            return content
        except Exception as e:
            logger.error(f"Writing phase failed: {e}")
            self.agents_failed.append("writer_agent")
            self.run_context.mark_agent_failed("writer_agent")
            return ""
    
    def validate_ebook(self) -> bool:
        """Validasi ebook.md."""
        logger.info("=== VALIDATING EBOOK ===")
        
        ebook_path = self.output_dir / "ebook.md"
        
        if not ebook_path.exists():
            logger.error("ebook.md tidak ditemukan")
            return False
        
        result = validate_markdown_file(str(ebook_path))
        
        if not result.get("is_valid", False):
            logger.warning(f"Ebook validation issues: {result.get('errors', [])}")
        
        safety_result = check_file_safety(str(ebook_path))
        
        if not safety_result.get("is_safe", True):
            logger.error(f"Safety check failed: {safety_result.get('findings', [])}")
            return False
        
        logger.info("Ebook validation completed")
        return True
    
    def run_review_phase(self) -> Dict[str, Any]:
        """Fase reviewer agent."""
        logger.info("=== REVIEW PHASE ===")
        
        try:
            review_result = run_reviewer_agent()
            self.agents_executed.append("reviewer_agent")
            self.run_context.mark_agent_done("reviewer_agent")
            
            logger.info(f"Review result: {review_result.get('status')}, score: {review_result.get('score')}")
            
            return review_result
        except Exception as e:
            logger.error(f"Review phase failed: {e}")
            self.agents_failed.append("reviewer_agent")
            self.run_context.mark_agent_failed("reviewer_agent")
            return {"status": "ERROR", "score": 0}
    
    def run_repair_if_needed(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """Fase repair agent jika diperlukan."""
        logger.info("=== REPAIR PHASE (if needed) ===")
        
        if review_result.get("status") != "REPAIR":
            logger.info("Repair tidak diperlukan")
            return {"status": "SKIPPED"}
        
        if review_result.get("secret_leak_detected"):
            logger.error("Secret leak - repair tidak dapat dilakukan")
            return {"status": "REJECTED"}
        
        try:
            repair_result = run_repair_agent()
            self.agents_executed.append("repair_agent")
            self.run_context.mark_agent_done("repair_agent")
            
            logger.info(f"Repair result: {repair_result.get('status')}")
            
            return repair_result
        except Exception as e:
            logger.error(f"Repair phase failed: {e}")
            self.agents_failed.append("repair_agent")
            self.run_context.mark_agent_failed("repair_agent")
            return {"status": "ERROR"}
    
    def _aggregate_cost_reports(self) -> Dict[str, Any]:
        """Agregasi cost reports dari Writer Agent."""
        writer_cost_path = self.output_dir / "writer_cost_report.json"
        
        if writer_cost_path.exists():
            try:
                with open(writer_cost_path, 'r', encoding='utf-8') as f:
                    writer_cost = json.load(f)
                    
                # Merge dengan cost guard report
                cost_report = self.cost_guard.get_report()
                cost_report["writer_cost_report"] = writer_cost
                
                return cost_report
            except Exception as e:
                logger.warning(f"Error reading writer cost report: {e}")
        
        return self.cost_guard.get_report()
    
    def finalize(self) -> None:
        """Finalisasi run - buat reports dan artifacts."""
        logger.info("=== FINALIZATION PHASE ===")
        
        self.run_context.finalize()
        
        output_files = self._get_output_files()
        
        # Build run report
        run_report = self.report_builder.build_run_report(
            self.run_context,
            self.agents_executed,
            self.agents_failed,
            output_files
        )
        
        # Add additional info
        run_report["provider_used"] = self.provider_used
        run_report["fallback_used"] = self.fallback_used
        run_report["fallback_reason"] = self.fallback_reason
        run_report["warnings"] = self.warnings
        run_report["ebook_title"] = self.run_context.ebook_title
        run_report["target_audience"] = self.run_context.target_audience
        run_report["total_chapters"] = self.run_context.total_chapters
        run_report["target_pages"] = self.run_context.target_pages
        run_report["session_number"] = self.run_context.session_number
        run_report["selected_provider"] = self.run_context.selected_provider
        
        # Determine next step
        if self.run_context.mode == "planning":
            run_report["next_step"] = "Plan created. Ready to generate content."
        elif self.fallback_used:
            run_report["next_step"] = "Generated with fallback. Review output quality."
        else:
            run_report["next_step"] = "Generated with AI. Review and approve."
        
        self.report_builder.save_run_report(run_report)
        
        # Build cost report dengan aggregasi
        cost_report = self._aggregate_cost_reports()
        cost_report["fallback_used"] = self.fallback_used
        
        if self.fallback_used:
            cost_report["warning"] = f"Fallback was used: {self.fallback_reason}"
        
        self.report_builder.save_cost_report(cost_report)
        
        self.report_builder.save_artifact_list(output_files)
        self.run_context.save_to_file("output/run_context.json")
        
        logger.info("Finalization completed")
        logger.info(f"Summary: {len(self.agents_executed)} executed, {len(self.agents_failed)} failed")
        logger.info(f"Total cost: ${self.run_context.total_usd_spent:.6f}")
        if self.fallback_used:
            logger.info(f"Fallback used: {self.fallback_reason}")
    
    def _get_output_files(self) -> List[str]:
        """Mendapatkan list file output yang ada."""
        files = [
            "output/task_plan.json",
            "output/outline.json",
            "output/ebook.md",
            "output/run_report.json",
            "output/cost_report.json",
            "output/memory_context.json",
            "output/routing_decision.json",
            "output/review_report.json",
            "output/ebook_repaired.md",
            "output/fallback_info.json",
            "output/writer_cost_report.json"
        ]
        
        existing = [f for f in files if Path(f).exists()]
        return existing
    
    def run(self) -> Dict[str, Any]:
        """
        Execute complete generation workflow.
        
        Returns:
            Result dictionary dengan status dan artifacts.
        """
        logger.info("=" * 50)
        logger.info("DIL AUTONOMOUS EBOOK AGENT - STARTING")
        logger.info("=" * 50)
        
        self.setup()
        
        # Memory phase (selalu)
        self.run_memory_phase()
        
        # Planning phase (selalu)
        plan = self.run_planning_phase()
        
        # Cek mode planning
        if self.run_context.mode == "planning":
            logger.info("Mode is 'planning' - stopping after task plan")
            self.finalize()
            return {
                "status": "SUCCESS",
                "mode": "planning",
                "artifacts": ["output/task_plan.json", "output/memory_context.json"]
            }
        
        # Cek approval gate
        if not self.validate_approval_gate():
            self.finalize()
            return {
                "status": "FAILED",
                "reason": "Approval diperlukan untuk mode ini",
                "phase": "approval_gate"
            }
        
        # Routing phase
        routing = self.run_routing_phase()
        
        # Outline phase
        outline = self.run_outline_phase()
        
        # Validasi outline
        if not self.validate_outline():
            logger.warning("Outline validation failed - melanjutkan dengan warning")
        
        # Writing phase
        content = self.run_writing_phase()
        
        if not content:
            logger.error("Writing phase menghasilkan konten kosong")
        
        # Validasi ebook
        if not self.validate_ebook():
            logger.warning("Ebook validation issues - melanjutkan dengan warning")
        
        # Review phase
        review_result = self.run_review_phase()
        
        # Repair phase jika diperlukan
        if review_result.get("status") == "REPAIR":
            repair_result = self.run_repair_if_needed(review_result)
            
            if repair_result.get("status") == "COMPLETED":
                logger.info("Repair completed successfully")
        
        # Finalize
        self.finalize()
        
        logger.info("=" * 50)
        logger.info("DIL AUTONOMOUS EBOOK AGENT - COMPLETED")
        logger.info("=" * 50)
        
        # Tentukan status akhir
        if len(self.agents_failed) == 0:
            final_status = "SUCCESS"
        elif review_result.get("status") in ["PASS", "REPAIR"]:
            final_status = "PARTIAL_SUCCESS"
        else:
            final_status = "FAILED"
        
        return {
            "status": final_status,
            "mode": self.run_context.mode,
            "agents_executed": self.agents_executed,
            "agents_failed": self.agents_failed,
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
            "provider_used": self.provider_used,
            "review_status": review_result.get("status"),
            "review_score": review_result.get("score"),
            "total_tokens": self.run_context.total_tokens_used,
            "total_cost_usd": round(self.run_context.total_usd_spent, 6),
            "artifacts": self._get_output_files()
        }


def main():
    """Main entry point."""
    try:
        generator = EbookGenerator()
        result = generator.run()
        
        print("\n" + "=" * 50)
        print("GENERATION RESULT")
        print("=" * 50)
        print(f"Status: {result.get('status')}")
        print(f"Mode: {result.get('mode')}")
        print(f"Agents executed: {result.get('agents_executed', [])}")
        print(f"Agents failed: {result.get('agents_failed', [])}")
        print(f"Fallback used: {result.get('fallback_used')}")
        print(f"Provider used: {result.get('provider_used')}")
        print(f"Review: {result.get('review_status')} (score: {result.get('review_score')})")
        print(f"Total tokens: {result.get('total_tokens', 0)}")
        print(f"Total cost: ${result.get('total_cost_usd', 0):.6f}")
        print(f"Artifacts: {len(result.get('artifacts', []))} files")
        print("=" * 50)
        
        status = result.get('status', 'FAILED')
        if status in ['SUCCESS', 'PARTIAL_SUCCESS']:
            sys.exit(0)
        else:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()