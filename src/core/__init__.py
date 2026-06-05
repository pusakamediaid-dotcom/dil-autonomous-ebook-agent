"""
DIL Autonomous Ebook Agent - Core Module

Core utilities and infrastructure for the ebook generation system.
"""

from .logger import get_logger, log_safe, MaskingFilter
from .secret_manager import SecretManager, get_secret_manager
from .run_context import RunContext, create_run_context_from_issue
from .cost_guard import CostGuard, get_cost_guard
from .report_builder import ReportBuilder, get_report_builder
from .task_schema import (
    TASK_PLAN_SCHEMA,
    OUTLINE_SCHEMA,
    create_task_plan,
    create_outline,
    validate_task_plan,
    validate_outline
)

__all__ = [
    'get_logger',
    'log_safe',
    'MaskingFilter',
    'SecretManager',
    'get_secret_manager',
    'RunContext',
    'create_run_context_from_issue',
    'CostGuard',
    'get_cost_guard',
    'ReportBuilder',
    'get_report_builder',
    'TASK_PLAN_SCHEMA',
    'OUTLINE_SCHEMA',
    'create_task_plan',
    'create_outline',
    'validate_task_plan',
    'validate_outline',
]