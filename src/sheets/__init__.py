"""
Google Sheets integration for the grant scanner.

Uploads newly discovered opportunities to a Google Sheet daily,
skipping any that already exist (deduplicated by URL).

Fetches the full sheet history to populate docs/data.json for
the GitHub Pages dashboard.
"""

import base64
import json
import logging
import os

from src.models import Opportunity

logger = logging.getLogger(__name__)

# Column headers — order must match _opp_to_row()
SHEET_HEADERS: list[str] = [
    "date_found",
    "name",
    "funder",
    "summary",
    "url",
    "deadline",
    "deadline_type",
    "deadline_display",
    "amount_display",
    "amount_usd_min",
    "amount_usd_max",
    "themes",
    "type",
    "eligibility",
    "brazil_eligible",
    "eligibility_confidence",
    "eligibility_source",
    "eligible_regions",
    "urgency",
    "link_valid",
]

_URL_COL = SHEET_HEADERS.index("url")


def _get_client():
    """Initialize gspread client from GOOGLE_SHEETS_CREDENTIALS env var."""
    try:
        import gspread
    except ImportError as exc:
        raise RuntimeError(
            "gspread is not installed. Run: pip install gspread>=6.0.0"
        ) from exc

    creds_raw = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    if not creds_raw:
        raise ValueError("GOOGLE_SHEETS_CREDENTIALS env var is not set")

    # Accept raw JSON or base64-encoded JSON
    try:
        creds_dict = json.loads(creds_raw)
    except json.JSONDecodeError:
        try:
            creds_dict = json.loads(base64.b64decode(creds_raw).decode())
        except Exception as exc:
            raise ValueError(
                "GOOGLE_SHEETS_CREDENTIALS must be valid JSON or base64-encoded JSON"
            ) from exc

    return gspread.service_account_from_dict(creds_dict)


def _normalize_url(url: str) -> str:
    """Strip query string and trailing slash for deduplication comparison."""
    return url.split("?")[0].rstrip("/").lower()


def _opp_to_row(opp: Opportunity, date_found: str) -> list:
    """Convert an Opportunity dict to a flat list matching SHEET_HEADERS order."""
    return [
        date_found,
        opp.get("name", ""),
        opp.get("funder", ""),
        opp.get("summary", ""),
        opp.get("url", ""),
        opp.get("deadline", ""),
        opp.get("deadline_type", ""),
        opp.get("deadline_display", ""),
        opp.get("amount_display", ""),
        opp.get("amount_usd_min", 0),
        opp.get("amount_usd_max", 0),
        ", ".join(opp.get("themes", [])),
        opp.get("type", ""),
        opp.get("eligibility", ""),
        str(opp.get("brazil_eligible", "")).lower(),
        opp.get("eligibility_confidence", ""),
        opp.get("eligibility_source", ""),
        ", ".join(opp.get("eligible_regions", [])),
        opp.get("urgency", ""),
        str(opp.get("link_valid", True)).lower(),
    ]


def upload_to_sheets(
    opportunities: list[Opportunity],
    spreadsheet_id: str,
    date_found: str,
    worksheet_name: str = "Oportunidades",
) -> tuple[int, int]:
    """
    Upload opportunities to Google Sheets, skipping duplicates by URL.

    Deduplication uses a normalized URL key (no query string, lowercase).

    Returns:
        (added_count, skipped_count)
    """
    client = _get_client()
    spreadsheet = client.open_by_key(spreadsheet_id)

    try:
        ws = spreadsheet.worksheet(worksheet_name)
    except Exception:
        ws = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows=5000,
            cols=len(SHEET_HEADERS),
        )

    existing_values = ws.get_all_values()

    if not existing_values:
        ws.append_row(SHEET_HEADERS, value_input_option="RAW")
        existing_url_set: set[str] = set()
    else:
        existing_url_set = {
            _normalize_url(row[_URL_COL])
            for row in existing_values[1:]
            if len(row) > _URL_COL and row[_URL_COL]
        }

    added = 0
    skipped = 0
    new_rows: list[list] = []

    for opp in opportunities:
        url_key = _normalize_url(opp.get("url", ""))
        if url_key and url_key in existing_url_set:
            logger.info(
                f"Sheets: duplicate skipped — '{opp.get('name')}' ({opp.get('url')})"
            )
            skipped += 1
        else:
            new_rows.append(_opp_to_row(opp, date_found))
            existing_url_set.add(url_key)
            added += 1

    if new_rows:
        ws.append_rows(new_rows, value_input_option="RAW")

    logger.info(f"Sheets: {added} new rows added, {skipped} duplicates skipped")
    return added, skipped


def fetch_all_from_sheets(
    spreadsheet_id: str,
    worksheet_name: str = "Oportunidades",
) -> list[dict]:
    """
    Fetch all rows from the spreadsheet as a list of dicts.

    Header row is used as dict keys. Used to populate docs/data.json
    for the GitHub Pages dashboard.
    """
    client = _get_client()
    spreadsheet = client.open_by_key(spreadsheet_id)

    try:
        ws = spreadsheet.worksheet(worksheet_name)
    except Exception:
        logger.warning(f"Worksheet '{worksheet_name}' not found — returning empty list")
        return []

    all_values = ws.get_all_values()
    if not all_values:
        return []

    # Use SHEET_HEADERS as keys if the first row looks like data (not a header)
    first_row = all_values[0]
    if first_row == SHEET_HEADERS:
        header = first_row
        data_rows = all_values[1:]
    else:
        header = SHEET_HEADERS
        data_rows = all_values

    return [
        dict(zip(header, row))
        for row in data_rows
        if any(cell.strip() for cell in row)
    ]


__all__ = ["upload_to_sheets", "fetch_all_from_sheets", "SHEET_HEADERS"]
