"""
DIL Content & Income Agent - News Content Agent

Creates draft content from news research results.
All content includes source attribution.
Never copies full articles.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.logger import get_logger

logger = get_logger(__name__)


class NewsContentAgent:
    """
    Agent that creates draft content from news research.
    
    Output formats:
    - Short news summary
    - Social media draft
    - Google-friendly article draft
    - Educational thread draft
    - Source list
    
    Rules:
    - Never copy full articles
    - Always cite sources
    - Separate facts from opinions
    - No misleading headlines
    - No hate speech
    """
    
    def __init__(self):
        """Initialize NewsContentAgent."""
        self.output_dir = Path("output/news")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.content_drafts: List[Dict[str, Any]] = []
    
    def load_research(self, research_file: str = "output/news/news_research_report.json") -> Dict[str, Any]:
        """Load news research from file."""
        try:
            path = Path(research_file)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading research: {e}")
        return {}
    
    def create_content_draft(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create content draft from a news source.
        
        Args:
            source: News source dictionary.
            
        Returns:
            Content draft dictionary.
        """
        title = source.get("title", "Berita")
        summary = source.get("summary", "")
        source_name = source.get("source_name", "")
        url = source.get("url", "")
        content_angle = source.get("content_angle", "")
        
        # Short summary
        short_summary = (
            f"**{title}**\n\n"
            f"{summary}\n\n"
            f"Sumber: {source_name}"
        )
        
        # Social media draft
        social_draft = (
            f"📰 {title}\n\n"
            f"{summary[:200]}{'...' if len(summary) > 200 else ''}\n\n"
            f"🔗 Sumber: {source_name}\n\n"
            f"#berita #teknologi #edukasi"
        )
        
        # Google-friendly article draft
        article_draft = (
            f"## {title}\n\n"
            f"**Ringkasan:**\n{summary}\n\n"
            f"**Konteks:**\n"
            f"Artikel ini merupakan ringkasan dan analisis singkat "
            f"dari berita yang diterbitkan oleh {source_name}. "
            f"Untuk informasi lengkap, silakan kunjungi sumber asli.\n\n"
            f"**Fakta Penting:**\n"
            f"- [Isi fakta penting dari berita]\n"
            f"- [Isi fakta tambahan]\n\n"
            f"**Analisis Singkat:**\n"
            f"[Isi analisis Anda tentang dampak atau konteks berita ini]\n\n"
            f"**Sumber:**\n"
            f"- [{source_name}]({url})"
        )
        
        # Educational thread draft
        thread_draft = (
            f"🧵 Thread: {title}\n\n"
            f"1/ Apa yang terjadi?\n"
            f"{summary[:150]}\n\n"
            f"2/ Mengapa penting?\n"
            f"[Isi analisis dampak]\n\n"
            f"3/ Apa pelajaran?\n"
            f"[Isi insight untuk pembaca]\n\n"
            f"4/ Sumber:\n"
            f"{source_name}: {url}"
        )
        
        draft = {
            "title": title,
            "source_name": source_name,
            "url": url,
            "short_summary": short_summary,
            "social_draft": social_draft,
            "article_draft": article_draft,
            "thread_draft": thread_draft,
            "content_angle": content_angle,
            "status": "draft",
            "approval_required": True,
            "created_at": datetime.now().isoformat()
        }
        
        return draft
    
    def create_all_drafts(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create content drafts for all sources."""
        drafts = []
        
        # If all sources are templates, create at least one template draft
        real_sources = [s for s in sources if s.get("source_type") != "template"]
        sources_to_use = real_sources if real_sources else sources

        for source in sources_to_use:
            draft = self.create_content_draft(source)
            drafts.append(draft)
            logger.info(f"Created draft for: {source.get('title', 'unknown')[:50]}")
        
        self.content_drafts = drafts
        return drafts
    
    def format_drafts_markdown(self, drafts: List[Dict[str, Any]], topic: str = "") -> str:
        """Format all drafts as markdown."""
        lines = [
            "# Draft Konten Berita",
            "",
            f"**Tanggal:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Topik:** {topic}",
            f"**Jumlah Draft:** {len(drafts)}",
            f"**Status:** DRAFT — Memerlukan review dan approval manusia",
            "",
            "---",
            ""
        ]
        
        if not drafts:
            lines.extend([
                "## Belum Ada Berita",
                "",
                "Tidak ada berita yang tersedia untuk membuat konten.",
                "Silakan jalankan mode `news_research` terlebih dahulu",
                "atau masukkan sumber berita secara manual.",
                ""
            ])
            return '\n'.join(lines)
        
        for i, draft in enumerate(drafts, 1):
            lines.extend([
                f"## Topik {i}: {draft['title']}",
                "",
                f"### Ringkasan Utama",
                "",
                draft['short_summary'],
                "",
                f"### Fakta Penting",
                "",
                "- [Isi fakta dari berita]",
                "- [Isi fakta tambahan]",
                "",
                f"### Konteks",
                "",
                f"Berita ini dari {draft['source_name']}. "
                f"{'Analisis: ' + draft['content_angle'] if draft['content_angle'] else 'Perlu analisis lebih lanjut.'}",
                "",
                f"### Draft Post Media Sosial",
                "",
                draft['social_draft'],
                "",
                f"### Draft Artikel Pendek",
                "",
                draft['article_draft'],
                "",
                f"### Draft Thread Edukatif",
                "",
                draft['thread_draft'],
                "",
                f"### Sumber",
                "",
                f"- [{draft['source_name']}]({draft['url']})",
                "",
                "---",
                ""
            ])
        
        # Source list
        lines.extend([
            "## Daftar Sumber Lengkap",
            ""
        ])
        
        for i, draft in enumerate(drafts, 1):
            lines.append(f"{i}. [{draft['source_name']}]({draft['url']})")
        
        lines.extend([
            "",
            "## Catatan Penting",
            "",
            "- Semua konten di atas adalah DRAFT",
            "- WAJIB review sebelum dipublikasikan",
            "- Jangan salin artikel penuh dari sumber",
            "- Kutipan langsung maksimal 50 kata",
            "- Wajib cantumkan sumber",
            "- Pisahkan fakta dan opini",
            "- Jangan buat judul menyesatkan",
            "- Posting hanya setelah approval manusia",
            ""
        ])
        
        return '\n'.join(lines)
    
    def save_drafts(self, topic: str = "") -> None:
        """Save content drafts to markdown file."""
        markdown = self.format_drafts_markdown(self.content_drafts, topic)
        output_path = self.output_dir / "news_content_drafts.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        logger.info(f"News content drafts saved to {output_path}")
    
    def execute(self, research_data: Dict[str, Any] = None) -> str:
        """
        Execute news content creation.
        
        Args:
            research_data: Research data. If None, loads from file.
            
        Returns:
            Markdown content.
        """
        logger.info("NewsContentAgent executing...")
        
        if research_data is None:
            research_data = self.load_research()
        
        topic = research_data.get("topic", "Berita Terkini")
        sources = research_data.get("sources", [])
        
        if not sources:
            logger.warning("No news sources found - creating template draft")
        
        drafts = self.create_all_drafts(sources)
        self.save_drafts(topic)
        
        markdown = self.format_drafts_markdown(drafts, topic)
        
        logger.info(f"NewsContentAgent completed: {len(drafts)} drafts created")
        return markdown


def run_news_content(research_data: Dict[str, Any] = None) -> str:
    """Convenience function to run news content creation."""
    agent = NewsContentAgent()
    return agent.execute(research_data)
