"""
Pipeline package — orchestrates the 3-pass grant search.

Entry point: run_grant_search(api_key) -> SearchResult
"""

import logging
from datetime import datetime

from google import genai

from src.config import BRT, GEMINI_MODEL
from src.models import Opportunity, SearchResult, Stats
from src.utils import (
    apply_audit_results,
    classify_urgency,
    deduplicate_opportunities,
    filter_by_eligibility,
    sort_opportunities,
    validate_links,
    validate_opportunity,
)
from .search import run_pass1, run_pass2
from .audit import run_pass3

logger = logging.getLogger(__name__)


def run_grant_search(api_key: str) -> SearchResult:
    """
    Execute the full 3-pass grant search pipeline.

    Pass 1: Broad sweep via Google Search + Gemini
    Pass 2: Targeted search for missed sources (includes curated source list)
    Pass 3: Adversarial eligibility audit

    Returns a SearchResult with confirmed, unverified, and combined opportunity lists.
    """
    client = genai.Client(api_key=api_key)
    today_dt = datetime.now(BRT)
    today = today_dt.strftime("%d/%m/%Y (%A)")

    # --- Pass 1 ---
    pass1_opps, all_recommendations = run_pass1(client, today)
    pass1_raw_count = len(pass1_opps)

    # --- Pass 2 ---
    found_names = "\n".join(
        f"- {opp.get('name', 'Unknown')}" for opp in pass1_opps
    )
    pass2_opps, pass2_recs = run_pass2(client, today, found_names)
    pass2_raw_count = len(pass2_opps)

    if not all_recommendations and pass2_recs:
        all_recommendations = pass2_recs

    all_opportunities: list[Opportunity] = pass1_opps + pass2_opps

    # --- Post-processing before audit ---
    all_opportunities = [validate_opportunity(opp) for opp in all_opportunities]
    all_opportunities = deduplicate_opportunities(all_opportunities)
    all_opportunities = [
        opp for opp in all_opportunities if classify_urgency(opp, today_dt) != "⚫"
    ]

    # --- Pass 3: adversarial eligibility audit ---
    audit_results = run_pass3(client, today, all_opportunities)
    if audit_results:
        all_opportunities = apply_audit_results(all_opportunities, audit_results)

    # --- Final post-processing ---
    all_opportunities = validate_links(all_opportunities)

    for opp in all_opportunities:
        opp["urgency"] = classify_urgency(opp, today_dt)

    all_opportunities = sort_opportunities(all_opportunities, today_dt)
    confirmed, unverified = filter_by_eligibility(all_opportunities)

    logger.info(
        f"Final: {len(confirmed)} confirmed + {len(unverified)} unverified = "
        f"{len(confirmed) + len(unverified)} total"
    )

    stats: Stats = {
        "pass1_raw_count": pass1_raw_count,
        "pass2_raw_count": pass2_raw_count,
        "pre_eligibility_count": len(all_opportunities),
        "confirmed_count": len(confirmed),
        "unverified_count": len(unverified),
        "removed_count": len(all_opportunities) - len(confirmed) - len(unverified),
    }

    return SearchResult(
        opportunities_confirmed=confirmed,
        opportunities_unverified=unverified,
        opportunities=confirmed + unverified,
        strategic_recommendations=all_recommendations,
        generated_at=today_dt.isoformat(),
        model=GEMINI_MODEL,
        stats=stats,
    )


__all__ = ["run_grant_search"]
