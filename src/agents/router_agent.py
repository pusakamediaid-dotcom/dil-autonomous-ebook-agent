"""
DIL Autonomous Ebook Agent - Router Agent

Selects the best available API provider based on priorities and availability.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger
from core.run_context import RunContext
from core.secret_manager import SecretManager, get_secret_manager

logger = get_logger(__name__)


class RouterAgent:
    """
    Agent that routes requests to the best available API provider.
    Checks provider availability and selects based on priority.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize RouterAgent.
        
        Args:
            config_dir: Path to config directory.
        """
        self.config_dir = Path(config_dir)
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.secret_manager = get_secret_manager()
        self.model_pool = self._load_model_pool()
        
        self.routing_decision: Dict[str, Any] = {}
    
    def _load_model_pool(self) -> Dict[str, Any]:
        """Load model pool configuration."""
        model_pool_path = self.config_dir / "model_pool.json"
        
        try:
            if model_pool_path.exists():
                with open(model_pool_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded model pool with {len(data.get('providers', []))} providers")
                    return data
            else:
                logger.warning(f"Model pool not found: {model_pool_path}")
                return {"providers": []}
        except Exception as e:
            logger.error(f"Error loading model pool: {e}")
            return {"providers": []}
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get list of providers with valid API keys.
        
        Returns:
            List of available provider configurations.
        """
        available = self.secret_manager.get_available_providers()
        logger.info(f"Found {len(available)} available providers")
        return available
    
    def select_provider(
        self,
        preference: Optional[str] = None,
        available: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Select the best provider based on preference and availability.
        
        Args:
            preference: Preferred provider ID (or "auto").
            available: List of available providers.
        
        Returns:
            Selected provider config or None.
        """
        if available is None:
            available = self.get_available_providers()
        
        if not available:
            logger.error("No providers available!")
            return None
        
        # If preference specified and available, use it
        if preference and preference != "auto":
            for provider in available:
                if provider.get("id") == preference:
                    logger.info(f"Selected preferred provider: {preference}")
                    return provider
            
            # Preference not available, use first available
            logger.warning(f"Preferred provider {preference} not available, using fallback")
        
        # Use first available (already sorted by priority)
        selected = available[0]
        logger.info(f"Selected provider (by priority): {selected.get('id')}")
        
        return selected
    
    def get_model_for_provider(
        self,
        provider: Dict[str, Any],
        reading_level: str = "intermediate"
    ) -> Optional[Dict[str, Any]]:
        """
        Select appropriate model for provider based on reading level.
        
        Args:
            provider: Provider configuration.
            reading_level: Target reading level.
        
        Returns:
            Selected model configuration.
        """
        models = provider.get("models", [])
        
        if not models:
            logger.warning(f"No models available for {provider.get('id')}")
            return None
        
        # For MVP, just return first model (could be enhanced with level-based selection)
        # Map reading levels to preferred model tiers
        level_preference = {
            "beginner": "mini",
            "intermediate": "standard",
            "advanced": "pro"
        }
        
        preferred_tier = level_preference.get(reading_level, "standard")
        
        # Try to find model matching preferred tier
        for model in models:
            model_id = model.get("id", "").lower()
            if preferred_tier in model_id or "standard" in model_id:
                return model
        
        # Fallback to first model
        return models[0]
    
    def make_routing_decision(
        self,
        run_context: RunContext,
        available: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create routing decision based on context and availability.
        
        Args:
            run_context: Current run context.
            available: List of available providers.
        
        Returns:
            Routing decision dictionary.
        """
        # Get available providers
        if available is None:
            available = self.get_available_providers()
        
        # Select provider
        selected = self.select_provider(run_context.api_preference, available)
        
        if not selected:
            decision = {
                "status": "failed",
                "reason": "No API providers available",
                "run_id": run_context.run_id
            }
        else:
            # Get model
            model = self.get_model_for_provider(selected, run_context.reading_level)
            
            decision = {
                "status": "success",
                "run_id": run_context.run_id,
                "selected_provider": {
                    "id": selected.get("id"),
                    "name": selected.get("name"),
                    "api_endpoint": selected.get("api_endpoint")
                },
                "selected_model": model,
                "alternative_providers": [
                    {"id": p.get("id"), "name": p.get("name")}
                    for p in available[1:5]  # Up to 4 alternatives
                ],
                "preference_used": run_context.api_preference,
                "fallback_used": run_context.api_preference not in [p.get("id") for p in available]
            }
            
            # Update run context
            run_context.selected_provider = selected.get("id")
        
        self.routing_decision = decision
        logger.info(f"Routing decision: {decision.get('status')}")
        
        return decision
    
    def save_routing_decision(self, output_file: str = "output/routing_decision.json") -> None:
        """
        Save routing decision to JSON file.
        
        Args:
            output_file: Output file path.
        """
        if not self.routing_decision:
            logger.warning("No routing decision to save")
            return
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.routing_decision, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Routing decision saved to {output_path}")
    
    def execute(self, run_context: RunContext) -> Dict[str, Any]:
        """
        Execute router agent.
        
        Args:
            run_context: Current run context.
        
        Returns:
            Routing decision dictionary.
        """
        logger.info("RouterAgent executing...")
        
        decision = self.make_routing_decision(run_context)
        self.save_routing_decision()
        
        logger.info("RouterAgent completed")
        
        return decision


def run_router_agent(run_context: RunContext) -> Dict[str, Any]:
    """
    Convenience function to run RouterAgent.
    
    Args:
        run_context: Current run context.
    
    Returns:
        Routing decision dictionary.
    """
    agent = RouterAgent()
    return agent.execute(run_context)