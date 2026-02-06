#!/usr/bin/env python3
"""
Grant Scanner for Investigative Journalism Organizations in Latin America.

Automated daily search for funding opportunities using Google Gemini 3 Pro
with Google Search Grounding. Designed for GitHub Actions CI/CD.

Author: Reinaldo Chaves (https://github.com/reichaves/grant-scanner)
License: MIT
"""

import os
import sys
import re
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

BRT = timezone(timedelta(hours=-3))

SENDER_EMAIL = "reichaves@gmail.com"
RECIPIENTS = [
    "reinaldo@abraji.org.br",
    "anacarolinamoreno@abraji.org.br",
    "sergioludtke@abraji.org.br",
    "leticiakleim@abraji.org.br",
]

# ---------------------------------------------------------------------------
# Model: Gemini 3 Pro Preview or gemini-3-flash-preview
# Google's most advanced reasoning model with native Google Search Grounding.
# The model ID may be updated when Google releases the stable version.
# Check: https://ai.google.dev/gemini-api/docs/models
# ---------------------------------------------------------------------------
GEMINI_MODEL = "gemini-3-pro-preview"
#GEMINI_MODEL = "gemini-3-flash-preview"

SYSTEM_PROMPT = """Você é um Especialista Sênior em Fundraising e Desenvolvimento Institucional para organizações de mídia e jornalismo investigativo na América Latina.

Sua tarefa é realizar uma varredura profunda na web para identificar oportunidades de financiamento abertas ou previstas para o ciclo 2025-2026.

PARÂMETROS DE BUSCA:
1. Priorize oportunidades de fundações globais (ex: Open Society, Luminate, Ford Foundation, MacArthur, Knight Foundation, Bloomberg), 
agências de cooperação internacional (ex: USAID, Europaid, Norad, GIZ, SIDA, AFD), 
organizações de nicho (ex: Pulitzer Center, GIJN, Google News Initiative, Internews, Free Press Unlimited, DW Akademie, Reporters Without Borders, National Endowment for Democracy, IJ4EU) e 
e outras fundações e organizações brasileiras ou internacionais (Betty & Jacob Lafer, Fundação Tide Setubal, Instituto Serrapilheira, Fundação Lemann, Embaixada e Consulado dos EUA, Embaixada e Consulado do Canadá, Fundação Itaú.
2. Busque por termos-chave em inglês, espanhol e português:
   - "Call for proposals journalism 2025 2026"
   - "Investigative reporting grants Latin America"
   - "Media development funding open call"
   - "Fellowships for journalists 2025 2026"
   - "Edital jornalismo investigativo 2025 2026"
   - "Grant for data journalism"
   - "Environmental journalism funding"
   - "Press freedom grants"
   - "AI journalism grants"
   - "Grants for newsrooms Global South"
   - "Transparency and accountability grants Latin America"
   - "Anti-corruption journalism funding"
   - "Digital rights and democracy grants"
   - "Human rights defenders funding Brazil"
   - "Fact-checking and disinformation grants"
   - "Open data innovation funds"
   - "Collaborative journalism projects funding"
   - "Safety of journalists grants"
   - "Climate change media partnership"
   - "Civic tech for media development"
   - "Financiamento para defesa da liberdade de imprensa"
   - "Apoio ao jornalismo local e independente"
   - "Gender equity in media grants"
   - "Public interest technology funding"
   - "Edital projetos de transparência pública"
3. IGNORE oportunidades exclusivas para cidadãos dos EUA ou UE. Foque naquelas abertas a brasileiros, latino-americanos ou candidatos globais.

FILTRAGEM RIGOROSA:
- Inclua APENAS oportunidades com prazo de inscrição futuro OU recorrente (ciclo anual ainda não encerrado).
- Verifique a elegibilidade real — se a página oficial diz "US-only" ou "EU citizens only", exclua.
- Se não conseguir confirmar que o prazo está aberto, indique "Verificar no site" em vez de inventar uma data.

FORMATO DE SAÍDA (OBRIGATÓRIO — siga exatamente):

Para cada oportunidade, forneça:

### [Número]. Nome do Grant/Fundo
- **Financiador:** Nome da organização
- **Resumo Executivo:** O que financiam (reportagem individual, estrutura da redação, viagem, projeto de dados, etc.) — máx. 2 linhas
- **Valor do Financiamento:** Teto financeiro ou range (ex: USD 5.000 – USD 20.000). Se não disponível, escreva "Não divulgado"
- **Deadline (Prazo):** Data exata ou "Rolling/Contínuo" ou "Verificar no site — ciclo anterior encerrou em [data]"
- **Elegibilidade:** Confirme se brasileiros/latino-americanos são elegíveis
- **Link Direto:** URL para a página oficial de aplicação (NÃO a home page genérica)

IMPORTANTE:
- Encontre no MÍNIMO 10 oportunidades, idealmente 15-20 ou mais.
- NÃO invente informações. Se não tiver certeza de um dado, indique claramente.
- Inclua a data de hoje no cabeçalho do relatório.

AÇÃO FINAL:
Após a lista, sugira 3 passos estratégicos específicos e acionáveis para a Abraji (Associação Brasileira de Jornalismo Investigativo) aumentar suas chances de aprovação nos editais listados. Considere que a Abraji é uma organização estabelecida com mais de 20 anos, que organiza congressos, oferece treinamentos e desenvolve ferramentas de dados para jornalistas."""

