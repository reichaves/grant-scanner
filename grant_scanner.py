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
from typing import Optional

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

    # Step 5: Upload to Google Sheets and refresh GitHub Pages data
    _upload_to_sheets_and_export(all_opps, result)

    logger.info("=" * 60)
    logger.info(
        f"GRANT SCANNER v3 — Done: {len(confirmed)} confirmed, "
        f"{len(unverified)} unverified, {urgent_count} urgent"
    )
    logger.info("=" * 60)


def _upload_to_sheets_and_export(
    opportunities: list, result: dict
) -> None:
    """Upload today's opportunities to Google Sheets and write docs/data.json."""
    sheets_id: Optional[str] = os.environ.get("GOOGLE_SHEET_ID")
    sheets_creds: Optional[str] = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")

    if not sheets_id or not sheets_creds:
        logger.info(
            "Skipping Google Sheets upload "
            "(GOOGLE_SHEET_ID or GOOGLE_SHEETS_CREDENTIALS not configured)"
        )
        return

    try:
        from src.sheets import fetch_all_from_sheets, upload_to_sheets

        date_found = datetime.now(BRT).strftime("%Y-%m-%d")
        added, skipped = upload_to_sheets(opportunities, sheets_id, date_found)
        logger.info(f"Sheets: {added} added, {skipped} skipped")

        # Fetch the full accumulated history and write docs/data.json
        all_historical = fetch_all_from_sheets(sheets_id)
        docs_path = Path("docs/data.json")
        docs_path.parent.mkdir(exist_ok=True)
        docs_path.write_text(
            json.dumps(
                {
                    "generated_at": datetime.now(BRT).isoformat(),
                    "opportunities": all_historical,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        logger.info(
            f"Dashboard data saved to {docs_path} "
            f"({len(all_historical)} total opportunities)"
        )
    except Exception as exc:
        logger.error(f"Sheets upload failed: {exc}")


if __name__ == "__main__":
    main()
