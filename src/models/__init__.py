"""
Data models for the grant scanner.

All types are TypedDicts with Literal constraints — no Any usage.
"""

from typing import Optional, TypedDict
from typing import Literal


class Opportunity(TypedDict):
    """A single grant, fellowship, or funding opportunity."""

    name: str
    funder: str
    summary: str
    url: str

    # Deadline
    deadline: str                              # ISO "YYYY-MM-DD" or "rolling"
    deadline_type: Literal["fixed", "rolling", "estimated"]
    deadline_display: str                      # Human-readable

    # Funding amount
    amount_display: str                        # e.g. "USD 5.000 – USD 20.000"
    amount_usd_min: int
    amount_usd_max: int

    # Classification
    themes: list[str]
    type: str                                  # "grant" | "fellowship" | "fund" | "emergency"

    # Eligibility (core to the scanner's value)
    eligibility: str
    brazil_eligible: Optional[bool]
    eligibility_confidence: Literal["confirmed", "likely", "partial", "unverified"]
    eligibility_source: str
    eligible_regions: list[str]

    # Post-processing fields (set by classify_urgency / validate_links)
    urgency: str                               # "🔴" | "🟡" | "🟢" | "⚫"
    link_valid: bool


class Stats(TypedDict):
    """Pipeline execution statistics."""

    pass1_raw_count: int
    pass2_raw_count: int
    pre_eligibility_count: int
    confirmed_count: int
    unverified_count: int
    removed_count: int


class SearchResult(TypedDict):
    """Full result returned by run_grant_search()."""

    opportunities_confirmed: list[Opportunity]
    opportunities_unverified: list[Opportunity]
    opportunities: list[Opportunity]           # confirmed + unverified combined
    strategic_recommendations: list[dict[str, str]]
    generated_at: str                          # ISO datetime string
    model: str
    stats: Stats


__all__ = ["Opportunity", "SearchResult", "Stats"]
