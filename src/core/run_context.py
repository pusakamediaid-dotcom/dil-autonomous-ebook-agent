"""
run_context.py
--------------
Membuat dan mengelola konteks untuk setiap run pipeline.

Input:
- Environment variables dari GitHub Actions.

Output:
- Objek RunContext yang dipakai oleh agent lain.
"""

import os
import uuid
from datetime import datetime
from src.core.logger import get_logger

logger = get_logger(__name__)


class RunContext:
    """Konteks satu kali eksekusi pipeline."""

    def __init__(self):
        self.run_id = str