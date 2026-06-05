"""
DIL Content & Income Agent - News Research Agent

Searches and summarizes world news from official sources.
Only uses allowed sources: RSS, official APIs, manual input.
Never copies full articles.
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.logger import get_logger
from core.source_manager import get_source_manager
from core.secret_manager import get_secret_manager

logger = get_logger(__name__)


class NewsResearchAgent:
    """
    Agent that researches news from official sources.
    
    Allowed sources:
    - RSS feeds from official media
    - News APIs (NewsAPI, etc.)
    - Google Custom Search API
    - Manual input from user
    - Official websites
    
    Forbidden:
    - Full article copy
    - Unattributed content
    - Fake news
    - Opinion as fact
    """
    
    def __init__(self):
        """Initialize NewsResearchAgent."""
        self.output_dir = Path("output/news")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.source_manager = get_source_manager()
        self.secret_manager = get_secret_manager()
        
        self.news_items: List[Dict[str, Any]] = []
        self.research_report: Dict[str, Any] = {}
    
    def check_sources_available(self) -> Dict[str, bool]:
        """Check which news sources are available."""
        return {
            "news_api": self.source_manager.check_news_api_available(),
            "google_custom_search": self.source_manager.check_google_search_available(),
            "manual_input": True,
            "rss_feeds": True  # Always available (public)
        }
    
    def research_from_manual_input(
        self,
        topic: str,
        manual_links: List[str] = None,
        manual_items: List[Dict[str, Any]] = None,
        content_brief: str = ""
    ) -> Dict[str, Any]:
        """
        Research news from manual input.
        
        Args:
            topic: News topic.
            manual_links: List of news URLs provided by user.
            manual_items: Manually provided news items.
            content_brief: Content brief.
            
        Returns:
            Research report.
        """
        logger.info(f"Researching news for topic: {topic}")
        
        sources = []
        warnings = []
        
        if manual_items:
            for item in manual_items:
                source_entry = {
                    "title": item.get("title", ""),
                    "source_name": item.get("source_name", "Manual Input"),
                    "url": item.get("url", ""),
                    "published_at": item.get("published_at", ""),
                    "summary": item.get("summary", ""),
                    "reliability_note": item.get("reliability_note", "Perlu verifikasi manual"),
                    "content_angle": item.get("content_angle", ""),
                    "source_type": "manual_input"
                }
                sources.append(source_entry)
        
        if manual_links:
            for link in manual_links:
                source_entry = {
                    "title": f"Berita dari {link[:50]}...",
                    "source_name": "User-provided link",
                    "url": link,
                    "published_at": "",
                    "summary": "Perlu diisi manual oleh user",
                    "reliability_note": "Sumber dari input user - perlu verifikasi",
                    "content_angle": "",
                    "source_type": "manual_link"
                }
                sources.append(source_entry)
        
        if not sources:
            # Create template for manual input
            sources = self._create_template_sources(topic)
            warnings.append("Tidak ada sumber berita yang tersedia. Gunakan template manual.")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "topic": topic,
            "content_brief": content_brief,
            "data_source": "manual_input",
            "sources_available": self.check_sources_available(),
            "total_sources": len(sources),
            "sources": sources,
            "warnings": warnings,
            "reliability_rules": {
                "must_have_source": True,
                "must_have_url": True,
                "must_label_opinion": True,
                "must_separate_fact_from_opinion": True,
                "max_quote_length_words": 50,
                "require_attribution": True
            },
            "next_steps": [
                "Verifikasi setiap sumber secara manual",
                "Pastikan sumber kredibel dan relevan",
                "Gunakan News Content Agent untuk membuat draft",
                "Jangan salin artikel penuh"
            ]
        }
        
        self.news_items = sources
        self.research_report = report
        
        logger.info(f"News research completed: {len(sources)} sources found")
        return report
    
    def _create_template_sources(self, topic: str) -> List[Dict[str, Any]]:
        """Create template sources for manual input."""
        return [
            {
                "title": f"[Judul Berita tentang {topic}]",
                "source_name": "[Nama Media]",
                "url": "[URL Artikel]",
                "published_at": "[Tanggal Publikasi]",
                "summary": "[Ringkasan singkat berita - maksimal 2-3 kalimat]",
                "reliability_note": "Template - perlu diisi dengan berita nyata",
                "content_angle": "[Sudut konten untuk analisis]",
                "source_type": "template"
            },
            {
                "title": f"[Judul Berita kedua tentang {topic}]",
                "source_name": "[Nama Media]",
                "url": "[URL Artikel]",
                "published_at": "[Tanggal Publikasi]",
                "summary": "[Ringkasan singkat berita - maksimal 2-3 kalimat]",
                "reliability_note": "Template - perlu diisi dengan berita nyata",
                "content_angle": "[Sudut konten untuk analisis]",
                "source_type": "template"
            }
        ]
    
    def save_research_report(self) -> None:
        """Save research report to file."""
        output_path = self.output_dir / "news_research_report.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.research_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"News research report saved to {output_path}")
    
    def execute(
        self,
        topic: str,
        manual_links: List[str] = None,
        manual_items: List[Dict[str, Any]] = None,
        content_brief: str = ""
    ) -> Dict[str, Any]:
        """
        Execute news research.
        
        Args:
            topic: News topic.
            manual_links: Manual news links.
            manual_items: Manual news items.
            content_brief: Content brief.
            
        Returns:
            Research report.
        """
        logger.info("NewsResearchAgent executing...")
        
        # Check available sources
        sources_available = self.check_sources_available()
        logger.info(f"Available sources: {sources_available}")
        
        # Research from manual input (default mode)
        report = self.research_from_manual_input(
            topic=topic,
            manual_links=manual_links,
            manual_items=manual_items,
            content_brief=content_brief
        )
        
        self.save_research_report()
        
        logger.info("NewsResearchAgent completed")
        return report


def run_news_research(
    topic: str,
    manual_links: List[str] = None,
    manual_items: List[Dict[str, Any]] = None,
    content_brief: str = ""
) -> Dict[str, Any]:
    """Convenience function to run news research."""
    agent = NewsResearchAgent()
    return agent.execute(topic, manual_links, manual_items, content_brief)