USER_PROMPT_TEMPLATE = """Data de hoje: {today}

Execute a varredura completa de oportunidades de financiamento conforme as instruções do sistema. Busque ativamente na web por grants, fellowships e editais abertos ou previstos para jornalismo investigativo, mídia independente e projetos de dados/AI para jornalismo na América Latina, com foco em elegibilidade para organizações e profissionais brasileiros.

Faça buscas em múltiplos idiomas (EN, ES, PT) e em múltiplas fontes. Seja exaustivo."""


def get_env_var(name: str) -> str:
    """Retrieve a required environment variable or exit."""
    value = os.environ.get(name)
    if not value:
        logger.error(f"Environment variable '{name}' is not set.")
        sys.exit(1)
    return value


# ---------------------------------------------------------------------------
# Gemini API Call with Google Search Grounding
# ---------------------------------------------------------------------------

def run_grant_search(api_key: str) -> str:
    """
    Call Gemini 3 Pro Preview with Google Search Grounding to find grants.

    Uses the google-genai SDK with the Tool(google_search=GoogleSearch())
    pattern, which enables the model to perform real-time web searches during
    generation and ground its responses in actual search results.

    Ref: https://ai.google.dev/gemini-api/docs/google-search
    """
    client = genai.Client(api_key=api_key)
    today = datetime.now(BRT).strftime("%d/%m/%Y (%A)")

    logger.info(f"Starting grant search — model={GEMINI_MODEL}, date={today}")

    # Configure Google Search Grounding tool
    google_search_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[google_search_tool],
        temperature=0.1,           # Lower = more factual
        max_output_tokens=16000,   # Allow long, detailed output
        thinking_config=types.ThinkingConfig(
            thinking_level="HIGH"  # Enable deep reasoning for thorough search
        ),
    )

    user_prompt = USER_PROMPT_TEMPLATE.format(today=today)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt,
            config=config,
        )

        result_text = response.text

        if not result_text or not result_text.strip():
            logger.error("Empty response from Gemini API.")
            sys.exit(1)

        # Log grounding metadata if available
        if response.candidates and response.candidates[0].grounding_metadata:
            metadata = response.candidates[0].grounding_metadata
            if metadata.web_search_queries:
                logger.info(
                    f"Search queries used: {metadata.web_search_queries}"
                )
            if metadata.grounding_chunks:
                logger.info(
                    f"Grounding sources: {len(metadata.grounding_chunks)} chunks"
                )

        logger.info(f"Search completed — response length: {len(result_text)} chars")
        return result_text

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Email Sending via Gmail SMTP
# ---------------------------------------------------------------------------

