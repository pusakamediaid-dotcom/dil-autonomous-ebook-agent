"""
secret_manager.py
-----------------
Mengelola akses API key secara aman dari environment variables.

Input:
- config/model_pool.json untuk membaca nama environment variable.

Output:
- API key dari environment saat runtime.

Catatan keamanan:
- API key tidak pernah disimpan di file kode.
- API key tidak pernah dicetak ke log.
"""

import json
import os
from src.core.logger import get_logger

logger = get_logger(__name__)


class SecretManager:
    """Pembaca GitHub Secrets melalui environment variables."""

    def __init__(self, model_pool_path: str = "config/model_pool.json"):
        self.model_pool_path = model_pool_path
        with open(model_pool_path, "r", encoding="utf-8") as file:
            self.pool = json.load(file)
        logger.info("SecretManager aktif dengan konfigurasi: %s", model_pool_path)

