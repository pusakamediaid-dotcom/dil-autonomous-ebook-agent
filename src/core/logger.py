"""
logger.py
---------
Modul logging terpusat untuk DIL Autonomous Ebook Agent.

Input:
- Nama logger.
- Path file log opsional.

Output:
- Objek logger Python yang sudah dikonfigurasi.

Fitur utama:
- Masking otomatis untuk nilai yang terlihat seperti API key.
- Output ke console dan ke file error_log.txt.
- Format log yang konsisten.
"""

import logging
import os
import re


class MaskingFilter(logging.Filter):
    """