def markdown_to_html(md_text: str) -> str:
    """Lightweight Markdown-to-HTML conversion for email rendering."""
    html = md_text

    # Escape HTML entities first
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Headers
    html = re.sub(
        r"^### (.+)$",
        r"<h3 style='color:#1a5276;margin-top:24px;'>\1</h3>",
        html, flags=re.MULTILINE,
    )
    html = re.sub(
        r"^## (.+)$",
        r"<h2 style='color:#1a5276;margin-top:28px;'>\1</h2>",
        html, flags=re.MULTILINE,
    )
    html = re.sub(
        r"^# (.+)$",
        r"<h1 style='color:#1a5276;'>\1</h1>",
        html, flags=re.MULTILINE,
    )

    # Bold
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)

    # Italic
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

    # Links — [text](url)
    html = re.sub(
        r"\[([^\]]+)\]\((https?://[^\)]+)\)",
        r'<a href="\2" style="color:#2980b9;" target="_blank">\1</a>',
        html,
    )

    # Bare URLs (not already inside an href)
    html = re.sub(
        r'(?<!href=")(https?://[^\s<\)]+)',
        r'<a href="\1" style="color:#2980b9;" target="_blank">\1</a>',
        html,
    )

    # Bullet points
    html = re.sub(
        r"^- (.+)$",
        r"<li style='margin-bottom:4px;'>\1</li>",
        html, flags=re.MULTILINE,
    )

    # Wrap consecutive <li> in <ul>
    html = re.sub(
        r"((?:<li[^>]*>.*?</li>\n?)+)",
        r"<ul style='margin:8px 0;padding-left:20px;'>\1</ul>",
        html,
    )

    # Horizontal rules
    html = re.sub(
        r"^---+$",
        r"<hr style='border:1px solid #ddd;margin:20px 0;'>",
        html, flags=re.MULTILINE,
    )

    # Paragraphs — double newlines
    html = re.sub(r"\n\n", r"</p><p style='line-height:1.6;'>", html)

    # Single newlines → <br>
    html = html.replace("\n", "<br>\n")

    # Wrap in paragraph
    html = f"<p style='line-height:1.6;'>{html}</p>"

    return html


def build_email_html(report: str) -> str:
    """Build a complete HTML email from the report."""
    today = datetime.now(BRT).strftime("%d/%m/%Y")
    report_html = markdown_to_html(report)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;max-width:900px;margin:0 auto;
             padding:20px;color:#333;background-color:#f9f9f9;">

  <div style="background:#1a5276;color:white;padding:24px 32px;border-radius:8px 8px 0 0;">
    <h1 style="margin:0;font-size:22px;">📡 Radar de Oportunidades — Abraji</h1>
    <p style="margin:8px 0 0;opacity:0.9;font-size:14px;">
      Relatório Automatizado de Grants &amp; Fellowships para Jornalismo · {today}
    </p>
  </div>

  <div style="background:white;padding:28px 32px;border-radius:0 0 8px 8px;
              box-shadow:0 2px 8px rgba(0,0,0,0.08);">
    {report_html}
  </div>

  <div style="text-align:center;padding:16px;font-size:12px;color:#888;margin-top:12px;">
    Gerado automaticamente via GitHub Actions · Powered by Google {GEMINI_MODEL}<br>
    Abraji — Associação Brasileira de Jornalismo Investigativo<br>
    <em>Este relatório usa IA e busca web automatizada.
    Sempre verifique os links e prazos nos sites oficiais.</em><br><br>
    Script criado por Reinaldo Chaves
    (<a href="https://github.com/reichaves/grant-scanner" style="color:#2980b9;">https://github.com/reichaves</a>)
  </div>

</body>
</html>"""


def send_email(
    sender: str,
    recipients: list[str],
    subject: str,
    html_body: str,
    app_password: str,
) -> None:
    """Send HTML email via Gmail SMTP with App Password."""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Abraji Grant Scanner <{sender}>"
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg["Reply-To"] = sender

    # Plain text fallback
    plain = "Este email requer um cliente com suporte a HTML. Abra no navegador."
    msg.attach(MIMEText(plain, "plain", "utf-8"))
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
            "Ensure 2FA is enabled and you're using an App Password, "
            "not your regular Gmail password."
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    logger.info("=" * 60)
    logger.info("GRANT SCANNER — Starting execution")
    logger.info("=" * 60)

    # Load secrets from environment
    gemini_api_key = get_env_var("GEMINI_API_KEY")
    gmail_app_password = get_env_var("GMAIL_APP_PASSWORD")

    # Step 1: Run the AI-powered web search
    report = run_grant_search(gemini_api_key)

    # Step 2: Build the email
    today = datetime.now(BRT).strftime("%d/%m/%Y")
    subject = f"📡 Radar de Grants — Abraji — {today}"
    html_body = build_email_html(report)

    # Step 3: Send the email
    send_email(SENDER_EMAIL, RECIPIENTS, subject, html_body, gmail_app_password)

    # Step 4: Also save the report as artifact (useful for debugging in GH Actions)
    report_path = "grant_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Radar de Oportunidades — Abraji — {today}\n\n")
        f.write(report)
    logger.info(f"Report saved to {report_path}")

    logger.info("=" * 60)
    logger.info("GRANT SCANNER — Execution completed successfully")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
