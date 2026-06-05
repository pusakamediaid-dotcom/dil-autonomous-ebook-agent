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
    """Filter untuk menyensor string panjang yang terlihat seperti secret."""

    PATTERNS_TO_MASK = [r"[A-Za-z0-9_\-]{32,}"]

    def filter(self, record):
        record.msg = self._mask_secrets(str(record.msg))
        if record.args:
            record.args = tuple(
                self._mask_secrets(str(arg)) if isinstance(arg, str) else arg
                for arg in (record.args if isinstance(record.args, tuple) else (record.args,))
            )
        return True

    def _mask_secrets(self, text: str) -> str:
        for pattern in self.PATTERNS_TO_MASK:
            def mask_match(match):
                value = match.group(0)
                if len(value) >= 32:
                    return value[:4] + "*" * (len(value) - 4)
                return value
            text = re.sub