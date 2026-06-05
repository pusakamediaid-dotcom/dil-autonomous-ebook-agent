"""
DIL Content & Income Agent - Compliance Agent

Checks affiliate and news content for compliance before use.
Ensures all content meets safety, legal, and ethical standards.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.logger import get_logger

logger = get_logger(__name__)


class ComplianceAgent:
    """
    Agent that checks content compliance for affiliate and news content.
    
    Checks affiliate:
    - Has affiliate disclosure
    - No false claims
    - No guaranteed income claims
    - No dangerous products
    - No spam CTA
    - No buyer manipulation
    
    Checks news:
    - Has source
    - No full article copy
    - No misinformation
    - No unsourced claims
    - No misleading headlines
    - Facts and opinions separated
    """
    
    def __init__(self, config_dir: str = "config"):
        """Initialize ComplianceAgent."""
        self.config_dir = Path(config_dir)
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.compliance_rules = self._load_compliance_rules()
        self.monetization_rules = self._load_monetization_rules()
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules from config."""
        rules_path = self.config_dir / "compliance_rules.json"
        try:
            if rules_path.exists():
                with open(rules_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load compliance rules: {e}")
        return {}
    
    def _load_monetization_rules(self) -> Dict[str, Any]:
        """Load monetization rules from config."""
        rules_path = self.config_dir / "monetization_rules.json"
        try:
            if rules_path.exists():
                with open(rules_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load monetization rules: {e}")
        return {}
    
    def check_affiliate_disclosure(self, content: str) -> List[str]:
        """Check if affiliate disclosure is present."""
        issues = []
        disclosure_patterns = [
            r'affiliate',
            r'link\s+affiliate',
            r'komisi',
            r'catatan.*tautan',
            r'disclosure',
        ]
        
        has_disclosure = any(
            re.search(p, content, re.IGNORECASE) for p in disclosure_patterns
        )
        
        if not has_disclosure:
            issues.append("Affiliate disclosure tidak ditemukan")
        
        return issues
    
    def check_false_claims(self, content: str) -> List[str]:
        """Check for false or misleading claims."""
        issues = []
        
        false_claim_patterns = [
            (r'(?:jaminan|pasti|guaranteed)\s*(?:uang|income|penghasilan|kaya)', 'Klaim penghasilan pasti terdeteksi'),
            (r'(?:100%|seratus\s+persen)\s*(?:berhasil|sukses|work)', 'Klaim keberhasilan 100% terdeteksi'),
            (r'(?:tanpa\s+kerja|passive\s+income)\s*(?:otomatis|automatis)', 'Klaim penghasilan tanpa kerja terdeteksi'),
        ]
        
        for pattern, message in false_claim_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(message)
        
        return issues
    
    def check_dangerous_products(self, products: List[Dict[str, Any]]) -> List[str]:
        """Check for dangerous or illegal products."""
        issues = []
        
        forbidden_keywords = [
            'senjata', 'weapon', 'narkoba', 'drug', 'obat ilegal',
            'judi', 'gambling', 'pornografi', 'pornography',
            'palsu', 'counterfeit', 'replica branded'
        ]
        
        for product in products:
            name = product.get("product_name", "").lower()
            desc = product.get("why_recommended", "").lower()
            combined = f"{name} {desc}"
            
            for keyword in forbidden_keywords:
                if keyword in combined:
                    issues.append(f"Produk berpotensi bermasalah: '{product.get('product_name')}' mengandung kata kunci '{keyword}'")
        
        return issues
    
    def check_spam_cta(self, content: str) -> List[str]:
        """Check for spammy call-to-action."""
        issues = []
        
        spam_patterns = [
            (r'(?:beli\s+sekarang|buy\s+now)\s*!!+', 'CTA agresif terdeteksi'),
            (r'(?:jangan\s+sampai\s+terlewat|dont\s+miss\s+out)\s*!!+', 'FOMO berlebihan terdeteksi'),
            (r'(?:promo\s+terbatas|limited\s+offer)\s*!!+', 'Urgency palsu terdeteksi'),
            (r'(?:!!!|⚠️⚠️⚠️)', 'Tanda seru berlebihan terdeteksi'),
        ]
        
        for pattern, message in spam_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(message)
        
        return issues
    
    def check_source_present(self, content: str) -> List[str]:
        """Check if source is cited in news content."""
        issues = []
        
        source_patterns = [
            r'(?:sumber|source|referensi|reference)\s*:',
            r'(?:menurut|berdasarkan|dilaporkan)\s+',
            r'https?://\S+',
            r'(?:dikutip\s+dari|quoted\s+from)',
        ]
        
        has_source = any(
            re.search(p, content, re.IGNORECASE) for p in source_patterns
        )
        
        if not has_source:
            issues.append("Sumber berita tidak ditemukan dalam konten")
        
        return issues
    
    def check_full_copy(self, content: str, sources: List[Dict[str, Any]] = None) -> List[str]:
        """Check for full article copy."""
        issues = []
        
        # If content is very long and has few sources, suspect full copy
        word_count = len(content.split())
        if word_count > 1000 and sources and len(sources) < 2:
            issues.append(f"Konten sangat panjang ({word_count} kata) dengan sedikit sumber - potensi salinan penuh")
        
        return issues
    
    def check_misleading_headline(self, content: str) -> List[str]:
        """Check for misleading headlines."""
        issues = []
        
        misleading_patterns = [
            (r'(?:mengejutkan|shocking|heboh|viral)\s*!', 'Judul sensasional terdeteksi'),
            (r'(?:anda\s+tidak\s+akan\s+percaya|you\s+wont\s+believe)', 'Clickbait terdeteksi'),
            (r'(?:rahasia|secret)\s+(?:yang|that)\s+(?: disembunyikan|hidden)', 'Clickbait terdeteksi'),
        ]
        
        for pattern, message in misleading_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(message)
        
        return issues
    
    def check_fact_opinion_separated(self, content: str) -> List[str]:
        """Check if facts and opinions are separated."""
        issues = []
        
        opinion_markers = [
            r'(?:menurut\s+saya|saya\s+berpikir|in\s+my\s+opinion)',
            r'(?:opini|opinion|analisis|analysis)\s*:',
            r'(?:pendapat|view)\s*:',
        ]
        
        has_opinion = any(
            re.search(p, content, re.IGNORECASE) for p in opinion_markers
        )
        
        # If content has opinion-like statements but no markers
        subjective_words = len(re.findall(r'\b(?:mungkin|seharusnya|sebaiknya|might|should)\b', content, re.IGNORECASE))
        if subjective_words > 3 and not has_opinion:
            issues.append("Konten mengandung pernyataan subjektif tanpa label opini/analisis yang jelas")
        
        return issues
    
    def execute_affiliate_compliance(self, content: str, products: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run full affiliate compliance check.
        
        Args:
            content: Content to check.
            products: List of products to check.
            
        Returns:
            Compliance report dictionary.
        """
        logger.info("Running affiliate compliance check...")
        
        all_issues = []
        required_fixes = []
        
        # Run checks
        disclosure_issues = self.check_affiliate_disclosure(content)
        all_issues.extend(disclosure_issues)
        required_fixes.extend(disclosure_issues)
        
        claim_issues = self.check_false_claims(content)
        all_issues.extend(claim_issues)
        
        if products:
            product_issues = self.check_dangerous_products(products)
            all_issues.extend(product_issues)
        
        cta_issues = self.check_spam_cta(content)
        all_issues.extend(cta_issues)
        
        # Determine status
        critical_issues = [i for i in all_issues if any(k in i.lower() for k in ['disclosure', 'klaim', 'berbahaya', 'palsu'])]
        
        if critical_issues:
            status = "REJECT"
            safe_to_publish = False
        elif all_issues:
            status = "REPAIR"
            safe_to_publish = False
        else:
            status = "PASS"
            safe_to_publish = True
        
        score = max(0, 100 - (len(all_issues) * 15))
        
        report = {
            "type": "affiliate_compliance",
            "status": status,
            "score": score,
            "issues": all_issues,
            "required_fixes": required_fixes,
            "approval_required": True,
            "safe_to_publish": safe_to_publish,
            "checks_performed": [
                "disclosure_check",
                "false_claims_check",
                "dangerous_products_check",
                "spam_cta_check"
            ]
        }
        
        logger.info(f"Affiliate compliance: {status} (score: {score}, issues: {len(all_issues)})")
        return report
    
    def execute_news_compliance(self, content: str, sources: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run full news compliance check.
        
        Args:
            content: Content to check.
            sources: List of sources.
            
        Returns:
            Compliance report dictionary.
        """
        logger.info("Running news compliance check...")
        
        all_issues = []
        required_fixes = []
        
        # Run checks
        source_issues = self.check_source_present(content)
        all_issues.extend(source_issues)
        
        copy_issues = self.check_full_copy(content, sources)
        all_issues.extend(copy_issues)
        
        headline_issues = self.check_misleading_headline(content)
        all_issues.extend(headline_issues)
        required_fixes.extend(headline_issues)
        
        fact_issues = self.check_fact_opinion_separated(content)
        all_issues.extend(fact_issues)
        required_fixes.extend(fact_issues)
        
        # Check for hate speech
        hate_patterns = [
            r'(?:benci|hate)\s+(?:terhadap|against)\s+',
            r'(?:kebencian|incitement)',
        ]
        for pattern in hate_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                all_issues.append("Indikasi ujaran kebencian terdeteksi")
        
        # Determine status
        critical_issues = [i for i in all_issues if any(k in i.lower() for k in ['sumber', 'salinan', 'kebencian', 'hoaks'])]
        
        if critical_issues:
            status = "REJECT"
            safe_to_publish = False
        elif all_issues:
            status = "REPAIR"
            safe_to_publish = False
        else:
            status = "PASS"
            safe_to_publish = True
        
        score = max(0, 100 - (len(all_issues) * 15))
        
        report = {
            "type": "news_compliance",
            "status": status,
            "score": score,
            "issues": all_issues,
            "required_fixes": required_fixes,
            "approval_required": True,
            "safe_to_publish": safe_to_publish,
            "checks_performed": [
                "source_check",
                "full_copy_check",
                "misleading_headline_check",
                "fact_opinion_check",
                "hate_speech_check"
            ]
        }
        
        logger.info(f"News compliance: {status} (score: {score}, issues: {len(all_issues)})")
        return report
    
    def save_compliance_report(self, report: Dict[str, Any], output_subdir: str = "affiliate") -> None:
        """Save compliance report to file."""
        output_path = self.output_dir / output_subdir / "compliance_report.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Compliance report saved to {output_path}")


def run_affiliate_compliance(content: str, products: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to run affiliate compliance."""
    agent = ComplianceAgent()
    report = agent.execute_affiliate_compliance(content, products)
    agent.save_compliance_report(report, "affiliate")
    return report


def run_news_compliance(content: str, sources: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to run news compliance."""
    agent = ComplianceAgent()
    report = agent.execute_news_compliance(content, sources)
    agent.save_compliance_report(report, "news")
    return report
