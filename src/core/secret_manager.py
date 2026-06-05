"""
DIL Autonomous Ebook Agent - Secret Manager Module

Manages API keys and provider configuration through GitHub Secrets.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from .logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class SecretManager:
    """
    Manages API keys and provider configurations.
    Reads secrets from environment variables (GitHub Secrets).
    Reads provider config from config/model_pool.json.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize SecretManager.
        
        Args:
            config_dir: Path to config directory.
        """
        self.config_dir = Path(config_dir)
        self.model_pool_path = self.config_dir / "model_pool.json"
        self.model_pool = self._load_model_pool()
        self._providers_cache = None
    
    def _load_model_pool(self) -> Dict[str, Any]:
        """Load model pool configuration from JSON file."""
        try:
            if self.model_pool_path.exists():
                with open(self.model_pool_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded model pool from {self.model_pool_path}")
                    return data
            else:
                logger.warning(f"Model pool config not found: {self.model_pool_path}")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse model pool JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading model pool: {e}")
            return {}
    
    def _get_env_key_name(self, provider_id: str) -> str:
        """
        Get the environment variable name for a provider's API key.
        
        Args:
            provider_id: Provider identifier (e.g., 'provider_1').
        
        Returns:
            Environment variable name.
        """
        return f"{provider_id.upper()}_API_KEY"
    
    def get_api_key(self, provider_id: str) -> Optional[str]:
        """
        Get API key for a specific provider from environment.
        
        IMPORTANT: Never log the actual API key value.
        
        Args:
            provider_id: Provider identifier.
        
        Returns:
            API key string or None if not available.
        
        Example:
            >>> secret_manager = SecretManager()
            >>> api_key = secret_manager.get_api_key("provider_1")
            >>> if api_key:
            ...     print("API key found")
        """
        env_key = self._get_env_key_name(provider_id)
        api_key = os.environ.get(env_key)
        
        if api_key:
            # Log presence but NOT the value
            logger.debug(f"API key found for {provider_id} (length: {len(api_key)})")
            return api_key
        else:
            logger.debug(f"No API key found for {provider_id}")
            return None
    
    def is_provider_available(self, provider_id: str) -> bool:
        """
        Check if a provider is available (has valid API key).
        
        Args:
            provider_id: Provider identifier.
        
        Returns:
            True if provider has valid API key.
        """
        api_key = self.get_api_key(provider_id)
        
        if api_key and len(api_key) > 0:
            logger.info(f"Provider {provider_id} is available")
            return True
        else:
            logger.info(f"Provider {provider_id} is NOT available (no API key)")
            return False
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get list of available providers based on valid API keys.
        
        Returns:
            List of provider configurations that have valid API keys.
        """
        if self._providers_cache is not None:
            return self._providers_cache
        
        available = []
        providers = self.model_pool.get("providers", [])
        
        for provider in providers:
            provider_id = provider.get("id")
            if provider_id and self.is_provider_available(provider_id):
                # Don't include the actual API key in returned config
                safe_config = {
                    "id": provider.get("id"),
                    "name": provider.get("name"),
                    "api_endpoint": provider.get("api_endpoint"),
                    "models": provider.get("models", []),
                    "priority": provider.get("priority", 100)
                }
                available.append(safe_config)
        
        # Sort by priority (lower is higher priority)
        available.sort(key=lambda x: x.get("priority", 100))
        
        self._providers_cache = available
        logger.info(f"Found {len(available)} available providers")
        
        return available
    
    def get_provider_config(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider_id: Provider identifier.
        
        Returns:
            Provider configuration dict or None.
        """
        providers = self.model_pool.get("providers", [])
        
        for provider in providers:
            if provider.get("id") == provider_id:
                # Return safe config without API key
                safe_config = provider.copy()
                return safe_config
        
        logger.warning(f"Provider config not found: {provider_id}")
        return None
    
    def clear_cache(self) -> None:
        """Clear the providers cache to force re-check."""
        self._providers_cache = None
        logger.debug("Providers cache cleared")


# Global instance for convenience
_global_secret_manager: Optional[SecretManager] = None


def get_secret_manager() -> SecretManager:
    """Get or create global SecretManager instance."""
    global _global_secret_manager
    if _global_secret_manager is None:
        _global_secret_manager = SecretManager()
    return _global_secret_manager