"""
Pass 3 of the grant search pipeline: adversarial eligibility audit.

Acts as a skeptic auditor that tries to DISPROVE eligibility, catching
grants like UNDP "Agents of Change" that look valid but are region-restricted.
"""

import logging

from google import genai
from google.genai import types

from src.config import GEMINI_MODEL
from src.models import Opportunity
from src.prompts import build_audit_prompt
from src.utils import extract_json_from_response

logger = logging.getLogger(__name__)


def _make_audit_config() -> types.GenerateContentConfig:
    """Build the GenerateContentConfig for Pass 3 (no system instruction, temp=0)."""
    return types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.0,  # Maximum factuality for the audit
        max_output_tokens=32768,
        thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
    )


def run_pass3(
    client: genai.Client, today: str, opportunities: list[Opportunity]
) -> list[dict]:
    """
    Execute Pass 3: adversarial eligibility audit.

    Receives the combined Pass 1+2 opportunity list, returns a list of
    audit result dicts (to be merged by apply_audit_results).
    """
    logger.info("PASS 3: Adversarial eligibility audit")

    audit_list = "\n".join(
        f"{i + 1}. {opp.get('name', 'Unknown')} — Financiador: {opp.get('funder', 'Unknown')} — "
        f"URL: {opp.get('url', 'N/A')} — "
        f"Elegibilidade declarada: {opp.get('eligibility', 'N/A')} — "
        f"Regiões declaradas: {', '.join(opp.get('eligible_regions', ['N/A']))}"
        for i, opp in enumerate(opportunities)
    )

    audit_prompt = build_audit_prompt(today, audit_list)
    audit_config = _make_audit_config()

    try:
        response3 = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=audit_prompt,
            config=audit_config,
        )

        # Log grounding inline to avoid circular import
        try:
            if response3.candidates and response3.candidates[0].grounding_metadata:
                md = response3.candidates[0].grounding_metadata
                if md.web_search_queries:
                    logger.info(f"Audit search queries: {md.web_search_queries}")
        except Exception:
            pass

        audit_data = extract_json_from_response(response3.text)

        if audit_data and "audit_results" in audit_data:
            results: list[dict] = audit_data["audit_results"]
            logger.info(f"Pass 3 audited {len(results)} opportunities")

            disqualified = sum(1 for ar in results if ar.get("brazil_eligible") is False)
            if disqualified > 0:
                logger.info(f"Pass 3 disqualified {disqualified} opportunities")

            return results

        logger.warning("Pass 3: Could not parse audit results. Continuing without audit.")
        return []

    except Exception as e:
        logger.warning(f"Pass 3 (audit) failed (non-fatal): {e}")
        return []


__all__ = ["run_pass3"]
