"""
Email building and delivery.

Functions:
    markdown_to_html(md_text) -> str
    build_email_html(report_md, result) -> str
    send_email(sender, recipients, subject, html_body, plain_text, app_password) -> None
"""

import logging
import re
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import BRT
from src.models import SearchResult

logger = logging.getLogger(__name__)


def markdown_to_html(md_text: str) -> str:
    """Lightweight Markdown-to-HTML conversion for email rendering."""
    html = md_text

    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html = re.sub(
        r"^### (.+)$",
        r"<h3 style='color:#1a5276;margin-top:24px;margin-bottom:8px;'>\1</h3>",
        html,
        flags=re.MULTILINE,
    )
    html = re.sub(
        r"^## (.+)$",
        r"<h2 style='color:#1a5276;margin-top:32px;border-bottom:2px solid #e8e8e8;padding-bottom:8px;'>\1</h2>",
        html,
        flags=re.MULTILINE,
    )
    html = re.sub(
        r"^# (.+)$",
        r"<h1 style='color:#1a5276;'>\1</h1>",
        html,
        flags=re.MULTILINE,
    )

    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

    html = re.sub(
        r"\[([^\]]+)\]\((https?://[^\)]+)\)",
        r'<a href="\2" style="color:#2980b9;" target="_blank">\1</a>',
        html,
    )
    html = re.sub(
        r'(?<!href=")(https?://[^\s&lt;\)]+)',
        r'<a href="\1" style="color:#2980b9;" target="_blank">\1</a>',
        html,
    )

    html = re.sub(
        r"^- (.+)$",
        r"<li style='margin-bottom:4px;'>\1</li>",
        html,
        flags=re.MULTILINE,
    )
    html = re.sub(
        r"((?:<li[^>]*>.*?</li>\n?)+)",
        r"<ul style='margin:8px 0;padding-left:20px;'>\1</ul>",
        html,
    )

    html = re.sub(
        r"^---+$",
        r"<hr style='border:none;border-top:2px solid #e8e8e8;margin:24px 0;'>",
        html,
        flags=re.MULTILINE,
    )

    html = re.sub(r"\n\n", r"</p><p style='line-height:1.6;margin:8px 0;'>", html)
    html = html.replace("\n", "<br>\n")
    html = f"<p style='line-height:1.6;margin:8px 0;'>{html}</p>"

    return html


def build_email_html(report_md: str, result: SearchResult) -> str:
    """Build a complete styled HTML email from the Markdown report."""
    today = datetime.now(BRT).strftime("%d/%m/%Y")

    confirmed = result.get("opportunities_confirmed", [])
    unverified = result.get("opportunities_unverified", [])
    all_opps = confirmed + unverified
    urgent_count = sum(1 for o in all_opps if o.get("urgency") == "🔴")

    report_html = markdown_to_html(report_md)

    # Urgent alerts (confirmed eligibility only)
    summary_items = [
        f"<li>🔴 <strong>{opp['name']}</strong> — {opp.get('deadline_display', 'Verificar')}</li>"
        for opp in all_opps
        if opp.get("urgency") == "🔴"
        and opp.get("eligibility_confidence") in ("confirmed", "likely")
    ]

    urgent_section = ""
    if summary_items:
        urgent_section = f"""
        <div style="background:#fff3cd;border-left:4px solid #ffc107;padding:12px 16px;margin-bottom:20px;border-radius:4px;">
            <strong>⚡ Prazos urgentes (próximos 30 dias) — elegibilidade confirmada:</strong>
            <ul style="margin:8px 0;padding-left:20px;">
                {"".join(summary_items)}
            </ul>
        </div>
        """

    stats = result.get("stats", {})
    removed = stats.get("removed_count", 0)

    unverified_line = (
        f"⚠️ {len(unverified)} oportunidades com elegibilidade a verificar manualmente<br>"
        if unverified
        else ""
    )
    removed_line = (
        f"❌ {removed} oportunidades removidas (Brasil não elegível)<br>"
        if removed > 0
        else ""
    )

    eligibility_note = f"""
        <div style="background:#e8f4f8;border-left:4px solid #17a2b8;padding:12px 16px;margin-bottom:20px;border-radius:4px;">
            <strong>🔍 Verificação de elegibilidade:</strong><br>
            ✅ {len(confirmed)} oportunidades com elegibilidade confirmada para o Brasil<br>
            {unverified_line}
            {removed_line}
            <em style="font-size:12px;">O sistema audita a elegibilidade geográfica de cada oportunidade
            para evitar falsos positivos.</em>
        </div>
        """

    dashboard_banner = """
        <div style="background:#eaf4ea;border-left:4px solid #27ae60;padding:12px 16px;margin-bottom:20px;border-radius:4px;text-align:center;">
            📊 Veja os dados de oportunidades agrupados no site
            <a href="https://reichaves.github.io/grant-scanner/"
               style="color:#1a7a3c;font-weight:bold;"
               target="_blank">https://reichaves.github.io/grant-scanner/</a>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;max-width:900px;margin:0 auto;
             padding:20px;color:#333;background-color:#f5f5f5;">

  <div style="background:linear-gradient(135deg, #1a5276, #2980b9);color:white;padding:28px 32px;border-radius:8px 8px 0 0;">
    <h1 style="margin:0;font-size:24px;">📡 Radar de Oportunidades — Abraji</h1>
    <p style="margin:8px 0 0;opacity:0.9;font-size:14px;">
      Relatório Automatizado de Grants &amp; Fellowships para Jornalismo · {today}
    </p>
    <p style="margin:4px 0 0;opacity:0.8;font-size:13px;">
      {len(all_opps)} oportunidades · {len(confirmed)} confirmadas · {urgent_count} urgentes
    </p>
  </div>

  <div style="background:white;padding:28px 32px;border-radius:0 0 8px 8px;
              box-shadow:0 2px 12px rgba(0,0,0,0.08);">

    {dashboard_banner}
    {eligibility_note}
    {urgent_section}
    {report_html}
  </div>

</body>
</html>"""


def send_email(
    sender: str,
    recipients: list[str],
    subject: str,
    html_body: str,
    plain_text: str,
    app_password: str,
) -> None:
    """Send HTML email via Gmail SMTP with App Password (port 465, SSL)."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Abraji Grant Scanner <{sender}>"
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg["Reply-To"] = sender

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    logger.info(f"Sending email to {len(recipients)} recipients via Gmail SMTP...")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_password)
            server.sendmail(sender, recipients, msg.as_string())
        logger.info("Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Gmail authentication failed. Check your App Password. "
            "Ensure 2FA is enabled and you're using an App Password."
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        sys.exit(1)


__all__ = ["markdown_to_html", "build_email_html", "send_email"]
