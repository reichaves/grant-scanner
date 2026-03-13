"""
Sources package — curated list of grant/fellowship websites to scan.

Aggregates entries from both spreadsheet tabs (Individual/Project + Institucional)
and provides a formatted block for injection into the Pass 2 prompt.

Usage:
    from src.sources import ALL_SOURCES, build_sources_block
"""

from .individual import INDIVIDUAL_SOURCES, Source
from .institutional import INSTITUTIONAL_SOURCES

# Deduplicate by URL while preserving order (individual tab first)
_seen_urls: set[str] = set()
ALL_SOURCES: list[Source] = []

for _source in INDIVIDUAL_SOURCES + INSTITUTIONAL_SOURCES:
    _url = _source["url"].rstrip("/")
    if _url not in _seen_urls:
        _seen_urls.add(_url)
        ALL_SOURCES.append(_source)


def build_sources_block() -> str:
    """
    Render ALL_SOURCES as a formatted checklist for prompt injection.

    The returned string is injected into the SECOND_PASS_PROMPT so the LLM
    visits each site explicitly instead of relying on reading the Google Sheet.
    """
    lines = [
        "LISTA DE FONTES CURADAS — visite CADA site abaixo e verifique oportunidades abertas:",
        "",
    ]
    for i, source in enumerate(ALL_SOURCES, 1):
        lines.append(f"{i:2d}. {source['name']}")
        lines.append(f"    URL: {source['url']}")
        lines.append(f"    Foco: {source['focus']}")
        lines.append("")
    return "\n".join(lines)


__all__ = ["ALL_SOURCES", "INDIVIDUAL_SOURCES", "INSTITUTIONAL_SOURCES", "Source", "build_sources_block"]
