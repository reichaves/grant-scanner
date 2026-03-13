#!/usr/bin/env python3
"""
Grant Scanner v3 — Radar de Oportunidades para Jornalismo Investigativo

Author: Reinaldo Chaves (https://github.com/reichaves/grant-scanner)
License: MIT

Entry point only. All logic lives in src/.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from src.config import BRT, GEMINI_MODEL, PREVIOUS_REPORT_PATH, RECIPIENTS, SENDER_EMAIL
from src.pipeline import run_grant_search
from src.report import format_report_markdown
from src.report.email import build_email_html, send_email
from src.utils import save_report_data

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        logger.error(f"Environment variable '{name}' is not set.")
        sys.exit(1)
    return value


def main() -> None:
    logger.info("=" * 60)
    logger.info("GRANT SCANNER v3 — Starting execution")
    logger.info("=" * 60)

    gemini_api_key = _require_env("GEMINI_API_KEY")
    gmail_app_password = _require_env("GMAIL_APP_PASSWORD")

    # Step 1: Run the 3-pass AI-powered search
    result = run_grant_search(gemini_api_key)

    # Step 2: Format Markdown report
    report_md = format_report_markdown(result)

    # Step 3: Build subject line and send email
    today = datetime.now(BRT).strftime("%d/%m/%Y")
    confirmed = result.get("opportunities_confirmed", [])
    unverified = result.get("opportunities_unverified", [])
    all_opps = confirmed + unverified
    urgent_count = sum(1 for o in all_opps if o.get("urgency") == "🔴")

    subject = f"📡 Radar de Grants — Abraji — {today} ({len(confirmed)} confirmadas"
    if unverified:
        subject += f", {len(unverified)} a verificar"
    if urgent_count > 0:
        subject += f", {urgent_count} urgentes"
    subject += ")"

    html_body = build_email_html(report_md, result)
    plain_text = f"Radar de Oportunidades — Abraji — {today}\n\n{report_md}"

    send_email(SENDER_EMAIL, RECIPIENTS, subject, html_body, plain_text, gmail_app_password)

    # Step 4: Save artifacts
    report_path = Path("grant_report.md")
    report_path.write_text(
        f"# Radar de Oportunidades — Abraji — {today}\n\n{report_md}",
        encoding="utf-8",
    )
    logger.info(f"Markdown report saved to {report_path}")

    save_report_data(result)

    json_path = Path("grant_report.json")
    json_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"JSON report saved to {json_path}")

    logger.info("=" * 60)
    logger.info(
        f"GRANT SCANNER v3 — Done: {len(confirmed)} confirmed, "
        f"{len(unverified)} unverified, {urgent_count} urgent"
    )
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
