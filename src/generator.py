"""
DIL Autonomous Ebook Agent - Generator (MVP)

Main entry point for ebook generation workflow.
Orchestrates all agents and generates final artifacts.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Determine package root
PACKAGE_ROOT = Path(__file__).parent
sys.path.insert(0, str(PACKAGE_ROOT))

# Import from core package
from core.logger import get_logger
from core.run_context import create_run_context_from_issue
from core.cost_guard import CostGuard
from core.report_builder import ReportBuilder

# Import from agents package
from agents.memory_agent import run_memory_agent
from agents.task_planner_agent import run_task_planner
from agents.router_agent import run_router_agent
from agents.outline_agent import run_outline_agent
from agents.writer_agent import run_writer_agent

logger = get_logger(__name__)


class EbookGenerator:
    """
    Main generator class that orchestrates the ebook generation workflow.
    
    Flow:
    1. Create RunContext
    2. Run MemoryAgent
    3. Run TaskPlannerAgent
    4. If mode=planning, create report and finish
    5. Run RouterAgent
    6. Run CostGuard
    7. Run OutlineAgent
    8. Run WriterAgent
    9. Create run_report.json
    10. Create cost_report.json
    """
    
    def __init__(self):
        """Initialize EbookGenerator."""
        self.run_context = None
        self.cost_guard = None
        self.report_builder = None
        
        self.agents_executed: List[str] = []
        self.agents_failed: List[str] = []
        
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("EbookGenerator initialized")
    
    def setup(self) -> None:
        """Setup generator components."""
        # Create run context from environment
        self.run_context = create_run_context_from_issue()
        logger.info(f"RunContext created: mode={self.run_context.mode}")
        
        # Initialize cost guard
        self.cost_guard = CostGuard()
        logger.info("CostGuard initialized")
        
        # Initialize report builder
        self.report_builder = ReportBuilder()
        logger.info("ReportBuilder initialized")
    
    def run_memory_phase(self) -> Dict[str, Any]:
        """
        Run memory agent phase.
        
        Returns:
            Memory context dictionary.
        """
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
        """
        Run task planner phase.
        
        Returns:
            Task plan dictionary.
        """
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
        """
        Run router agent phase.
        
        Returns:
            Routing decision dictionary.
        """
        logger.info("=== ROUTING PHASE ===")
        
        try:
            decision = run_router_agent(self.run_context)
            
            if decision.get("status") == "failed":
                logger.error(f"Routing failed: {decision.get('reason')}")
                self.agents_failed.append("router_agent")
                self.run_context.mark_agent_failed("router_agent")
            else:
                self.agents_executed.append("router_agent")
                self.run_context.mark_agent_done("router_agent")
                logger.info("Routing phase completed successfully")
            
            return decision
        except Exception as e:
            logger.error(f"Routing phase failed: {e}")
            self.agents_failed.append("router_agent")
            self.run_context.mark_agent_failed("router_agent")
            return {"status": "failed", "reason": str(e)}
    
    def run_outline_phase(self) -> Dict[str, Any]:
        """
        Run outline agent phase.
        
        Returns:
            Outline dictionary.
        """
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
    
    def run_writing_phase(self) -> str:
        """
        Run writer agent phase.
        
        Returns:
            Ebook content string.
        """
        logger.info("=== WRITING PHASE ===")
        
        try:
            content = run_writer_agent(self.run_context)
            self.agents_executed.append("writer_agent")
            self.run_context.mark_agent_done("writer_agent")
            
            # Estimate words written
            word_count = len(content.split())
            estimated_tokens = word_count * 1  # Approx tokens
            estimated_cost = self.cost_guard.estimate_cost(
                estimated_tokens,
                self.run_context.selected_provider or "unknown",
                "default"
            )
            
            self.run_context.add_cost(estimated_tokens, estimated_cost)
            logger.info(f"Writing phase completed - {word_count} words")
            
            return content
        except Exception as e:
            logger.error(f"Writing phase failed: {e}")
            self.agents_failed.append("writer_agent")
            self.run_context.mark_agent_failed("writer_agent")
            return ""
    
    def finalize(self) -> None:
        """
        Finalize run - create reports and artifacts.
        """
        logger.info("=== FINALIZATION PHASE ===")
        
        # Mark run as finalized
        self.run_context.finalize()
        
        # Build and save run report
        output_files = self._get_output_files()
        
        run_report = self.report_builder.build_run_report(
            self.run_context,
            self.agents_executed,
            self.agents_failed,
            output_files
        )
        
        self.report_builder.save_run_report(run_report)
        
        # Build and save cost report
        cost_report = self.report_builder.build_cost_report(self.cost_guard)
        self.report_builder.save_cost_report(cost_report)
        
        # Save artifacts manifest
        self.report_builder.save_artifact_list(output_files)
        
        # Save run context
        self.run_context.save_to_file("output/run_context.json")
        
        logger.info("Finalization completed")
        logger.info(f"Summary: {len(self.agents_executed)} executed, {len(self.agents_failed)} failed")
        logger.info(f"Total cost: ${self.run_context.total_usd_spent:.6f}")
    
    def _get_output_files(self) -> List[str]:
        """
        Get list of generated output files.
        
        Returns:
            List of file paths.
        """
        files = [
            "output/task_plan.json",
            "output/outline.json",
            "output/ebook.md",
            "output/run_report.json",
            "output/cost_report.json",
            "output/memory_context.json",
            "output/routing_decision.json",
            "output/run_context.json"
        ]
        
        # Only include existing files
        existing = [f for f in files if Path(f).exists()]
        
        return existing
    
    def run(self) -> Dict[str, Any]:
        """
        Execute complete generation workflow.
        
        Returns:
            Result dictionary with status and artifacts.
        """
        logger.info("=" * 50)
        logger.info("DIL AUTONOMOUS EBOOK AGENT - STARTING")
        logger.info("=" * 50)
        
        # Setup
        self.setup()
        
        # Memory phase (always)
        self.run_memory_phase()
        
        # Planning phase (always)
        plan = self.run_planning_phase()
        
        # Check if mode is planning - if so, stop after planning
        if self.run_context.mode == "planning":
            logger.info("Mode is 'planning' - stopping after task plan")
            self.finalize()
            return {
                "status": "success",
                "mode": "planning",
                "artifacts": ["output/task_plan.json"]
            }
        
        # Routing phase
        routing = self.run_routing_phase()
        
        if routing.get("status") == "failed":
            logger.error("Routing failed - cannot proceed")
            self.finalize()
            return {
                "status": "failed",
                "reason": "No API provider available",
                "phase": "routing"
            }
        
        # Outline phase
        outline = self.run_outline_phase()
        
        # Writing phase
        content = self.run_writing_phase()
        
        # Finalize
        self.finalize()
        
        logger.info("=" * 50)
        logger.info("DIL AUTONOMOUS EBOOK AGENT - COMPLETED")
        logger.info("=" * 50)
        
        return {
            "status": "success" if len(self.agents_failed) == 0 else "completed_with_errors",
            "mode": self.run_context.mode,
            "agents_executed": self.agents_executed,
            "agents_failed": self.agents_failed,
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
        print(f"Total tokens: {result.get('total_tokens', 0)}")
        print(f"Total cost: ${result.get('total_cost_usd', 0):.6f}")
        print(f"Artifacts: {result.get('artifacts', [])}")
        print("=" * 50)
        
        # Exit with appropriate code
        sys.exit(0 if result.get('status') == 'success' else 1)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()