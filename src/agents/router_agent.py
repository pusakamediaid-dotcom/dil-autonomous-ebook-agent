"""
DIL Autonomous Ebook Agent - Router Agent

Memilih provider API terbaik berdasarkan prioritas dan ketersediaan.
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
    Agent yang merutekan request ke provider API terbaik.
    Memeriksa ketersediaan provider dan memilih berdasarkan prioritas.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Inisialisasi RouterAgent.
        
        Args:
            config_dir: Path ke direktori config.
        """
        self.config_dir = Path(config_dir)
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.secret_manager = get_secret_manager()
        self.model_pool = self._load_model_pool()
        
        self.routing_decision: Dict[str, Any] = {}
    
    def _load_model_pool(self) -> Dict[str, Any]:
        """Memuat konfigurasi model pool."""
        model_pool_path = self.config_dir / "model_pool.json"
        
        try:
            if model_pool_path.exists():
                with open(model_pool_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded model pool dengan {len(data.get('providers', []))} providers")
                    return data
            else:
                logger.warning(f"Model pool tidak ditemukan: {model_pool_path}")
                return {"providers": []}
        except Exception as e:
            logger.error(f"Error memuat model pool: {e}")
            return {"providers": []}
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Mendapatkan daftar provider dengan API key valid.
        
        Returns:
            List konfigurasi provider yang tersedia.
        """
        available = self.secret_manager.get_available_providers()
        logger.info(f"Ditemukan {len(available)} provider tersedia")
        return available
    
    def select_provider(
        self,
        preference: Optional[str] = None,
        available: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Memilih provider terbaik berdasarkan preference dan ketersediaan.
        
        Args:
            preference: Provider ID yang dipilih (atau "auto").
            available: List provider yang tersedia.
        
        Returns:
            Konfigurasi provider yang dipilih atau None.
        """
        if available is None:
            available = self.get_available_providers()
        
        if not available:
            logger.error("Tidak ada provider tersedia!")
            return None
        
        # Jika preference ditentukan dan tersedia, gunakan
        if preference and preference != "auto":
            for provider in available:
                if provider.get("id") == preference:
                    logger.info(f"Provider dipilih sesuai preference: {preference}")
                    return provider
            
            # Preference tidak tersedia, gunakan fallback
            logger.warning(f"Provider preference {preference} tidak tersedia, menggunakan fallback")
        
        # Gunakan provider dengan priority tertinggi (sudah terurut)
        selected = available[0]
        logger.info(f"Provider dipilih (by priority): {selected.get('id')} - {selected.get('provider_name')}")
        
        return selected
    
    def build_fallback_chain(
        self,
        selected: Optional[Dict[str, Any]],
        available: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Membangun chain fallback provider.
        
        Args:
            selected: Provider yang dipilih.
            available: List provider yang tersedia.
        
        Returns:
            List ID provider dalam urutan fallback.
        """
        chain = []
        
        if selected:
            # Tambahkan selected provider pertama
            chain.append(selected.get("id"))
        
        # Tambahkan provider lain sebagai fallback
        for provider in available:
            provider_id = provider.get("id")
            if provider_id not in chain:
                chain.append(provider_id)
        
        return chain
    
    def make_routing_decision(
        self,
        run_context: RunContext,
        available: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Membuat keputusan routing berdasarkan context dan ketersediaan.
        
        Args:
            run_context: Run context saat ini.
            available: List provider yang tersedia.
        
        Returns:
            Dictionary keputusan routing.
        """
        # Dapatkan provider yang tersedia
        if available is None:
            available = self.get_available_providers()
        
        # Pilih provider
        selected = self.select_provider(run_context.api_preference, available)
        
        if not selected:
            decision = {
                "status": "failed",
                "reason": "Tidak ada provider API yang tersedia. Pastikan GitHub Secrets sudah dikonfigurasi.",
                "run_id": run_context.run_id,
                "provider_available_count": 0,
                "fallback_chain": []
            }
        else:
            # Bangun fallback chain
            fallback_chain = self.build_fallback_chain(selected, available)
            
            decision = {
                "status": "success",
                "run_id": run_context.run_id,
                "selected_provider_id": selected.get("id"),
                "selected_provider_name": selected.get("provider_name"),
                "selected_sdk_type": selected.get("sdk_type"),
                "selected_base_url": selected.get("base_url"),
                "selected_model_fast": selected.get("model_fast"),
                "selected_model_strong": selected.get("model_strong"),
                "fallback_chain": fallback_chain,
                "provider_available_count": len(available),
                "preference_used": run_context.api_preference,
                "fallback_used": run_context.api_preference not in [p.get("id") for p in available] if run_context.api_preference else False,
                "reason": f"Provider {selected.get('provider_name')} dipilih" + 
                         (" (fallback)" if run_context.api_preference and run_context.api_preference != selected.get("id") else "")
            }
            
            # Update run context
            run_context.selected_provider = selected.get("id")
        
        self.routing_decision = decision
        logger.info(f"Routing decision: {decision.get('status')}")
        
        return decision
    
    def save_routing_decision(self, output_file: str = "output/routing_decision.json") -> None:
        """
        Menyimpan keputusan routing ke file JSON.
        
        Args:
            output_file: Path file output.
        """
        if not self.routing_decision:
            logger.warning("Tidak ada routing decision untuk disimpan")
            return
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.routing_decision, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Routing decision disimpan ke {output_path}")
    
    def execute(self, run_context: RunContext) -> Dict[str, Any]:
        """
        Menjalankan router agent.
        
        Args:
            run_context: Run context saat ini.
        
        Returns:
            Dictionary keputusan routing.
        """
        logger.info("RouterAgent executing...")
        
        decision = self.make_routing_decision(run_context)
        self.save_routing_decision()
        
        logger.info("RouterAgent completed")
        
        return decision


def run_router_agent(run_context: RunContext) -> Dict[str, Any]:
    """
    Fungsi convenience untuk menjalankan RouterAgent.
    
    Args:
        run_context: Run context saat ini.
    
    Returns:
        Dictionary keputusan routing.
    """
    agent = RouterAgent()
    return agent.execute(run_context)