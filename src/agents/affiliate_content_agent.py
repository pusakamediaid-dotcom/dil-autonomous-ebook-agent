"""
DIL Content & Income Agent - Affiliate Content Agent

Creates draft promotional content for affiliate products.
All content includes mandatory disclosure.
All output is DRAFT - no auto-posting.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.logger import get_logger
from core.approval_gate import get_approval_gate
from core.cost_guard import CostGuard

logger = get_logger(__name__)

AFFILIATE_DISCLOSURE = (
    "Catatan: tautan ini bisa berupa link affiliate. "
    "Jika Anda membeli melalui link ini, saya bisa mendapat komisi "
    "tanpa biaya tambahan untuk Anda."
)


class AffiliateContentAgent:
    """
    Agent that creates draft promotional content for affiliate products.
    
    Output formats:
    - Draft Threads post
    - Short caption draft
    - Educational content draft
    - Landing page draft
    - CTA draft
    - Disclosure draft
    
    All content is DRAFT and requires human review before publishing.
    """
    
    def __init__(self):
        """Initialize AffiliateContentAgent."""
        self.output_dir = Path("output/affiliate")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.approval_gate = get_approval_gate()
        self.cost_guard = CostGuard()
        
        self.content_drafts: List[Dict[str, Any]] = []
    
    def load_products(self, products_file: str = "output/affiliate/product_candidates.json") -> List[Dict[str, Any]]:
        """Load product candidates from file."""
        try:
            path = Path(products_file)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("products", [])
        except Exception as e:
            logger.error(f"Error loading products: {e}")
        return []
    
    def create_content_draft(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create content draft for a single product.
        
        Args:
            product: Product dictionary.
            
        Returns:
            Content draft dictionary.
        """
        product_name = product.get("product_name", "Produk")
        target_buyer = product.get("target_buyer", "pembaca")
        content_angle = product.get("content_angle", "edukasi")
        why_recommended = product.get("why_recommended", "")
        price_range = product.get("price_range", "")
        
        # Education angle draft
        education_draft = (
            f"## {product_name}\n\n"
            f"Produk ini cocok untuk {target_buyer} yang membutuhkan "
            f"alat praktis untuk kebutuhan sehari-hari.\n\n"
            f"{why_recommended}\n\n"
            f"**Harga:** {price_range}\n\n"
            f"**Catatan:** Produk ini dipilih berdasarkan relevansi "
            f"dan manfaat praktis, bukan klaim berlebihan."
        )
        
        # Threads draft
        threads_draft = (
            f"Rekomendasi untuk {target_buyer}:\n\n"
            f"📌 {product_name}\n\n"
            f"{why_recommended[:200]}\n\n"
            f"Harga: {price_range}\n\n"
            f"{AFFILIATE_DISCLOSURE}"
        )
        
        # Short caption
        caption_draft = (
            f"Rekomendasi: {product_name} — "
            f"cocok untuk {target_buyer}. "
            f"{AFFILIATE_DISCLOSURE}"
        )
        
        # CTA
        cta_draft = (
            f"Tertarik dengan {product_name}? "
            f"Cek link di bio untuk info lebih lanjut. "
            f"{AFFILIATE_DISCLOSURE}"
        )
        
        # Risk assessment
        risk = product.get("risk", "")
        risk_note = f"Risiko: {risk}" if risk else "Risiko: Perlu verifikasi harga dan ketersediaan terbaru."
        
        draft = {
            "product_name": product_name,
            "content_angle": content_angle,
            "education_draft": education_draft,
            "threads_draft": threads_draft,
            "caption_draft": caption_draft,
            "cta_draft": cta_draft,
            "disclosure": AFFILIATE_DISCLOSURE,
            "risk_note": risk_note,
            "status": "draft",
            "approval_required": True,
            "created_at": datetime.now().isoformat()
        }
        
        return draft
    
    def create_all_drafts(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create content drafts for all products."""
        drafts = []
        
        for product in products:
            draft = self.create_content_draft(product)
            drafts.append(draft)
            logger.info(f"Created draft for: {product.get('product_name', 'unknown')}")
        
        self.content_drafts = drafts
        return drafts
    
    def format_drafts_markdown(self, drafts: List[Dict[str, Any]]) -> str:
        """Format all drafts as markdown."""
        lines = [
            "# Draft Konten Affiliate",
            "",
            f"**Tanggal:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Jumlah Produk:** {len(drafts)}",
            f"**Status:** DRAFT — Memerlukan review dan approval manusia",
            "",
            "---",
            ""
        ]
        
        for i, draft in enumerate(drafts, 1):
            lines.extend([
                f"## Produk {i} — {draft['product_name']}",
                "",
                f"### Angle Edukasi",
                "",
                draft['education_draft'],
                "",
                f"### Draft Threads",
                "",
                draft['threads_draft'],
                "",
                f"### Draft Caption Pendek",
                "",
                draft['caption_draft'],
                "",
                f"### CTA",
                "",
                draft['cta_draft'],
                "",
                f"### Disclosure",
                "",
                draft['disclosure'],
                "",
                f"### Risiko Klaim",
                "",
                draft['risk_note'],
                "",
                "---",
                ""
            ])
        
        lines.extend([
            "## Catatan Penting",
            "",
            "- Semua konten di atas adalah DRAFT",
            "- WAJIB review sebelum dipublikasikan",
            "- Affiliate disclosure WAJIB disertakan",
            "- Jangan klaim produk pasti menghasilkan uang",
            "- Jangan membuat testimoni palsu",
            "- Posting hanya setelah approval manusia",
            ""
        ])
        
        return '\n'.join(lines)
    
    def save_drafts(self) -> None:
        """Save content drafts to markdown file."""
        markdown = self.format_drafts_markdown(self.content_drafts)
        output_path = self.output_dir / "content_drafts.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        logger.info(f"Content drafts saved to {output_path}")
    
    def execute(self, products: List[Dict[str, Any]] = None) -> str:
        """
        Execute content creation.
        
        Args:
            products: List of products. If None, loads from file.
            
        Returns:
            Markdown content.
        """
        logger.info("AffiliateContentAgent executing...")
        
        if products is None:
            products = self.load_products()
        
        if not products:
            logger.warning("No products found - creating template draft")
            products = [{
                "product_name": "[Isi Nama Produk]",
                "product_url": "",
                "affiliate_url": "",
                "price_range": "[Harga]",
                "commission_info": "",
                "why_recommended": "[Alasan rekomendasi]",
                "target_buyer": "[Target pembeli]",
                "content_angle": "edukasi",
                "risk": "Template - perlu diisi dengan produk nyata",
                "approval_required": True
            }]
        
        drafts = self.create_all_drafts(products)
        self.save_drafts()
        
        markdown = self.format_drafts_markdown(drafts)
        
        logger.info(f"AffiliateContentAgent completed: {len(drafts)} drafts created")
        return markdown


def run_affiliate_content(products: List[Dict[str, Any]] = None) -> str:
    """Convenience function to run affiliate content creation."""
    agent = AffiliateContentAgent()
    return agent.execute(products)
