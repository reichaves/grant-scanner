# 📡 Grant Scanner — Radar de Oportunidades para a Abraji

**Monitor Automatizado de Oportunidades de Financiamento para Jornalismo Investigativo**

Um workflow GitHub Actions que usa Google Gemini com busca na web para identificar, verificar e reportar diariamente grants, fellowships e editais para jornalismo investigativo. Executa automaticamente de segunda a sexta às **07:00 BRT** e entrega relatórios curados por e-mail, armazena todas as oportunidades em uma planilha no Google Drive e publica um dashboard no GitHub Pages.

Desenvolvido para a [Abraji](https://abraji.org.br/) (Associação Brasileira de Jornalismo Investigativo).

---

## Como funciona

O sistema realiza **três passagens** sequenciais com o modelo Gemini, com busca na web em tempo real:

```
Pass 1 (Varredura ampla)
  → 12–20 oportunidades identificadas via Google Search

Pass 2 (Busca complementar)
  → Oportunidades adicionais não encontradas no Pass 1
  → Visita explicitamente as 70 URLs curadas em src/sources/
  → Foco em editais brasileiros, tech, fellowships, fundos climáticos

Pass 3 (Auditoria adversarial de elegibilidade)
  → Age como auditor CÉTICO, tentando REFUTAR a elegibilidade
  → Verifica a página oficial de cada oportunidade
  → Remove oportunidades onde o Brasil confirmadamente não é elegível

→ Validação de links, classificação de urgência, formatação e envio por e-mail
→ Upload para Google Sheets (deduplicado por URL)
→ Atualização do dashboard GitHub Pages via docs/data.json
```

---

## Funcionalidades

- **Execução automática** de segunda a sexta às 07:00 BRT
- **Três passagens** de busca com `thinking_level="HIGH"` para maior profundidade
- **Auditoria de elegibilidade**: cada oportunidade é verificada para confirmar se o Brasil pode aplicar
- **Relatório por e-mail** em HTML com banner de urgência para prazos próximos
- **Planilha no Google Drive**: todas as oportunidades são salvas diariamente, sem duplicatas
- **Dashboard GitHub Pages**: visualização histórica com gráficos e filtros
- **Classificação de urgência**: 🔴 urgente (<30 dias), 🟡 atenção (30–90 dias), 🟢 planejamento
- **Validação de links**: URLs quebradas são sinalizadas automaticamente
- **Artefatos**: `grant_report.md` e `grant_report.json` retidos por 90 dias no GitHub Actions
- **Trigger manual** disponível pela aba Actions

---

## Configuração

### Pré-requisitos

- Repositório GitHub com Actions habilitado
- Chave da API do Google Gemini ([obter aqui](https://aistudio.google.com/app/apikey))
- Conta Gmail com App Password ([guia](https://support.google.com/accounts/answer/185833)) — requer 2FA ativado
- Conta Google Cloud para a integração com Google Sheets (opcional, mas recomendado)

---

### 1. Configuração básica (e-mail)

Em **Settings → Secrets and Variables → Actions**, adicione:

| Segredo | Descrição |
|---------|-----------|
| `GEMINI_API_KEY` | Chave da API Google Gemini |
| `GMAIL_APP_PASSWORD` | App Password do Gmail (não é a senha da conta) |

---

### 2. Configuração do Google Sheets

Siga este passo a passo para que o scanner salve oportunidades na planilha do Google Drive.

#### 2.1 Criar o projeto no Google Cloud

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto (ex: `grant-scanner`)
3. No menu lateral, vá em **APIs e serviços → Biblioteca**
4. Busque e ative as duas APIs:
   - **Google Sheets API**
   - **Google Drive API**

#### 2.2 Criar a conta de serviço

1. Vá em **IAM e administrador → Contas de serviço**
2. Clique em **Criar conta de serviço**
3. Preencha: nome `grant-scanner-bot`, clique em **Criar e continuar**
4. Em "Conceder acesso ao projeto", selecione a função **Editor** (ou **Viewer** se preferir só leitura)
5. Clique em **Concluído**

#### 2.3 Baixar a chave JSON

1. Na lista de contas de serviço, clique na que você criou
2. Vá em **Chaves → Adicionar chave → Criar nova chave**
3. Selecione **JSON** e clique em **Criar** — o arquivo é baixado automaticamente
4. Guarde este arquivo com segurança; você precisará do conteúdo na próxima etapa

#### 2.4 Criar a planilha no Google Drive

1. Acesse o [Google Sheets](https://sheets.google.com/) e crie uma nova planilha em branco
2. Dê um nome (ex: `Radar de Grants — Abraji`)
3. **Compartilhe a planilha com a conta de serviço**: botão "Compartilhar" → cole o e-mail da conta de serviço (formato `nome@projeto.iam.gserviceaccount.com`) → selecione permissão **Editor**
4. Copie o **ID da planilha** da URL: `https://docs.google.com/spreadsheets/d/**ID_AQUI**/edit`

#### 2.5 Adicionar os segredos no GitHub

Em **Settings → Secrets and Variables → Actions**, adicione:

| Segredo | Descrição |
|---------|-----------|
| `GOOGLE_SHEET_ID` | ID da planilha (extraído da URL no passo 2.4) |
| `GOOGLE_SHEETS_CREDENTIALS` | Conteúdo completo do JSON baixado no passo 2.3 |

> **Dica**: O segredo `GOOGLE_SHEETS_CREDENTIALS` aceita tanto o JSON bruto quanto codificado em base64. Para base64: `cat credentials.json | base64 | tr -d '\n'`

---

### 3. Configuração do GitHub Pages (dashboard)

#### 3.1 Habilitar o GitHub Pages

1. No repositório, vá em **Settings → Pages**
2. Em **Source**, selecione **Deploy from a branch**
3. Branch: `main` — pasta: `/docs`
4. Clique em **Save**

O dashboard estará disponível em:
`https://<seu-usuario>.github.io/<nome-do-repo>/`

#### 3.2 Como o dashboard é atualizado

Após cada execução do workflow com Google Sheets configurado:

1. O scanner faz upload das novas oportunidades na planilha
2. Busca o histórico completo da planilha e grava em `docs/data.json`
3. O workflow commita e faz push de `docs/data.json` automaticamente
4. O GitHub Pages serve o dashboard atualizado com os dados mais recentes

> O commit de atualização usa a mensagem `chore: update dashboard data [skip ci]` para evitar loops de execução.

#### 3.3 Permissão de escrita no repositório

O workflow já está configurado com `permissions: contents: write` para poder fazer o push de `docs/data.json`. Se o repositório tiver proteções de branch no `main`, crie uma exceção para `github-actions[bot]`.

---

### Execução local

```bash
pip install -r requirements.txt
GEMINI_API_KEY=<chave> GMAIL_APP_PASSWORD=<app_password> python grant_scanner.py
```

Com Google Sheets:
```bash
GEMINI_API_KEY=<chave> \
GMAIL_APP_PASSWORD=<app_password> \
GOOGLE_SHEET_ID=<id_da_planilha> \
GOOGLE_SHEETS_CREDENTIALS="$(cat credentials.json)" \
python grant_scanner.py
```

> Para testar sem enviar e-mail, comente a chamada `send_email()` no final de `main()` em `grant_scanner.py`.

---

## Estrutura de arquivos

```
grant_scanner.py              # Ponto de entrada (~100 linhas)
requirements.txt              # Dependências: google-genai, requests, gspread
docs/
  index.html                  # Dashboard GitHub Pages (single-file)
  data.json                   # Dados para o dashboard (gerado pelo workflow)
  .nojekyll                   # Desativa o Jekyll no GitHub Pages
.github/
  workflows/
    grant-scanner.yml         # Workflow do GitHub Actions (cron + manual)
src/
  config/__init__.py          # Constantes: modelo, e-mails, fuso horário, templates
  models/__init__.py          # TypedDicts: Opportunity, SearchResult, Stats
  sheets/__init__.py          # Google Sheets: upload (dedup por URL) + fetch histórico
  sources/
    __init__.py               # Agrega ALL_SOURCES + build_sources_block()
    individual.py             # 8 fontes da aba "Individual/Projeto" da planilha
    institutional.py          # 69 fontes da aba "Institucional" da planilha
  prompts/__init__.py         # SYSTEM_PROMPT + funções build_*_prompt()
  pipeline/
    __init__.py               # run_grant_search() — orquestra as 3 passagens
    search.py                 # run_pass1() e run_pass2()
    audit.py                  # run_pass3() — auditoria de elegibilidade
  report/
    __init__.py               # format_report_markdown()
    email.py                  # markdown_to_html(), build_email_html(), send_email()
  utils/__init__.py           # Funções utilitárias: JSON, validação, dedup, links
```

---

## Dashboard (GitHub Pages)

O dashboard em `docs/index.html` é um single-page app estático que lê `docs/data.json`.

**Visualizações disponíveis:**
- 5 cartões de resumo: total, elegibilidade confirmada, a verificar, urgentes, fluxo contínuo
- Gráfico de rosca: distribuição de urgência
- Gráfico de rosca: distribuição de elegibilidade
- Gráfico de rosca: distribuição por tipo (grant, fellowship, edital…)
- Gráfico de barras: oportunidades descobertas por dia (linha do tempo)
- Gráfico de barras horizontal: top 12 temas mais frequentes
- Tabela completa com busca por texto e filtros de urgência, tipo e elegibilidade

Todos os dados são carregados localmente do `data.json` — sem dependências externas de autenticação.

---

## Deduplicação na planilha

A cada execução, antes de inserir novas linhas, o scanner:

1. Lê todas as URLs já presentes na planilha
2. Normaliza cada URL (remove query string e trailing slash)
3. Insere apenas oportunidades com URLs ainda não registradas

Isso garante que a mesma oportunidade não apareça duplicada mesmo que seja encontrada em múltiplas execuções.

---

## Elegibilidade — como funciona

| `brazil_eligible` | `eligibility_confidence` | Seção no relatório |
|:-----------------:|:------------------------:|--------------------|
| `true` | `confirmed` | ✅ Confirmada |
| `true` | `likely` | ✅ Confirmada |
| `true` | `partial` | ⚠️ A verificar (Brasil só como parceiro) |
| `null` | `unverified` | ⚠️ A verificar |
| `false` | `confirmed` | Removida silenciosamente |

---

## Adicionando novas fontes

Edite [src/sources/individual.py](src/sources/individual.py) ou [src/sources/institutional.py](src/sources/institutional.py):

```python
Source(
    name="Nome da organização",
    url="https://example.org/grants",
    focus="Descrição do foco (ex: Jornalismo investigativo, LatAm)",
)
```

A nova fonte aparecerá automaticamente no prompt do Pass 2 na próxima execução.

---

## Troubleshooting

**Workflow não executa**
- Verifique se o Actions está habilitado no repositório
- Confirme que os segredos `GEMINI_API_KEY` e `GMAIL_APP_PASSWORD` estão configurados
- Revise os logs na aba Actions

**E-mail não chega**
- Verifique se o `GMAIL_APP_PASSWORD` é um App Password (não a senha da conta)
- Confirme que o 2FA está ativado na conta Gmail remetente
- Cheque se o `SENDER_EMAIL` em `src/config/__init__.py` corresponde à conta Gmail

**Google Sheets: erro de autenticação**
- Confirme que o JSON em `GOOGLE_SHEETS_CREDENTIALS` está completo (sem quebras de linha extras)
- Verifique se a planilha foi compartilhada com o e-mail da conta de serviço
- Confirme que as APIs Google Sheets e Google Drive estão ativadas no Cloud Console

**Google Sheets: planilha não atualiza**
- Verifique se `GOOGLE_SHEET_ID` está correto (apenas o ID, não a URL completa)
- Confirme que o segredo `GOOGLE_SHEET_ID` está configurado em Actions Secrets (não em Variables)

**Dashboard não atualiza (GitHub Pages)**
- Confirme que o `permissions: contents: write` está no workflow
- Se o branch `main` tiver proteção de branch, crie uma exceção para `github-actions[bot]`
- Verifique na aba Actions se o step "Commit dashboard data" foi executado e se houve erro

**JSON truncado / poucas oportunidades**
- O `_recover_truncated_json()` em `src/utils/__init__.py` tenta recuperar automaticamente
- Se o problema persistir, considere reduzir `max_output_tokens` ou simplificar os prompts

---

## Dependências

```
google-genai>=1.0.0   # SDK oficial do Google Gemini (genai.Client)
requests              # Validação de links HTTP
gspread>=6.0.0        # Integração com Google Sheets
```

> O projeto usa `google-genai` (API `genai.Client`), **não** o pacote legado `google-generativeai`.

---

## Schedule do workflow

```yaml
schedule:
  # 07:00 BRT = 10:00 UTC (BRT = UTC-3)
  - cron: "0 10 * * 1-5"   # Segunda a sexta
```

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
- **Google Sheets** — persistência e histórico de oportunidades
- **GitHub Actions / Pages** — automação e publicação do dashboard

**Desenvolvido por** Reinaldo Chaves ([@reichaves](https://github.com/reichaves))
