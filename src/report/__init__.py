"""
Report package — Markdown report formatting.

Entry point: format_report_markdown(result) -> str
"""

import logging
from datetime import datetime

from src.config import BRT, GEMINI_MODEL, HEADER_TEMPLATE, FOOTER_TEMPLATE
from src.models import Opportunity, SearchResult
from src.utils import classify_eligibility_display

logger = logging.getLogger(__name__)


def _format_opportunity(num: int, opp: Opportunity) -> list[str]:
    """Format a single opportunity as a list of Markdown lines."""
    urgency = opp.get("urgency", "🟢")
    elig_icon = classify_eligibility_display(opp)
    confidence = opp.get("eligibility_confidence", "unverified")

    lines: list[str] = []
    lines.append(f"### {urgency} {num}. {opp['name']}\n")
    lines.append(f"**Financiador:** {opp['funder']}\n")
    lines.append(f"**Resumo Executivo:** {opp['summary']}\n")
    lines.append(f"**Valor do Financiamento:** {opp['amount_display']}\n")
    lines.append(f"**Deadline (Prazo):** {opp['deadline_display']}\n")
    lines.append(f"**Elegibilidade:** {elig_icon} {opp['eligibility']}\n")

    regions = opp.get("eligible_regions", [])
    if regions:
        lines.append(f"**Regiões elegíveis:** {', '.join(regions)}\n")

    if confidence == "partial":
        lines.append("**⚠️ Nota:** Brasil elegível como PARCEIRO, não como aplicante principal.\n")

    lines.append(f"**Tipo:** {opp.get('type', 'grant').capitalize()}\n")

    themes = opp.get("themes", [])
    if themes:
        lines.append(f"**Temas:** {', '.join(themes)}\n")

    lines.append(f"**Link Direto:** {opp['url']}\n")

    source = opp.get("eligibility_source", "")
    if source and source != opp.get("url", ""):
        lines.append(f"**Fonte de elegibilidade:** {source}\n")

    lines.append("")
    return lines


def format_report_markdown(result: SearchResult) -> str:
    """Format the SearchResult into a full Markdown report."""
    if result.get("parse_failed"):
        return result.get("raw_text", "Erro ao gerar relatório.")  # type: ignore[return-value]

    today_dt = datetime.now(BRT)
    today = today_dt.strftime("%d/%m/%Y")
    year = today_dt.strftime("%Y")

    confirmed = result.get("opportunities_confirmed", [])
    unverified = result.get("opportunities_unverified", [])
    all_opps = confirmed + unverified

    urgent_count = sum(1 for o in all_opps if o.get("urgency") == "🔴")

    header = HEADER_TEMPLATE.format(
        today=today,
        year=year,
        total_count=len(all_opps),
        confirmed_count=len(confirmed),
        unverified_count=len(unverified),
        urgent_count=urgent_count,
    )

    lines: list[str] = [header, "---\n"]

    if confirmed:
        lines.append("## ✅ OPORTUNIDADES COM ELEGIBILIDADE CONFIRMADA\n")
        lines.append(
            "*Elegibilidade para organizações/profissionais brasileiros verificada na fonte oficial.*\n"
        )
        for i, opp in enumerate(confirmed, 1):
            lines.extend(_format_opportunity(i, opp))

    if unverified:
        lines.append("---\n")
        lines.append("## ⚠️ OPORTUNIDADES COM ELEGIBILIDADE A VERIFICAR\n")
        lines.append(
            "*A elegibilidade para o Brasil não pôde ser confirmada automaticamente. "
            "Verifique nos links oficiais antes de investir tempo na aplicação.*\n"
        )
        for i, opp in enumerate(unverified, len(confirmed) + 1):
            lines.extend(_format_opportunity(i, opp))

    recs = result.get("strategic_recommendations", [])
    if recs:
        lines.append("---\n")
        lines.append("## 3 PASSOS ESTRATÉGICOS PARA A ABRAJI\n")

        for i, rec in enumerate(recs, 1):
            title = rec.get("title", f"Recomendação {i}")
            action = rec.get("action", "")
            strategy = rec.get("strategy", "")
            relevant = rec.get("relevant_opportunities", [])
            deadline = rec.get("deadline_action", "")

            lines.append(f"### {i}. {title}\n")
            lines.append(f"**Ação:** {action}\n")
            lines.append(f"**Estratégia:** {strategy}\n")
            if relevant:
                lines.append(f"**Editais relacionados:** {', '.join(relevant)}\n")
            if deadline:
                lines.append(f"**Começar preparação até:** {deadline}\n")
            lines.append("")

    lines.append(FOOTER_TEMPLATE.format(model=GEMINI_MODEL))

    return "\n".join(lines)


__all__ = ["format_report_markdown"]
