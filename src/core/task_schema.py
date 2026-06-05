"""
task_schema.py
--------------
Mendefinisikan JSON schema untuk validasi struktur data pipeline.

Module ini menyediakan schema definitions untuk:
- task_plan.json: Rencana kerja pipeline
- outline.json: Struktur outline ebook
- routing_decision.json: Keputusan routing provider/model

Schema ini digunakan oleh:
- json_validator.py untuk validasi struktur
- agents untuk pembuatan struktur yang benar
- report builder untuk validasi before save

Catatan:
- Tidak ada imports (base layer)
- Hanya pure Python data structures
- Versioned (3.0) untuk backward compatibility
"""

# ============================================================================
# TASK PLAN SCHEMA
# ============================================================================
# Struktur untuk task_plan.json yang dihasilkan oleh TaskPlannerAgent
# Berisi daftar tasks yang harus dijalankan dalam order

TASK_PLAN_SCHEMA: dict = {
    "type": "object",
    "required": [
        "schema_version",
        "run_id",
        "issue_number",
        "mode",
        "ebook_title",
        "total_chapters",
        "pdf_required",
        "api_preference",
        "approval_required",
        "approval_given",
        "estimated_tokens",
        "estimated_usd",
        "tasks",
    ],
    "properties": {
        "schema_version": {"type": "string", "pattern": r"^\d+\.\d+$"},
        "run_id": {"type": "string", "minLength": 1},
        "issue_number": {"type": ["string", "integer"]},
        "mode": {
            "type": "string",
            "enum": ["planning", "test", "session", "full", "review", "repair", "html", "pdf", "archive"],
        },
        "ebook_title": {"type": "string", "minLength": 1},
        "total_chapters": {"type": "integer", "minimum": 1},
        "pdf_required": {"type": "boolean"},
        "api_preference": {
            "type": "string",
            "enum": ["auto", "provider_1", "provider_2", "provider_3", "provider_4", "provider_5"],
        },
        "approval_required": {"type": "boolean"},
        "approval_given": {"type": "boolean"},
        "estimated_tokens": {"type": "integer", "minimum": 0},
        "estimated_usd": {"type": "number", "minimum": 0},
        "tasks": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["task_id", "agent", "description", "order", "requires_approval", "depends_on"],
                "properties": {
                    "task_id": {"type": "string", "pattern": r"^T\d{2}$"},
                    "agent": {"type": "string", "minLength": 1},
                    "description": {"type": "string", "minLength": 1},
                    "order": {"type": "integer", "minimum": 1},
                    "requires_approval": {"type": "boolean"},
                    "depends_on": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
    },
}

# ============================================================================
# OUTLINE SCHEMA
# ============================================================================
# Struktur untuk outline.json yang dihasilkan oleh OutlineAgent
# Berisi struktur lengkap ebook (bab, subbab, learning objectives, dll)

OUTLINE_SCHEMA: dict = {
    "type": "object",
    "required": [
        "schema_version",
        "title",
        "target_audience",
        "reading_level",
        "total_chapters",
        "production_mode",
        "chapters",
    ],
    "properties": {
        "schema_version": {"type": "string", "pattern": r"^\d+\.\d+$"},
        "title": {"type": "string", "minLength": 1},
        "subtitle": {"type": "string"},
        "target_audience": {"type": "string", "minLength": 1},
        "reading_level": {
            "type": "string",
            "enum": ["pemula", "menengah", "lanjutan"],
        },
        "total_chapters": {"type": "integer", "minimum": 1},
        "total_sessions": {"type": "integer", "minimum": 1},
        "production_mode": {
            "type": "string",
            "enum": ["planning", "test", "session", "full"],
        },
        "chapters": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["chapter_num", "title", "learning_objectives", "subtopics"],
                "properties": {
                    "chapter_num": {"type": "integer", "minimum": 1},
                    "session_num": {"type": "integer", "minimum": 1},
                    "title": {"type": "string", "minLength": 1},
                    "learning_objectives": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string", "minLength": 1},
                    },
                    "subtopics": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["id", "title", "keywords"],
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "pattern": r"^\d+\.\d+$",  # Format: chapter.subtopic
                                },
                                "title": {"type": "string", "minLength": 1},
                                "keywords": {
                                    "type": "array",
                                    "minItems": 3,
                                    "items": {"type": "string", "minLength": 1},
                                },
                                "visual_plan": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "table_plan": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "reference_plan": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            },
        },
    },
}

# ============================================================================
# ROUTING DECISION SCHEMA
# ============================================================================
# Struktur untuk routing_decision.json yang dihasilkan oleh RouterAgent
# Berisi keputusan provider dan model untuk setiap task

