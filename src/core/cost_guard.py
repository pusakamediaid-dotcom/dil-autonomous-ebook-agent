"""
DIL Autonomous Ebook Agent - Cost Guard Module (MVP)

Simple token estimation and cost tracking to prevent budget overruns.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

from .logger import get_logger

logger = get_logger(__name__)


# Default cost per 1K tokens if config not available
DEFAULT_COSTS = {
    "gpt-4o": 0.005,
    "gpt-4o-mini": 0.00015,
    "gpt-4-turbo": 0.01,
    "gpt-3.5-turbo": 0.0005,
    "claude-3-5-sonnet": 0.003,
    "claude-3-opus": 0.015,
    "default": 0.001
}


class CostGuard:
    """
    MVP cost guard for tracking and estimating token usage.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize CostGuard.
        
        Args:
            config_dir: Path to config directory.
        """
        self.config_dir = Path(config_dir)
        self.cost_limits_path = self.config_dir / "cost_limits.json"
        self.model_pool_path = self.config_dir / "model_pool.json"
        
        self.cost_limits = self._load_cost_limits()
        self.model_prices = self._load_model_prices()
        
        self.total_tokens = 0
        self.total_cost = 0.0
        self.requests = []
        
        # Default limits
        self.max_tokens_per_run = self.cost_limits.get("max_tokens_per_run", 100000)
        self.max_cost_per_run = self.cost_limits.get("max_cost_per_run", 0.50)
    
    def _load_cost_limits(self) -> Dict[str, Any]:
        """Load cost limits from config."""
        try:
            if self.cost_limits_path.exists():
                with open(self.cost_limits_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.debug(f"Loaded cost limits from {self.cost_limits_path}")
                    return data
        except Exception as e:
            logger.warning(f"Could not load cost limits: {e}")
        return {}
    
    def _load_model_prices(self) -> Dict[str, float]:
        """Load model prices from model pool config."""
        prices = DEFAULT_COSTS.copy()
        
        try:
            if self.model_pool_path.exists():
                with open(self.model_pool_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    providers = data.get("providers", [])
                    
                    for provider in providers:
                        for model in provider.get("models", []):
                            model_id = model.get("id", "")
                            cost_input = model.get("cost_input_per_1k", 0)
                            
                            if model_id and cost_input:
                                prices[model_id] = float(cost_input)
        except Exception as e:
            logger.warning(f"Could not load model prices: {e}")
        
        return prices
    
    def estimate_tokens(self, text: str) -> int:
        """
        Simple token estimation based on word count.
        
        Rough estimate: 1 token ≈ 4 characters for English,
        or ~0.75 words for typical prose.
        
        Args:
            text: Input text string.
        
        Returns:
            Estimated token count.
        """
        if not text:
            return 0
        
        # Simple heuristic: ~4 characters per token
        char_count = len(text)
        estimated = int(char_count / 4)
        
        return max(estimated, 10)  # Minimum 10 tokens
    
    def estimate_tokens_from_words(self, word_count: int) -> int:
        """
        Estimate tokens from word count.
        
        Args:
            word_count: Number of words.
        
        Returns:
            Estimated token count.
        """
        return int(word_count * 1.33)  # ~1.33 tokens per word
    
    def get_cost_per_1k(self, model_id: str) -> float:
        """
        Get cost per 1K tokens for a model.
        
        Args:
            model_id: Model identifier.
        
        Returns:
            Cost per 1K tokens.
        """
        return self.model_prices.get(model_id, self.model_prices.get("default", 0.001))
    
    def estimate_cost(self, tokens: int, provider_id: str, model_type: str) -> float:
        """
        Estimate cost for a given token count.
        
        Args:
            tokens: Number of tokens.
            provider_id: Provider identifier.
            model_type: Model type/identifier.
        
        Returns:
            Estimated cost in USD.
        """
        cost_per_1k = self.get_cost_per_1k(model_type)
        cost = (tokens / 1000) * cost_per_1k
        
        logger.debug(f"Cost estimate: {tokens} tokens × ${cost_per_1k}/1K = ${cost:.6f}")
        
        return round(cost, 6)
    
    def check_and_register(
        self,
        prompt: str,
        provider_id: str,
        model_type: str,
        agent_name: str
    ) -> Dict[str, Any]:
        """
        Check if request is within budget and register it.
        
        Args:
            prompt: Prompt text to process.
            provider_id: Provider identifier.
            model_type: Model type/identifier.
            agent_name: Name of agent making the request.
        
        Returns:
            Dict with 'allowed' boolean and 'reason' if not allowed.
        """
        # Estimate tokens for prompt
        estimated_tokens = self.estimate_tokens(prompt)
        
        # Estimate cost
        estimated_cost = self.estimate_cost(estimated_tokens, provider_id, model_type)
        
        # Check limits
        new_total_tokens = self.total_tokens + estimated_tokens
        new_total_cost = self.total_cost + estimated_cost
        
        # Check token limit
        if new_total_tokens > self.max_tokens_per_run:
            logger.warning(
                f"Token limit exceeded: {new_total_tokens} > {self.max_tokens_per_run}"
            )
            return {
                "allowed": False,
                "reason": f"Token limit exceeded ({new_total_tokens} > {self.max_tokens_per_run})"
            }
        
        # Check cost limit
        if new_total_cost > self.max_cost_per_run:
            logger.warning(
                f"Cost limit exceeded: ${new_total_cost:.4f} > ${self.max_cost_per_run:.4f}"
            )
            return {
                "allowed": False,
                "reason": f"Cost limit exceeded (${new_total_cost:.4f} > ${self.max_cost_per_run:.4f})"
            }
        
        # Register the request
        self.total_tokens += estimated_tokens
        self.total_cost += estimated_cost
        
        self.requests.append({
            "agent": agent_name,
            "provider": provider_id,
            "model": model_type,
            "tokens": estimated_tokens,
            "cost": estimated_cost
        })
        
        logger.info(
            f"Request registered: {agent_name} - {estimated_tokens} tokens, ${estimated_cost:.6f}"
        )
        
        return {
            "allowed": True,
            "tokens": estimated_tokens,
            "cost": estimated_cost
        }
    
    def get_report(self) -> Dict[str, Any]:
        """
        Get cost report.
        
        Returns:
            Dictionary with cost statistics.
        """
        return {
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "max_tokens_limit": self.max_tokens_per_run,
            "max_cost_limit": self.max_cost_per_run,
            "requests": self.requests,
            "tokens_remaining": self.max_tokens_per_run - self.total_tokens,
            "cost_remaining": round(self.max_cost_per_run - self.total_cost, 6)
        }
    
    def add_actual_cost(self, tokens: int, cost: float) -> None:
        """
        Add actual cost after API call (for more accurate tracking).
        
        Args:
            tokens: Actual tokens used.
            cost: Actual cost in USD.
        """
        self.total_tokens += tokens
        self.total_cost += cost
        logger.debug(f"Added actual cost: {tokens} tokens, ${cost:.6f}")


def get_cost_guard() -> CostGuard:
    """Get or create global CostGuard instance."""
    global _global_cost_guard
    if '_global_cost_guard' not in globals():
        _global_cost_guard = CostGuard()
    return _global_cost_guard