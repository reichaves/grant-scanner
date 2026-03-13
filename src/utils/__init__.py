"""
Utility functions for the grant scanner pipeline.

Pure functions: JSON parsing, opportunity validation/normalization,
urgency classification, deduplication, sorting, eligibility filtering,
link validation, and persistence helpers.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import BRT, PREVIOUS_REPORT_PATH
from src.models import Opportunity, SearchResult

logger = logging.getLogger(__name__)

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------


def _recover_truncated_json(text: str) -> Optional[dict]:
    """
    Attempt to recover a truncated JSON string by closing unclosed structures.

    Handles the common case where the LLM response was cut off mid-JSON due to
    max_output_tokens being reached.
    """
    stack: list[str] = []
    in_string = False
    escape_next = False

    for char in text:
        if escape_next:
            escape_next = False
            continue
        if char == "\\" and in_string:
            escape_next = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char in "{[":
            stack.append(char)
        elif char in "}]":
            if stack:
                stack.pop()

    if not stack:
        return None  # No unclosed structures; truncation recovery not applicable

    closing = ('"' if in_string else "") + "".join(
        "}" if c == "{" else "]" for c in reversed(stack)
    )
    try:
        recovered = json.loads(text + closing)
        logger.warning(
            f"Truncated JSON recovered: closed {len(stack)} unclosed structure(s). "
            f"Original length: {len(text)} chars."
        )
        return recovered
    except json.JSONDecodeError:
        return None


def extract_json_from_response(text: str) -> Optional[dict]:
    """Extract and parse JSON from LLM response, handling markdown fences and truncation."""
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        candidate = match.group()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            recovered = _recover_truncated_json(candidate)
            if recovered:
                return recovered

    recovered = _recover_truncated_json(text)
    if recovered:
        return recovered

    logger.warning(
        f"Could not parse JSON from response "
        f"(length: {len(text)} chars, tail: ...{text[-120:]!r})"
    )
    return None


# ---------------------------------------------------------------------------
# Opportunity normalization
# ---------------------------------------------------------------------------


def validate_opportunity(opp: dict) -> Opportunity:
    """Validate and normalize a raw opportunity dict from the LLM response."""
    for field in ("name", "funder", "summary", "url"):
        if field not in opp or not opp[field]:
            opp[field] = "⚠️ Não informado"

    if "deadline" not in opp:
        opp["deadline"] = "rolling"
        opp["deadline_type"] = "rolling"
        opp["deadline_display"] = "Fluxo contínuo"

    if "deadline_type" not in opp:
        opp["deadline_type"] = (
            "fixed" if str(opp.get("deadline", "")).count("-") == 2 else "rolling"
        )

    if "deadline_display" not in opp:
        opp["deadline_display"] = opp.get("deadline", "Verificar no site")

    if "amount_display" not in opp or not opp["amount_display"]:
        opp["amount_display"] = "Não divulgado"

    for field in ("amount_usd_min", "amount_usd_max"):
        if field not in opp:
            opp[field] = 0

    if "themes" not in opp:
        opp["themes"] = []

    if "type" not in opp:
        opp["type"] = "grant"

    if "eligibility" not in opp:
        opp["eligibility"] = "Verificar no site"

    if "eligibility_confidence" not in opp:
        opp["eligibility_confidence"] = "unverified"

    if "eligibility_source" not in opp:
        opp["eligibility_source"] = ""

    if "eligible_regions" not in opp:
        opp["eligible_regions"] = []

    if "brazil_eligible" not in opp:
        opp["brazil_eligible"] = None

    if "urgency" not in opp:
        opp["urgency"] = "🟢"

    if "link_valid" not in opp:
        opp["link_valid"] = True

    return opp  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------


def classify_urgency(opp: Opportunity, today: datetime) -> str:
    """Return urgency emoji based on deadline proximity."""
    if opp.get("deadline_type") == "rolling":
        return "🟢"

    deadline_str = opp.get("deadline", "")
    if not deadline_str or deadline_str == "rolling" or "verificar" in deadline_str.lower():
        return "🟢"

    try:
        deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").replace(tzinfo=BRT)
        days_until = (deadline_date - today).days

        if days_until < 0:
            return "⚫"
        elif days_until <= 30:
            return "🔴"
        elif days_until <= 90:
            return "🟡"
        else:
            return "🟢"
    except ValueError:
        return "🟢"


def classify_eligibility_display(opp: Opportunity) -> str:
    """Return display emoji for eligibility confidence level."""
    conf = opp.get("eligibility_confidence", "unverified")
    if conf in ("confirmed", "likely"):
        return "✅"
    elif conf == "partial":
        return "🔗"
    return "⚠️"


# ---------------------------------------------------------------------------
# List operations
# ---------------------------------------------------------------------------


def deduplicate_opportunities(opps: list[Opportunity]) -> list[Opportunity]:
    """Remove duplicate opportunities based on name similarity."""
    seen: dict[str, bool] = {}
    unique: list[Opportunity] = []

    for opp in opps:
        key = re.sub(r"[^a-z0-9]", "", opp.get("name", "").lower())
        short_key = key[:30]

        if key not in seen and short_key not in seen:
            seen[key] = True
            seen[short_key] = True
            unique.append(opp)
        else:
            logger.info(f"Dedup: removed duplicate '{opp.get('name', 'unknown')}'")

    return unique


def sort_opportunities(opps: list[Opportunity], today: datetime) -> list[Opportunity]:
    """Sort opportunities: urgent first, then by deadline, rolling last."""

    def sort_key(opp: Opportunity) -> tuple[int, datetime]:
        deadline_str = opp.get("deadline", "")
        if opp.get("deadline_type") == "rolling" or deadline_str == "rolling":
            return (2, datetime(2099, 12, 31, tzinfo=BRT))
        try:
            d = datetime.strptime(deadline_str, "%Y-%m-%d").replace(tzinfo=BRT)
            return (0 if (d - today).days <= 30 else 1, d)
        except ValueError:
            return (2, datetime(2099, 12, 31, tzinfo=BRT))

    return sorted(opps, key=sort_key)


def filter_by_eligibility(
    opps: list[Opportunity],
) -> tuple[list[Opportunity], list[Opportunity]]:
    """
    Split opportunities into confirmed and unverified sections.

    Returns:
        (confirmed_list, unverified_list)

    Opportunities with brazil_eligible=False are silently dropped (never shown).
    """
    confirmed: list[Opportunity] = []
    unverified: list[Opportunity] = []

    for opp in opps:
        if opp.get("brazil_eligible") is False:
            logger.info(
                f"Eligibility filter: REMOVED '{opp.get('name')}' "
                f"(brazil_eligible=false, reason: {opp.get('eligibility', 'N/A')})"
            )
            continue

        confidence = opp.get("eligibility_confidence", "unverified")

        if confidence in ("confirmed", "likely") and opp.get("brazil_eligible") is True:
            confirmed.append(opp)
        else:
            # "partial", "unverified", or brazil_eligible is None
            unverified.append(opp)

    logger.info(
        f"Eligibility filter: {len(confirmed)} confirmed, "
        f"{len(unverified)} unverified, "
        f"{len(opps) - len(confirmed) - len(unverified)} removed"
    )
    return confirmed, unverified


def apply_audit_results(
    opps: list[Opportunity], audit_results: list[dict]
) -> list[Opportunity]:
    """Merge Pass 3 audit findings back into the opportunity list."""
    audit_map: dict[str, dict] = {}
    for ar in audit_results:
        key = re.sub(r"[^a-z0-9]", "", ar.get("name", "").lower())
        audit_map[key] = ar

    updated: list[Opportunity] = []
    for opp in opps:
        key = re.sub(r"[^a-z0-9]", "", opp.get("name", "").lower())

        if key in audit_map:
            ar = audit_map[key]

            if ar.get("brazil_eligible") is False:
                opp["brazil_eligible"] = False
                opp["eligibility_confidence"] = "confirmed"
                opp["eligibility"] = opp["eligibility"] + (
                    f" — ❌ AUDITORIA: {ar.get('disqualification_reason', 'Brasil não elegível')}"
                )
                logger.info(
                    f"Audit override: '{opp.get('name')}' marked as INELIGIBLE — "
                    f"{ar.get('disqualification_reason', 'no reason')}"
                )

            elif ar.get("brazil_eligible") is True:
                audit_conf = ar.get("eligibility_confidence")

                if audit_conf == "partial":
                    opp["eligibility_confidence"] = "partial"
                    opp["brazil_eligible"] = True
                    if ar.get("audit_notes"):
                        opp["eligibility_source"] = ar["audit_notes"]
                    logger.info(
                        f"Audit downgrade: '{opp.get('name')}' → 'partial' (partner-only grant)"
                    )

                elif audit_conf == "confirmed":
                    opp["eligibility_confidence"] = "confirmed"
                    opp["brazil_eligible"] = True
                    if ar.get("audit_notes"):
                        opp["eligibility_source"] = ar["audit_notes"]

            if ar.get("eligible_regions_found"):
                opp["eligible_regions"] = ar["eligible_regions_found"]

        updated.append(opp)

    return updated


# ---------------------------------------------------------------------------
# Link validation
# ---------------------------------------------------------------------------


def validate_links(opps: list[Opportunity]) -> list[Opportunity]:
    """Check if URLs are reachable via HTTP HEAD. Mark broken ones."""
    if not _HAS_REQUESTS:
        logger.info("Skipping link validation (requests not installed)")
        return opps

    for opp in opps:
        url = opp.get("url", "")
        if not url or url.startswith("⚠️"):
            continue

        if not url.startswith("http"):
            opp["url"] = f"https://{url}"
            url = opp["url"]

        try:
            resp = requests.head(
                url,
                timeout=10,
                allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 Grant-Scanner/3.0"},
            )
            opp["link_valid"] = resp.status_code < 400
            if resp.status_code >= 400:
                opp["url"] = f"{url} ⚠️ (HTTP {resp.status_code} — verificar manualmente)"
                logger.warning(f"Broken link ({resp.status_code}): {url}")
        except requests.RequestException as e:
            opp["link_valid"] = False
            opp["url"] = f"{url} ⚠️ (não acessível — verificar manualmente)"
            logger.warning(f"Link check failed for {url}: {e}")

    return opps


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def save_report_data(result: SearchResult, path: str = PREVIOUS_REPORT_PATH) -> None:
    """Persist structured report data to disk for comparison in next run."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"Report data saved to {path}")
    except Exception as e:
        logger.warning(f"Could not save report data: {e}")


def load_previous_report(path: str = PREVIOUS_REPORT_PATH) -> Optional[SearchResult]:
    """Load previous run data if available."""
    try:
        if Path(path).exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load previous report: {e}")
    return None


__all__ = [
    "extract_json_from_response",
    "validate_opportunity",
    "classify_urgency",
    "classify_eligibility_display",
    "deduplicate_opportunities",
    "sort_opportunities",
    "filter_by_eligibility",
    "apply_audit_results",
    "validate_links",
    "save_report_data",
    "load_previous_report",
]
