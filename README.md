# 📡 Grant Scanner — Abraji

**Monitor Automatizado de Oportunidades de Financiamento para Jornalismo Investigativo**

Um workflow GitHub Actions que usa Google Gemini com busca na web para identificar, verificar e reportar diariamente grants, fellowships e editais para jornalismo investigativo. Executa automaticamente de segunda a sexta às **07:00 BRT** e entrega relatórios curados por e-mail.

Desenvolvido para a [Abraji](https://abraji.org.br/) (Associação Brasileira de Jornalismo Investigativo).

---

## Como funciona

O sistema realiza **três passagens** sequenciais com o modelo Gemini, com busca na web em tempo real:

```
Pass 1 (Varredura ampla)
  → 12–20 oportunidades identificadas

Pass 2 (Busca complementar)
  → Oportunidades adicionais não encontradas na Pass 1
  → Foco em editais brasileiros, tech, fellowships, fundos climáticos

Pass 3 (Auditoria adversarial de elegibilidade)
  → Age como auditor CÉTICO, tentando REFUTAR a elegibilidade
  → Verifica a página oficial de cada oportunidade
  → Remove oportunidades onde o Brasil confirmadamente não é elegível

→ Validação de links, classificação de urgência, formatação e envio por e-mail
```

### Fontes consultadas em cada sessão

Além da busca livre na web, o sistema consulta **obrigatoriamente** a cada execução:

- [Grants for Journalists](https://grantsforjournalists.com/) — base de dados curada de grants para jornalistas
- [Planilha de oportunidades de financiamento](https://docs.google.com/spreadsheets/d/1vQs72vGfa2_LWBNMbVAr3WCeusTGrAIKSjkGtTR84Xo/edit?gid=380145027) — planilha colaborativa de oportunidades

---

## Funcionalidades

- **Execução automática** de segunda a sexta às 07:00 BRT
- **Três passagens** de busca com `thinking_level="HIGH"` para maior profundidade
- **Auditoria de elegibilidade**: cada oportunidade é verificada para confirmar se o Brasil pode aplicar
- **Seções separadas no relatório**: oportunidades com elegibilidade confirmada vs. a verificar
- **Classificação de urgência**: 🔴 urgente (<30 dias), 🟡 atenção (30–90 dias), 🟢 planejamento
- **Validação de links**: URLs quebradas são sinalizadas automaticamente
- **Relatório por e-mail** em HTML com banner de urgência para prazos próximos
- **Artefatos**: `grant_report.md` e `grant_report.json` retidos por 90 dias no GitHub Actions
- **Trigger manual** disponível pela aba Actions

---

## Configuração

### Pré-requisitos

- Repositório GitHub com Actions habilitado
- Chave da API do Google Gemini ([obter aqui](https://aistudio.google.com/app/apikey))
- Conta Gmail com App Password ([guia de configuração](https://support.google.com/accounts/answer/185833)) — requer 2FA ativado

### Segredos do repositório

Em **Settings → Secrets and Variables → Actions**, adicione:

| Segredo | Descrição |
|---------|-----------|
| `GEMINI_API_KEY` | Chave da API Google Gemini |
| `GMAIL_APP_PASSWORD` | App Password do Gmail (não é a senha da conta) |

### Execução local

```bash
pip install -r requirements.txt
GEMINI_API_KEY=<chave> GMAIL_APP_PASSWORD=<app_password> python grant_scanner.py
```

A execução local envia e-mail para a lista `RECIPIENTS` e salva `grant_report.md`, `grant_report.json` e `previous_grant_report.json` no diretório corrente.

---

## Configuração principal (`grant_scanner.py`)

| Variável | Descrição |
|----------|-----------|
| `GEMINI_MODEL` | Modelo Gemini usado (atualmente `gemini-3-pro-preview`) |
| `RECIPIENTS` | Lista de e-mails que recebem o relatório |
| `SENDER_EMAIL` | Conta Gmail usada para envio SMTP |
| `PREVIOUS_REPORT_PATH` | Arquivo JSON que persiste os dados da última execução |
| `HEADER_TEMPLATE` / `FOOTER_TEMPLATE` | Seções estáticas do relatório (não geradas pela IA) |

---

## Elegibilidade — como funciona

Cada oportunidade carrega dois campos de elegibilidade:

| Campo | Valores |
|-------|---------|
| `brazil_eligible` | `true` / `false` / `null` |
| `eligibility_confidence` | `"confirmed"` \| `"likely"` \| `"partial"` \| `"unverified"` |

O relatório final divide as oportunidades em duas seções:

- **✅ Elegibilidade confirmada** — `confirmed` ou `likely` com `brazil_eligible=true`
- **⚠️ A verificar** — `unverified`, `partial` ou `brazil_eligible=null`
- **Removidas silenciosamente** — `brazil_eligible=false` (inelegíveis confirmadas)

---

## Fluxo de dados

```
Gemini API (Pass 1 + Pass 2)
  → validate_opportunity()
  → deduplicate_opportunities()
  → filter expired deadlines
  → Gemini API (Pass 3 — audit)
  → apply_audit_results()
  → validate_links()
  → classify_urgency()
  → sort_opportunities()
  → filter_by_eligibility()
  → format_report_markdown()
  → build_email_html()
  → send_email()
  → save artifacts (grant_report.md, grant_report.json)
```

---

## Schedule do workflow

```yaml
schedule:
  # 07:00 BRT = 10:00 UTC (BRT = UTC-3)
  - cron: "0 10 * * 1-5"   # Segunda a sexta
```

---

## Troubleshooting

**Workflow não executa**
- Verifique se o Actions está habilitado no repositório
- Confirme que os segredos `GEMINI_API_KEY` e `GMAIL_APP_PASSWORD` estão configurados
- Revise os logs na aba Actions

**E-mail não chega**
- Verifique se o `GMAIL_APP_PASSWORD` é um App Password (não a senha da conta)
- Confirme que o 2FA está ativado na conta Gmail remetente
- Cheque se o `SENDER_EMAIL` no código corresponde à conta Gmail

**Erros de API Gemini**
- Confirme que a chave `GEMINI_API_KEY` é válida
- Verifique se o modelo `gemini-3-pro-preview` está disponível na sua conta
- Revise os logs para mensagens de erro específicas

**Poucas oportunidades encontradas**
- A auditoria de elegibilidade pode ter removido muitas oportunidades — veja nos logs quantas foram descartadas
- Considere ajustar os prompts para focar em regiões ou temas específicos

---

## Segurança

- Nunca commite chaves de API no repositório
- Use exclusivamente o GitHub Secrets para credenciais
- Rotacione periodicamente o App Password do Gmail
- Monitore os logs de execução para anomalias

---

## Licença

MIT License — consulte o arquivo [LICENSE](LICENSE).

---

## Créditos

- **Abraji** — Associação Brasileira de Jornalismo Investigativo
- **Google Gemini** — modelo de IA com busca na web em tempo real
- **GitHub Actions** — automação do workflow

**Desenvolvido por** Reinaldo Chaves ([@reichaves](https://github.com/reichaves))
