"""
Pass 1 and Pass 2 of the grant search pipeline.

Pass 1: broad sweep via SYSTEM_PROMPT + user prompt
Pass 2: targeted search for sources NOT found in Pass 1, with explicit source list
"""

import logging
import sys
from datetime import datetime

from google import genai
from google.genai import types

from src.config import BRT, GEMINI_MODEL
from src.models import Opportunity
from src.prompts import build_user_prompt, build_second_pass_prompt, SYSTEM_PROMPT
from src.sources import build_sources_block
from src.utils import extract_json_from_response

logger = logging.getLogger(__name__)


def _log_grounding_metadata(response) -> None:  # noqa: ANN001
    """Log Google Search grounding metadata from an API response."""
    try:
        if response.candidates and response.candidates[0].grounding_metadata:
            metadata = response.candidates[0].grounding_metadata
            if metadata.web_search_queries:
                logger.info(f"Search queries: {metadata.web_search_queries}")
            if metadata.grounding_chunks:
                logger.info(f"Grounding sources: {len(metadata.grounding_chunks)} chunks")
    except Exception:
        pass


def _make_search_config(today: str) -> types.GenerateContentConfig:
    """Build the shared GenerateContentConfig for Pass 1 and Pass 2."""
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT.format(today=today),
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.1,
        max_output_tokens=65536,
        thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
    )


def run_pass1(
    client: genai.Client, today: str
) -> tuple[list[Opportunity], list[dict]]:
    """
    Execute Pass 1: broad sweep.

    Returns:
        (opportunities, strategic_recommendations)
    """
    logger.info(f"PASS 1: Broad sweep — model={GEMINI_MODEL}, date={today}")
    config = _make_search_config(today)
    user_prompt = build_user_prompt(today)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt,
            config=config,
        )
        _log_grounding_metadata(response)
        data = extract_json_from_response(response.text)

        if data and "opportunities" in data:
            opps: list[Opportunity] = data["opportunities"]
            recs: list[dict] = data.get("strategic_recommendations", [])
            logger.info(f"Pass 1 found {len(opps)} opportunities")
            return opps, recs

        logger.warning(
            "Pass 1: Could not parse structured data. "
            "Continuing to Pass 2 (Pass 1 results will be empty)."
        )
        return [], []

    except Exception as e:
        logger.error(f"Gemini API error (Pass 1): {e}")
        sys.exit(1)


def run_pass2(
    client: genai.Client,
    today: str,
    found_names: str,
) -> tuple[list[Opportunity], list[dict]]:
    """
    Execute Pass 2: targeted search for missed opportunities.

    Injects the curated source list (from spreadsheet tabs) so the LLM
    visits each site explicitly.

    Returns:
        (new_opportunities, strategic_recommendations_fallback)
    """
    logger.info("PASS 2: Targeted search for missed opportunities")
    config = _make_search_config(today)
    sources_block = build_sources_block()
    second_prompt = build_second_pass_prompt(today, found_names, sources_block)

    try:
        response2 = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=second_prompt,
            config=config,
        )
        _log_grounding_metadata(response2)
        data2 = extract_json_from_response(response2.text)

        if data2 and "opportunities" in data2:
            opps2: list[Opportunity] = data2["opportunities"]
            recs2: list[dict] = data2.get("strategic_recommendations", [])
            logger.info(f"Pass 2 found {len(opps2)} additional opportunities")
            return opps2, recs2

        return [], []

    except Exception as e:
        logger.warning(f"Pass 2 failed (non-fatal): {e}")
        return [], []


__all__ = ["run_pass1", "run_pass2"]
