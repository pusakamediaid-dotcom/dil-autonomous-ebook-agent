"""
DIL Content & Income Agent - Affiliate Product Research Agent

Searches for products suitable for affiliate promotion.
Only uses allowed data sources: API, public pages, manual input.
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.logger import get_logger
from core.source_manager import get_source_manager
from core.platform_policy_guard import get_platform_policy_guard

logger = get_logger(__name__)


class AffiliateProductResearchAgent:
    """
    Agent that researches products for affiliate promotion.
    
    Allowed data sources:
    - Official marketplace API (if available)
    - Public product pages (without login)
    - User manual input via GitHub Issue
    - User CSV upload
    - Manual research data
    
    Forbidden:
    - Login scraping
    - Cookie-based access
    - Automated browsing
    """
    
    # Product evaluation criteria
    CRITERIA = {
        "required": [
            "legal_and_safe",
            "relevant_to_niche",
            "has_practical_benefit",
            "reasonable_price"
        ],
        "preferred": [
            "clear_commission_info",
            "good_reviews",
            "educational_value",
            "suitable_for_target_audience"
        ]
    }
    
    # Forbidden product categories
    FORBIDDEN_CATEGORIES = [
        "illegal_products",
        "dangerous_products",
        "adult_only",
        "gambling",
        "weapons",
        "counterfeit",
        "get_rich_quick"
    ]
    
    def __init__(self):
        """Initialize AffiliateProductResearchAgent."""
        self.output_dir = Path("output/affiliate")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.source_manager = get_source_manager()
        self.policy_guard = get_platform_policy_guard()
        
        self.products: List[Dict[str, Any]] = []
        self.research_report: Dict[str, Any] = {}
    
    def check_api_available(self, platform: str) -> bool:
        """Check if API is available for platform."""
        if platform == "tokopedia":
            return self.source_manager.check_tokopedia_api_available()
        return False
    
    def create_manual_input_template(self, niche: str, target_audience: str) -> Dict[str, Any]:
        """Create a template for manual product input."""
        return {
            "platform": "manual",
            "niche": niche,
            "target_audience": target_audience,
            "instructions": "Isi data produk secara manual. Jangan ambil data dari halaman yang butuh login.",
            "template": {
                "product_name": "Nama Produk",
                "product_url": "URL produk publik",
                "affiliate_url": "URL affiliate jika ada",
                "price_range": "Rentang harga",
                "commission_info": "Info komisi (jika diketahui)",
                "why_recommended": "Alasan produk ini cocok",
                "target_buyer": "Siapa yang cocok membeli",
                "content_angle": "Sudut konten untuk promosi",
                "risk": "Risiko atau catatan",
                "approval_required": True
            },
            "csv_columns": [
                "product_name",
                "product_url",
                "affiliate_url",
                "price_range",
                "commission_info",
                "why_recommended",
                "target_buyer",
                "content_angle",
                "risk"
            ]
        }
    
    def research_from_manual_input(
        self,
        niche: str,
        target_audience: str,
        platform: str,
        manual_products: List[Dict[str, Any]] = None,
        content_brief: str = ""
    ) -> Dict[str, Any]:
        """
        Research products from manual input.
        
        Args:
            niche: Target niche.
            target_audience: Target audience.
            platform: Target platform.
            manual_products: Manually provided products.
            content_brief: Content brief for context.
            
        Returns:
            Research report dictionary.
        """
        logger.info(f"Researching products for niche='{niche}', platform={platform}")
        
        products = []
        
        if manual_products:
            for product in manual_products:
                # Validate product
                product_entry = {
                    "product_name": product.get("product_name", ""),
                    "product_url": product.get("product_url", ""),
                    "affiliate_url": product.get("affiliate_url", ""),
                    "price_range": product.get("price_range", ""),
                    "commission_info": product.get("commission_info", ""),
                    "why_recommended": product.get("why_recommended", ""),
                    "target_buyer": product.get("target_buyer", target_audience),
                    "content_angle": product.get("content_angle", ""),
                    "risk": product.get("risk", ""),
                    "approval_required": True,
                    "source": "manual_input"
                }
                products.append(product_entry)
        
        # If no products provided, create example products based on niche
        if not products:
            products = self._generate_example_products(niche, target_audience)
        
        self.products = products
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "platform": platform,
            "niche": niche,
            "target_audience": target_audience,
            "content_brief": content_brief,
            "data_source": "manual_input" if manual_products else "example_template",
            "api_available": self.check_api_available(platform),
            "products_found": len(products),
            "products": products,
            "evaluation_criteria": self.CRITERIA,
            "forbidden_categories": self.FORBIDDEN_CATEGORIES,
            "notes": "Produk dari input manual. Verifikasi sebelum promosi." if manual_products else "Ini adalah template contoh. Isi dengan produk nyata dari riset Anda.",
            "next_steps": [
                "Verifikasi setiap produk secara manual",
                "Pastikan produk relevan dengan niche",
                "Buat affiliate link jika platform mendukung",
                "Gunakan Affiliate Content Agent untuk membuat draft"
            ]
        }
        
        self.research_report = report
        logger.info(f"Research completed: {len(products)} products found")
        return report
    
    def _generate_example_products(self, niche: str, target_audience: str) -> List[Dict[str, Any]]:
        """Generate example product template based on niche."""
        examples = [
            {
                "product_name": f"[Isi Nama Produk - {niche}]",
                "product_url": "[URL produk publik]",
                "affiliate_url": "[URL affiliate jika ada]",
                "price_range": "[Rentang harga]",
                "commission_info": "[Info komisi jika diketahui]",
                "why_recommended": f"Cocok untuk {target_audience} karena...",
                "target_buyer": target_audience,
                "content_angle": f"Edukasi tentang manfaat produk untuk {niche}",
                "risk": "Perlu verifikasi harga dan ketersediaan",
                "approval_required": True,
                "source": "template"
            }
        ]
        return examples
    
    def save_products(self) -> None:
        """Save product candidates to file."""
        output_path = self.output_dir / "product_candidates.json"
        
        data = {
            "platform": self.research_report.get("platform", "manual"),
            "niche": self.research_report.get("niche", ""),
            "target_audience": self.research_report.get("target_audience", ""),
            "products": self.products,
            "notes": self.research_report.get("notes", ""),
            "generated_at": self.research_report.get("generated_at", "")
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Product candidates saved to {output_path}")
    
    def save_research_report(self) -> None:
        """Save research report to file."""
        output_path = self.output_dir / "affiliate_research_report.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.research_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Research report saved to {output_path}")
    
    def execute(
        self,
        niche: str,
        target_audience: str,
        platform: str = "tokopedia",
        manual_products: List[Dict[str, Any]] = None,
        content_brief: str = ""
    ) -> Dict[str, Any]:
        """
        Execute product research.
        
        Args:
            niche: Target niche.
            target_audience: Target audience.
            platform: Target platform.
            manual_products: Manually provided products.
            content_brief: Content brief.
            
        Returns:
            Research report.
        """
        logger.info("AffiliateProductResearchAgent executing...")
        
        # Check if API is available
        api_available = self.check_api_available(platform)
        
        if api_available:
            logger.info(f"API available for {platform} - would fetch from API")
            # In a real implementation, this would call the API
            # For now, fall back to manual input
        
        # Use manual input or generate template
        report = self.research_from_manual_input(
            niche=niche,
            target_audience=target_audience,
            platform=platform,
            manual_products=manual_products,
            content_brief=content_brief
        )
        
        # Save outputs
        self.save_products()
        self.save_research_report()
        
        logger.info("AffiliateProductResearchAgent completed")
        return report


def run_affiliate_product_research(
    niche: str,
    target_audience: str,
    platform: str = "tokopedia",
    manual_products: List[Dict[str, Any]] = None,
    content_brief: str = ""
) -> Dict[str, Any]:
    """Convenience function to run affiliate product research."""
    agent = AffiliateProductResearchAgent()
    return agent.execute(niche, target_audience, platform, manual_products, content_brief)
