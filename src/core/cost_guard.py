"""
DIL Autonomous Ebook Agent - Cost Guard Module

Track dan limit token usage serta biaya untuk mencegah budget overrun.
"""

import json
from typing import Dict, Any, List, Optional

from .logger import get_logger

logger = get_logger(__name__)


class CostGuard:
    """
    Cost guard untuk tracking dan estimating token usage.
    Mencegah budget overrun dengan pre-check sebelum API calls.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Inisialisasi CostGuard.
        
        Args:
            config_dir: Path ke direktori config.
        """
        from pathlib import Path
        
        self.config_dir = Path(config_dir)
        self.cost_limits_path = self.config_dir / "cost_limits.json"
        self.model_pool_path = self.config_dir / "model_pool.json"
        
        self.cost_limits = self._load_cost_limits()
        self.model_prices = self._load_model_prices()
        
        self.total_tokens = 0
        self.total_cost = 0.0
        self.requests: List[Dict[str, Any]] = []
        self.provider_costs: Dict[str, Dict[str, Any]] = {}
        self.limit_exceeded = False
        
        # Default limits
        self.max_tokens_per_run = self.cost_limits.get("limits", {}).get("max_tokens_per_run", 100000)
        self.max_cost_per_run = self.cost_limits.get("limits", {}).get("max_cost_per_run", 0.50)
    
    def _load_cost_limits(self) -> Dict[str, Any]:
        """Load cost limits dari config."""
        try:
            if self.cost_limits_path.exists():
                with open(self.cost_limits_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.debug(f"Loaded cost limits dari {self.cost_limits_path}")
                    return data
        except Exception as e:
            logger.warning(f"Could not load cost limits: {e}")
        return {}
    
    def _load_model_prices(self) -> Dict[str, float]:
        """Load model prices dari model pool config."""
        prices = {}
        
        try:
            if self.model_pool_path.exists():
                with open(self.model_pool_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    providers = data.get("providers", [])
                    
                    for provider in providers:
                        for model in provider.get("models", []):
                            model_id = model.get("id", "")
                            cost_input = model.get("cost_input_per_1k", 0)
                            
                            if model_id and cost_input is not None:
                                prices[model_id] = float(cost_input)
        except Exception as e:
            logger.warning(f"Could not load model prices: {e}")
        
        return prices
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens dari text.
        
        Args:
            text: Input text string.
        
        Returns:
            Estimated token count.
        """
        if not text:
            return 0
        
        # Rough estimate: ~4 characters per token
        char_count = len(text)
        estimated = int(char_count / 4)
        
        return max(estimated, 10)
    
    def get_cost_per_1k(self, model_id: str) -> float:
        """
        Get cost per 1K tokens untuk model.
        
        Args:
            model_id: Model identifier.
        
        Returns:
            Cost per 1K tokens.
        """
        return self.model_prices.get(model_id, 0.001)
    
    def estimate_cost(self, tokens: int, provider_id: str, model_id: str) -> float:
        """
        Estimate cost untuk token count.
        
        Args:
            tokens: Number of tokens.
            provider_id: Provider identifier.
            model_id: Model type/identifier.
        
        Returns:
            Estimated cost in USD.
        """
        cost_per_1k = self.get_cost_per_1k(model_id)
        cost = (tokens / 1000) * cost_per_1k
        
        return round(cost, 6)
    
    def check_limit(self, tokens: int, cost: float) -> tuple[bool, str]:
        """
        Check apakah request akan melebihi limit.
        
        Args:
            tokens: Tokens untuk request.
            cost: Cost untuk request.
        
        Returns:
            Tuple (allowed, reason).
        """
        new_total_tokens = self.total_tokens + tokens
        new_total_cost = self.total_cost + cost
        
        if new_total_tokens > self.max_tokens_per_run:
            return False, f"Token limit exceeded: {new_total_tokens} > {self.max_tokens_per_run}"
        
        if new_total_cost > self.max_cost_per_run:
            return False, f"Cost limit exceeded: ${new_total_cost:.4f} > ${self.max_cost_per_run:.4f}"
        
        return True, "OK"
    
    def check_and_register(
        self,
        prompt: str,
        provider_id: str,
        model_id: str,
        agent_name: str
    ) -> Dict[str, Any]:
        """
        Check jika request within budget dan register.
        
        Args:
            prompt: Prompt text untuk diproses.
            provider_id: Provider identifier.
            model_id: Model type/identifier.
            agent_name: Nama agent membuat request.
        
        Returns:
            Dict dengan 'allowed' boolean dan details.
        """
        estimated_tokens = self.estimate_tokens(prompt)
        estimated_cost = self.estimate_cost(estimated_tokens, provider_id, model_id)
        
        # Check limit
        allowed, reason = self.check_limit(estimated_tokens, estimated_cost)
        
        if not allowed:
            logger.warning(f"Request denied: {reason}")
            self.limit_exceeded = True
            return {
                "allowed": False,
                "reason": reason,
                "tokens": estimated_tokens,
                "cost": estimated_cost
            }
        
        # Register request
        self.total_tokens += estimated_tokens
        self.total_cost += estimated_cost
        
        request = {
            "agent": agent_name,
            "provider": provider_id,
            "model": model_id,
            "tokens": estimated_tokens,
            "cost": estimated_cost,
            "prompt_length": len(prompt)
        }
        
        self.requests.append(request)
        
        # Track per provider
        if provider_id not in self.provider_costs:
            self.provider_costs[provider_id] = {"tokens": 0, "cost": 0.0, "requests": 0}
        
        self.provider_costs[provider_id]["tokens"] += estimated_tokens
        self.provider_costs[provider_id]["cost"] += estimated_cost
        self.provider_costs[provider_id]["requests"] += 1
        
        logger.info(f"Request registered: {agent_name} via {provider_id} - {estimated_tokens} tokens, ${estimated_cost:.6f}")
        
        return {
            "allowed": True,
            "tokens": estimated_tokens,
            "cost": estimated_cost
        }
    
    def add_actual_cost(self, tokens: int, cost: float, provider_id: str, agent_name: str) -> None:
        """
        Add actual cost setelah API call.
        
        Args:
            tokens: Actual tokens used.
            cost: Actual cost in USD.
            provider_id: Provider ID.
            agent_name: Agent name.
        """
        self.total_tokens += tokens
        self.total_cost += cost
        
        request = {
            "agent": agent_name,
            "provider": provider_id,
            "model": "unknown",
            "tokens": tokens,
            "cost": cost,
            "prompt_length": 0,
            "actual": True
        }
        
        self.requests.append(request)
        
        if provider_id not in self.provider_costs:
            self.provider_costs[provider_id] = {"tokens": 0, "cost": 0.0, "requests": 0}
        
        self.provider_costs[provider_id]["tokens"] += tokens
        self.provider_costs[provider_id]["cost"] += cost
        self.provider_costs[provider_id]["requests"] += 1
    
    def get_report(self) -> Dict[str, Any]:
        """
        Get cost report.
        
        Returns:
            Dictionary dengan cost statistics.
        """
        return {
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "limits": {
                "max_tokens_per_run": self.max_tokens_per_run,
                "max_cost_per_run": self.max_cost_per_run
            },
            "remaining": {
                "tokens_remaining": self.max_tokens_per_run - self.total_tokens,
                "cost_remaining": round(self.max_cost_per_run - self.total_cost, 6)
            },
            "utilization": {
                "token_usage_percent": round(
                    (self.total_tokens / self.max_tokens_per_run) * 100,
                    2
                ) if self.max_tokens_per_run > 0 else 0,
                "cost_usage_percent": round(
                    (self.total_cost / self.max_cost_per_run) * 100,
                    2
                ) if self.max_cost_per_run > 0 else 0
            },
            "provider_breakdown": self.provider_costs,
            "requests": self.requests,
            "limit_exceeded": self.limit_exceeded
        }


def get_cost_guard() -> CostGuard:
    """Get atau create global CostGuard instance."""
    global _global_cost_guard
    if '_global_cost_guard' not in globals():
        _global_cost_guard = CostGuard()
    return _global_cost_guard