"""
DIL Autonomous Ebook Agent - Secret Manager Module

Mengelola API keys dan konfigurasi provider melalui GitHub Secrets.
Semua API key dibaca dari environment variables (GitHub Secrets).
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from .logger import get_logger

logger = get_logger(__name__)


class SecretManager:
    """
    Mengelola API keys dan konfigurasi provider.
    Membaca secrets dari environment variables (GitHub Secrets).
    Membaca provider config dari config/model_pool.json.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Inisialisasi SecretManager.
        
        Args:
            config_dir: Path ke direktori config.
        """
        self.config_dir = Path(config_dir)
        self.model_pool_path = self.config_dir / "model_pool.json"
        self.model_pool = self._load_model_pool()
        self._providers_cache: Optional[List[Dict[str, Any]]] = None
    
    def _load_model_pool(self) -> Dict[str, Any]:
        """Memuat konfigurasi model pool dari file JSON."""
        try:
            if self.model_pool_path.exists():
                with open(self.model_pool_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded model pool dari {self.model_pool_path}")
                    return data
            else:
                logger.warning(f"Model pool config tidak ditemukan: {self.model_pool_path}")
                return {"providers": []}
        except json.JSONDecodeError as e:
            logger.error(f"Gagal parsing model pool JSON: {e}")
            return {"providers": []}
        except Exception as e:
            logger.error(f"Error memuat model pool: {e}")
            return {"providers": []}
    
    def _find_provider_by_id(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        Mencari konfigurasi provider berdasarkan ID.
        
        Args:
            provider_id: ID provider (misalnya 'provider_1').
        
        Returns:
            Konfigurasi provider atau None jika tidak ditemukan.
        """
        providers = self.model_pool.get("providers", [])
        for provider in providers:
            if provider.get("id") == provider_id:
                return provider
        return None
    
    def get_api_key(self, provider_id: str) -> Optional[str]:
        """
        Mendapatkan API key untuk provider tertentu dari environment.
        
        PENTING: Jangan pernah log nilai API key sebenarnya.
        
        Args:
            provider_id: ID provider.
        
        Returns:
            String API key atau None jika tidak tersedia.
        
        Example:
            >>> secret_manager = SecretManager()
            >>> api_key = secret_manager.get_api_key("provider_1")
            >>> if api_key:
            ...     print("API key ditemukan")
        """
        provider_config = self._find_provider_by_id(provider_id)
        
        if not provider_config:
            logger.warning(f"Provider config tidak ditemukan: {provider_id}")
            return None
        
        # Baca env_secret_name dari konfigurasi provider
        env_secret_name = provider_config.get("env_secret_name")
        
        if not env_secret_name:
            logger.warning(f"Provider {provider_id} tidak memiliki env_secret_name")
            return None
        
        api_key = os.environ.get(env_secret_name)
        
        if api_key and len(api_key) > 0:
            # Log keberadaan tapi BUKAN nilainya
            logger.debug(f"API key ditemukan untuk {provider_id} (env: {env_secret_name}, panjang: {len(api_key)})")
            return api_key
        else:
            logger.debug(f"Tidak ada API key untuk {provider_id} (env: {env_secret_name})")
            return None
    
    def is_provider_available(self, provider_id: str) -> bool:
        """
        Memeriksa apakah provider tersedia (memiliki API key valid).
        
        Args:
            provider_id: ID provider.
        
        Returns:
            True jika provider memiliki API key valid.
        """
        api_key = self.get_api_key(provider_id)
        
        if api_key and len(api_key) > 0:
            logger.info(f"Provider {provider_id} tersedia")
            return True
        else:
            logger.info(f"Provider {provider_id} TIDAK tersedia (tidak ada API key)")
            return False
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar provider yang tersedia berdasarkan API key valid.
        
        Returns:
            List konfigurasi provider yang memiliki API key valid.
        """
        if self._providers_cache is not None:
            return self._providers_cache
        
        available = []
        providers = self.model_pool.get("providers", [])
        
        for provider in providers:
            provider_id = provider.get("id")
            
            if provider_id and self.is_provider_available(provider_id):
                # Buat safe config tanpa API key
                safe_config = {
                    "id": provider.get("id"),
                    "provider_name": provider.get("provider_name"),
                    "sdk_type": provider.get("sdk_type"),
                    "base_url": provider.get("base_url"),
                    "model_fast": provider.get("model_fast"),
                    "model_strong": provider.get("model_strong"),
                    "priority": provider.get("priority", 100),
                    "models": provider.get("models", [])
                }
                available.append(safe_config)
        
        # Urutkan berdasarkan priority (lower = higher priority)
        available.sort(key=lambda x: x.get("priority", 100))
        
        self._providers_cache = available
        logger.info(f"Ditemukan {len(available)} provider tersedia")
        
        return available
    
    def get_provider_config(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan konfigurasi untuk provider tertentu.
        
        Args:
            provider_id: ID provider.
        
        Returns:
            Konfigurasi provider atau None.
        """
        providers = self.model_pool.get("providers", [])
        
        for provider in providers:
            if provider.get("id") == provider_id:
                # Return safe config tanpa API key
                return {
                    "id": provider.get("id"),
                    "provider_name": provider.get("provider_name"),
                    "env_secret_name": provider.get("env_secret_name"),
                    "sdk_type": provider.get("sdk_type"),
                    "base_url": provider.get("base_url"),
                    "model_fast": provider.get("model_fast"),
                    "model_strong": provider.get("model_strong"),
                    "priority": provider.get("priority", 100),
                    "models": provider.get("models", [])
                }
        
        logger.warning(f"Konfigurasi provider tidak ditemukan: {provider_id}")
        return None
    
    def get_provider_by_priority(self) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan provider dengan priority tertinggi yang tersedia.
        
        Returns:
            Konfigurasi provider atau None.
        """
        available = self.get_available_providers()
        
        if available:
            return available[0]  # Sudah terurut berdasarkan priority
        return None
    
    def mask_secret_for_log(self, secret_value: str) -> str:
        """
        Membuat versi aman dari secret untuk logging.
        
        Args:
            secret_value: Nilai secret.
        
        Returns:
            String yang sudah di-mask.
        """
        if not secret_value:
            return "[EMPTY]"
        
        if len(secret_value) <= 4:
            return "[SHORT]"
        
        # Tampilkan 2 karakter pertama dan terakhir
        masked = secret_value[:2] + "***" + secret_value[-2:]
        return f"[MASKED:{masked}]"
    
    def clear_cache(self) -> None:
        """Menghapus cache provider untuk memaksa re-check."""
        self._providers_cache = None
        logger.debug("Providers cache dihapus")


# Global instance untuk kemudahan
_global_secret_manager: Optional[SecretManager] = None


def get_secret_manager() -> SecretManager:
    """Mendapatkan atau membuat instance SecretManager global."""
    global _global_secret_manager
    if _global_secret_manager is None:
        _global_secret_manager = SecretManager()
    return _global_secret_manager