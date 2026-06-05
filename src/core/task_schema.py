"""
DIL Autonomous Ebook Agent - Task Schema Module

Simple schemas for task planning and outline structures.
"""

from typing import List, Dict, Any, Optional


# ============================================================================
# Task Plan Schema
# ============================================================================

TASK_PLAN_SCHEMA = {
    "schema_version": "1.0",
    "description": "Schema for ebook generation task plan",
    "fields": {
        "run_id": "string - GitHub run ID or local identifier",
        "mode": "string - 'planning' or 'test' or 'production'",
        "ebook_title": "string - Title of the ebook",
        "target_audience": "string - Target reader demographic",
        "reading_level": "string - beginner/intermediate/advanced",
        "chapters": [
            {
                "number": "integer - Chapter number",
                "title": "string - Chapter title",
                "subtopics": ["list of subtopic strings"],
                "estimated_words": "integer - Estimated word count",
                "priority": "integer - Execution priority (1=highest)"
            }
        ],
        "total_chapters": "integer - Total number of chapters",
        "estimated_total_words": "integer - Total estimated words",
        "agents_required": ["list of agent names to execute"],
        "provider_selection": {
            "preferred": "string - Preferred provider ID",
            "fallback": "string - Fallback provider ID",
            "reason": "string - Selection reasoning"
        },
        "cost_estimate": {
            "min_tokens": "integer - Minimum estimated tokens",
            "max_tokens": "integer - Maximum estimated tokens",
            "estimated_cost_usd": "float - Estimated cost in USD"
        },
        "created_at": "string - ISO timestamp"
    }
}


def create_task_plan(
    run_id: str,
    mode: str,
    ebook_title: str,
    target_audience: str,
    reading_level: str,
    chapters: List[Dict[str, Any]],
    provider_selection: Dict[str, str],
    cost_estimate: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a task plan dictionary.
    
    Args:
        run_id: Run identifier.
        mode: Execution mode.
        ebook_title: Title of the ebook.
        target_audience: Target audience description.
        reading_level: Reading level.
        chapters: List of chapter configurations.
        provider_selection: Provider selection info.
        cost_estimate: Cost estimation.
    
    Returns:
        Task plan dictionary.
    """
    from datetime import datetime
    
    total_words = sum(c.get("estimated_words", 500) for c in chapters)
    
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "mode": mode,
        "ebook_title": ebook_title,
        "target_audience": target_audience,
        "reading_level": reading_level,
        "chapters": chapters,
        "total_chapters": len(chapters),
        "estimated_total_words": total_words,
        "agents_required": ["memory_agent", "router_agent", "outline_agent", "writer_agent"],
        "provider_selection": provider_selection,
        "cost_estimate": cost_estimate,
        "created_at": datetime.now().isoformat()
    }


# ============================================================================
# Outline Schema
# ============================================================================

OUTLINE_SCHEMA = {
    "schema_version": "1.0",
    "description": "Schema for ebook outline",
    "fields": {
        "ebook_title": "string - Title of the ebook",
        "chapters": [
            {
                "number": "integer - Chapter number",
                "title": "string - Chapter title",
                "description": "string - Brief chapter description",
                "sections": [
                    {
                        "title": "string - Section title",
                        "subsections": [
                            {
                                "title": "string - Subsection title",
                                "content_type": "string - konseptual/praktikal/referensi",
                                "key_concepts": ["list of key concepts"],
                                "estimated_words": "integer - Estimated words"
                            }
                        ]
                    }
                ],
                "estimated_words": "integer - Total chapter words"
            }
        ],
        "metadata": {
            "total_chapters": "integer - Total chapters",
            "total_sections": "integer - Total sections",
            "total_subsections": "integer - Total subsections",
            "total_estimated_words": "integer - Total estimated words"
        },
        "created_at": "string - ISO timestamp"
    }
}


def create_outline(
    ebook_title: str,
    chapters: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create an outline dictionary.
    
    Args:
        ebook_title: Title of the ebook.
        chapters: List of chapter outlines.
    
    Returns:
        Outline dictionary.
    """
    from datetime import datetime
    
    total_sections = 0
    total_subsections = 0
    total_words = 0
    
    for chapter in chapters:
        for section in chapter.get("sections", []):
            total_sections += 1
            total_subsections += len(section.get("subsections", []))
        total_words += chapter.get("estimated_words", 0)
    
    return {
        "schema_version": "1.0",
        "ebook_title": ebook_title,
        "chapters": chapters,
        "metadata": {
            "total_chapters": len(chapters),
            "total_sections": total_sections,
            "total_subsections": total_subsections,
            "total_estimated_words": total_words
        },
        "created_at": datetime.now().isoformat()
    }


# ============================================================================
# Validation Functions
# ============================================================================

def validate_task_plan(plan: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate a task plan against schema.
    
    Args:
        plan: Task plan dictionary.
    
    Returns:
        Tuple of (is_valid, list of error messages).
    """
    errors = []
    
    required_fields = ["run_id", "mode", "ebook_title", "chapters", "total_chapters"]
    
    for field in required_fields:
        if field not in plan:
            errors.append(f"Missing required field: {field}")
    
    if "chapters" in plan and not isinstance(plan["chapters"], list):
        errors.append("'chapters' must be a list")
    
    if "mode" in plan and plan["mode"] not in ["planning", "test", "production"]:
        errors.append("Invalid mode: must be 'planning', 'test', or 'production'")
    
    return len(errors) == 0, errors


def validate_outline(outline: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate an outline against schema.
    
    Args:
        outline: Outline dictionary.
    
    Returns:
        Tuple of (is_valid, list of error messages).
    """
    errors = []
    
    if "ebook_title" not in outline:
        errors.append("Missing required field: ebook_title")
    
    if "chapters" not in outline:
        errors.append("Missing required field: chapters")
    elif not isinstance(outline["chapters"], list):
        errors.append("'chapters' must be a list")
    
    return len(errors) == 0, errors