ROUTING_DECISION_SCHEMA: dict = {
    "type": "object",
    "required": [
        "schema_version",
        "run_id",
        "selected_provider",
        "provider_name",
        "sdk_type",
        "task_routing",
    ],
    "properties": {
        "schema_version": {"type": "string", "pattern": r"^\d+\.\d+$"},
        "run_id": {"type": "string", "minLength": 1},
        "selected_provider": {
            "type": "string",
            "enum": ["provider_1", "provider_2", "provider_3", "provider_4", "provider_5"],
        },
        "provider_name": {"type": "string", "minLength": 1},
        "sdk_type": {"type": "string", "minLength": 1},
        "fallback_provider": {
            "type": ["string", "null"],
            "enum": ["provider_1", "provider_2", "provider_3", "provider_4", "provider_5", None],
        },
        "task_routing": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["task_id", "agent", "provider_id", "model_name", "model_type"],
                "properties": {
                    "task_id": {"type": "string", "pattern": r"^T\d{2}$"},
                    "agent": {"type": "string", "minLength": 1},
                    "provider_id": {
                        "type": "string",
                        "enum": ["provider_1", "provider_2", "provider_3", "provider_4", "provider_5", "local"],
                    },
                    "model_name": {"type": "string"},
                    "model_type": {
                        "type": "string",
                        "enum": ["fast", "strong", "local"],
                    },
                },
            },
        },
    },
}

# ============================================================================
# RUN REPORT SCHEMA
# ============================================================================
# Struktur untuk run_report.json yang dihasilkan oleh ReportBuilder
# Berisi hasil akhir run pipeline

RUN_REPORT_SCHEMA: dict = {
    "type": "object",
    "required": [
        "schema_version",
        "run_id",
        "github_run_id",
        "timestamp_start",
        "timestamp_end",
        "issue_number",
        "mode",
        "ebook_title",
        "status",
        "agents_executed",
        "agents_failed",
        "validators_passed",
        "validators_failed",
        "review_score",
        "review_status",
        "pdf_generated",
        "total_tokens_used",
        "total_usd_spent",
        "human_approval_requested",
    ],
    "properties": {
        "schema_version": {"type": "string", "pattern": r"^\d+\.\d+$"},
        "run_id": {"type": "string", "minLength": 1},
        "github_run_id": {"type": "string"},
        "timestamp_start": {"type": "string"},
        "timestamp_end": {"type": ["string", "null"]},
        "issue_number": {"type": ["string", "integer"]},
        "mode": {
            "type": "string",
            "enum": ["planning", "test", "session", "full", "review", "repair", "html", "pdf"],
        },
        "ebook_title": {"type": "string"},
        "status": {
            "type": "string",
            "enum": ["SUCCESS", "PARTIAL", "FAILED", "PENDING_APPROVAL"],
        },
        "agents_executed": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "agent": {"type": "string"},
                    "timestamp": {"type": "string"},
                },
            },
        },
        "agents_failed": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "agent": {"type": "string"},
                    "error": {"type": "string"},
                    "timestamp": {"type": "string"},
                },
            },
        },
        "validators_passed": {
            "type": "array",
            "items": {"type": "string"},
        },
        "validators_failed": {
            "type": "array",
            "items": {"type": "string"},
        },
        "review_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "review_status": {
            "type": "string",
            "enum": ["PASS", "REPAIR", "REJECT", "PENDING"],
        },
        "pdf_generated": {"type": "boolean"},
        "pdf_pages": {"type": "integer", "minimum": 0},
        "repair_iterations": {"type": "integer", "minimum": 0},
        "total_tokens_used": {"type": "integer", "minimum": 0},
        "total_usd_spent": {"type": "number", "minimum": 0},
        "human_approval_requested": {"type": "boolean"},
        "notes": {"type": "string"},
    },
}

# ============================================================================
# COST REPORT SCHEMA
# ============================================================================
# Struktur untuk cost_report.json yang dihasilkan oleh CostGuard

COST_REPORT_SCHEMA: dict = {
    "type": "object",
    "required": [
        "schema_version",
        "total_tokens_used",
        "total_usd_spent",
        "breakdown_by_provider",
        "breakdown_by_agent",
        "limit_exceeded",
    ],
    "properties": {
        "schema_version": {"type": "string", "pattern": r"^\d+\.\d+$"},
        "total_tokens_used": {"type": "integer", "minimum": 0},
        "total_usd_spent": {"type": "number", "minimum": 0},
        "breakdown_by_provider": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["provider_id", "tokens_used", "usd_spent", "calls_made"],
                "properties": {
                    "provider_id": {"type": "string"},
                    "tokens_used": {"type": "integer", "minimum": 0},
                    "usd_spent": {"type": "number", "minimum": 0},
                    "calls_made": {"type": "integer", "minimum": 0},
                },
            },
        },
        "breakdown_by_agent": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["agent_name", "tokens_used", "usd_spent"],
                "properties": {
                    "agent_name": {"type": "string"},
                    "tokens_used": {"type": "integer", "minimum": 0},
                    "usd_spent": {"type": "number", "minimum": 0},
                },
            },
        },
        "limit_warnings": {
            "type": "array",
            "items": {"type": "string"},
        },
        "limit_exceeded": {"type": "boolean"},
    },
}
