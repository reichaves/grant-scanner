# 📡 Grant Scanner — Radar de Oportunidades para a Abraji

**Monitor Automatizado de Oportunidades de Financiamento para Jornalismo Investigativo**

Um workflow GitHub Actions que usa Google Gemini com busca na web para identificar, verificar e reportar diariamente grants, fellowships e editais para jornalismo investigativo. Executa automaticamente de segunda a sexta às **07:00 BRT** e entrega relatórios curados por e-mail.

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
```

### Fontes consultadas em cada sessão

Além da busca livre na web, o sistema consulta obrigatoriamente a cada execução:

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

> Para testar sem enviar e-mail, comente a chamada `send_email()` no final de `main()` em `grant_scanner.py`.

---

## Estrutura de arquivos

```
grant_scanner.py              # Ponto de entrada (~70 linhas)
requirements.txt              # Dependências: google-genai, requests
.github/
  workflows/
    grant-scanner.yml         # Workflow do GitHub Actions (cron + manual)
src/
  config/__init__.py          # Constantes: modelo, e-mails, fuso horário, templates
  models/__init__.py          # TypedDicts: Opportunity, SearchResult, Stats
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

## Descrição detalhada de cada arquivo

### `grant_scanner.py`

Ponto de entrada da aplicação com ~70 linhas. Responsabilidades:

1. Valida as variáveis de ambiente obrigatórias (`GEMINI_API_KEY`, `GMAIL_APP_PASSWORD`) — encerra com código 1 se ausentes
2. Chama `run_grant_search(api_key)` para executar o pipeline completo
3. Formata o relatório Markdown com `format_report_markdown()`
4. Constrói o assunto do e-mail com contagens dinâmicas (confirmadas, a verificar, urgentes)
5. Envia o e-mail HTML + texto simples
6. Salva `grant_report.md`, `grant_report.json` e `previous_grant_report.json`

---

### `src/config/__init__.py`

Todas as constantes estáticas da aplicação — sem segredos, sem lógica:

| Constante | Descrição |
|-----------|-----------|
| `BRT` | Fuso horário UTC-3 (Brasília) |
| `GEMINI_MODEL` | ID do modelo Gemini a usar (`gemini-3-pro-preview`) |
| `SENDER_EMAIL` | E-mail remetente do relatório |
| `RECIPIENTS` | Lista de destinatários do relatório |
| `PREVIOUS_REPORT_PATH` | Caminho do JSON da execução anterior (`previous_grant_report.json`) |
| `HEADER_TEMPLATE` | Cabeçalho do relatório com totais e legenda (placeholders: `{today}`, `{year}`, `{total_count}`, `{confirmed_count}`, `{unverified_count}`, `{urgent_count}`) |
| `FOOTER_TEMPLATE` | Rodapé com créditos e aviso de verificação manual |

---

### `src/models/__init__.py`

Define os tipos de dados do projeto usando `TypedDict` (sem `Any`):

**`Opportunity`** — uma oportunidade de financiamento. Campos principais:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `name`, `funder`, `summary`, `url` | `str` | Dados básicos |
| `deadline` | `str` | ISO `YYYY-MM-DD` ou `"rolling"` |
| `deadline_type` | `Literal` | `"fixed"` / `"rolling"` / `"estimated"` |
| `deadline_display` | `str` | Ex: `"15 de março de 2026"` |
| `amount_display` | `str` | Ex: `"USD 5.000 – USD 20.000"` |
| `amount_usd_min/max` | `int` | Valor numérico (0 se não divulgado) |
| `themes` | `list[str]` | Tags temáticas em inglês |
| `type` | `str` | `"grant"` / `"fellowship"` / `"fund"` / `"emergency"` |
| `eligibility` | `str` | Texto descritivo de elegibilidade |
| `brazil_eligible` | `bool\|None` | Flag explícita de elegibilidade |
| `eligibility_confidence` | `Literal` | `"confirmed"` / `"likely"` / `"partial"` / `"unverified"` |
| `eligibility_source` | `str` | URL onde a elegibilidade foi verificada |
| `eligible_regions` | `list[str]` | Regiões elegíveis conforme fonte oficial |
| `urgency` | `str` | `"🔴"` / `"🟡"` / `"🟢"` / `"⚫"` |
| `link_valid` | `bool` | Se a URL retornou HTTP 200 |

**`Stats`** — estatísticas de execução do pipeline (contagens por passagem, removidos, etc.)

**`SearchResult`** — resultado completo retornado por `run_grant_search()`: listas separadas de confirmadas/não-verificadas, recomendações estratégicas, metadados, estatísticas.

---

### `src/sources/`

Lista curada de 70 sites de grants extraída da planilha colaborativa da Abraji.

| Arquivo | Conteúdo |
|---------|----------|
| `individual.py` | 8 fontes voltadas a projetos individuais e fellowships |
| `institutional.py` | 69 fontes voltadas a organizações institucionais |
| `__init__.py` | Agrega e deduplica por URL; exporta `ALL_SOURCES` e `build_sources_block()` |

**`build_sources_block()`** retorna uma string formatada com nome, URL e foco de cada fonte — injetada diretamente no prompt do Pass 2 para que o Gemini visite cada site explicitamente, substituindo a instrução anterior de "ler a planilha Google".

**Para adicionar uma nova fonte:** edite `individual.py` ou `institutional.py` adicionando um dict `Source` com os campos `name`, `url` e `focus`. Ela aparecerá automaticamente no Pass 2 na próxima execução.

---

### `src/prompts/__init__.py`

Define todos os prompts do sistema. Escrito integralmente em português.

| Função/Constante | Passagem | Descrição |
|-----------------|----------|-----------|
| `SYSTEM_PROMPT` | Pass 1 | Instrução de sistema completa: papel do modelo, organizações-alvo, 25+ termos de busca em EN/ES/PT, protocolo obrigatório de verificação de elegibilidade em 4 passos, formato JSON de saída exato, exemplos de falsos positivos a evitar |
| `build_user_prompt(today)` | Pass 1 | Prompt de usuário com a data atual, 7 categorias temáticas e fontes obrigatórias a visitar |
| `build_second_pass_prompt(today, found_names, sources_block)` | Pass 2 | Prompt com lista de oportunidades já encontradas e o bloco de 70 fontes curadas para buscar apenas o que está faltando |
| `build_audit_prompt(today, opportunities_to_audit)` | Pass 3 | Prompt de auditor cético: recebe a lista combinada e instrui o modelo a buscar evidências de inelegibilidade geográfica para cada item |

O `SYSTEM_PROMPT` inclui um **Protocolo de Verificação de Elegibilidade** com 4 passos detalhados, definição das 5 classificações possíveis, exemplos de grants `partial` (IJ4EU, Journalismfund) e uma "Regra de Ouro": na dúvida, marcar como `unverified` — nunca `confirmed` sem verificar a fonte oficial.

---

### `src/pipeline/__init__.py` — `run_grant_search(api_key)`

Função principal do pipeline. Orquestra todas as etapas em sequência:

1. Inicializa `genai.Client` com a chave da API
2. Executa **Pass 1** — varredura ampla
3. Executa **Pass 2** — busca complementar com nomes já encontrados + fontes curadas
4. Combina as listas de oportunidades dos dois passes
5. Normaliza cada oportunidade com `validate_opportunity()`
6. Remove duplicatas com `deduplicate_opportunities()`
7. Filtra prazos expirados (descarta urgência `⚫`)
8. Executa **Pass 3** — auditoria adversarial de elegibilidade
9. Aplica os resultados da auditoria com `apply_audit_results()`
10. Valida links HTTP com `validate_links()`
11. Classifica urgência e ordena por prazo com `classify_urgency()` + `sort_opportunities()`
12. Divide em confirmadas/não-verificadas com `filter_by_eligibility()`
13. Retorna `SearchResult` com estatísticas completas

---

### `src/pipeline/search.py`

Implementa as duas primeiras passagens da busca:

**`run_pass1(client, today)`**
- Varredura ampla usando `SYSTEM_PROMPT` + `build_user_prompt()`
- Retorna `(opportunities, strategic_recommendations)`
- Falha com `sys.exit(1)` em erro de API (Pass 1 é crítico)

**`run_pass2(client, today, found_names)`**
- Busca direcionada: injeta a lista de nomes já encontrados e as 70 fontes curadas via `build_sources_block()`
- Retorna apenas oportunidades *novas* não encontradas no Pass 1
- Falha graciosamente (não encerra o processo)

Ambas usam a mesma configuração via `_make_search_config()`:
- `ThinkingConfig(thinking_level="HIGH")` — raciocínio aprofundado
- `tools=[GoogleSearch()]` — grounding com busca web em tempo real
- `temperature=0.1`, `max_output_tokens=65536`

---

### `src/pipeline/audit.py` — `run_pass3(client, today, opportunities)`

Executa a auditoria adversarial de elegibilidade geográfica. Diferencia-se dos passes anteriores em três aspectos:

- **Sem `system_instruction`** — o prompt de auditoria é passado direto como conteúdo do usuário
- **`temperature=0.0`** — máxima factualidade, sem variação criativa
- **`max_output_tokens=32768`** — resposta menor, focada nos resultados

Retorna lista de `audit_results`, cada um com:
- `brazil_eligible` — booleano ou null
- `eligibility_confidence` — classificação revisada
- `audit_notes` — URL ou descrição da fonte consultada
- `eligible_regions_found` — regiões reais encontradas na fonte oficial
- `disqualification_reason` — motivo da inelegibilidade (quando `brazil_eligible=false`)

Falha graciosamente — se o Pass 3 falhar, o pipeline continua sem auditoria.

---

### `src/utils/__init__.py`

Funções utilitárias puras, sem efeitos colaterais de I/O (exceto as de persistência):

**JSON parsing:**
- `extract_json_from_response(text)` — extrai JSON do texto LLM; remove fences de Markdown (` ```json `), tenta `json.loads()` direto, busca por regex `{...}`, e como último recurso chama `_recover_truncated_json()`
- `_recover_truncated_json(text)` — recupera JSON cortado pelo `max_output_tokens` percorrendo o texto char-a-char para fechar estruturas `{[` abertas

**Normalização:**
- `validate_opportunity(opp)` — garante que todos os campos obrigatórios existem; preenche ausentes com `"⚠️ Não informado"`, `"rolling"`, `"Não divulgado"`, `0`, `[]`, etc.

**Classificação:**
- `classify_urgency(opp, today)` — calcula dias até o prazo e retorna emoji: `🔴` (<30d), `🟡` (30–90d), `🟢` (>90d ou rolling), `⚫` (expirado)
- `classify_eligibility_display(opp)` — retorna `✅` (confirmed/likely), `🔗` (partial) ou `⚠️` (unverified)

**Operações de lista:**
- `deduplicate_opportunities(opps)` — remove duplicatas normalizando o nome para lowercase alfanumérico e comparando os primeiros 30 caracteres
- `sort_opportunities(opps, today)` — ordena: urgentes primeiro (≤30d), depois por data crescente, rolling sempre por último
- `filter_by_eligibility(opps)` — divide em `(confirmed_list, unverified_list)`; silenciosamente descarta `brazil_eligible=false`
- `apply_audit_results(opps, audit_results)` — faz merge dos resultados do Pass 3 nas oportunidades usando normalização de nome; pode marcar inelegível, confirmar, ou fazer downgrade para `partial`

**Validação de links:**
- `validate_links(opps)` — faz HTTP HEAD em cada URL com timeout de 10s; marca broken links com aviso `⚠️ (HTTP 4xx)` na própria URL; skip gracioso se `requests` não estiver instalado

**Persistência:**
- `save_report_data(result)` — salva `SearchResult` como JSON em `previous_grant_report.json`
- `load_previous_report()` — carrega execução anterior (disponível para uso futuro, ex: comparação de runs)

---

### `src/report/__init__.py` — `format_report_markdown(result)`

Formata o `SearchResult` em relatório Markdown completo. Estrutura gerada:

1. **Cabeçalho** — `HEADER_TEMPLATE` preenchido com data, totais e legenda de urgência/elegibilidade
2. **Seção `✅ ELEGIBILIDADE CONFIRMADA`** — oportunidades com `confirmed` ou `likely` + `brazil_eligible=true`
3. **Seção `⚠️ ELEGIBILIDADE A VERIFICAR`** — oportunidades `unverified`, `partial` ou `brazil_eligible=null`
4. **Seção `3 PASSOS ESTRATÉGICOS PARA A ABRAJI`** — recomendações geradas pelo LLM (título, ação, estratégia, editais relacionados, data limite para preparação)
5. **Rodapé** — `FOOTER_TEMPLATE` com créditos

Cada oportunidade é formatada por `_format_opportunity()` com: urgência, número, nome, financiador, resumo, valor, prazo, elegibilidade, regiões, nota de parceiro (se `partial`), tipo, temas e link.

---

### `src/report/email.py`

Três funções para construção e entrega do relatório por e-mail:

**`markdown_to_html(md_text)`**
Conversor leve de Markdown → HTML sem dependências externas. Trata: escape de HTML, `#`/`##`/`###` → `<h1>`/`<h2>`/`<h3>`, `**bold**` / `*italic*`, links `[text](url)` e URLs nuas, listas com `-`, divisores `---` e parágrafos com `\n\n`.

**`build_email_html(report_md, result)`**
Monta HTML completo com:
- Cabeçalho gradiente azul com título e contadores
- Painel de verificação de elegibilidade (confirmadas vs. a verificar vs. removidas)
- Alerta amarelo com prazos urgentes (apenas oportunidades com elegibilidade confirmada)
- Corpo do relatório renderizado

**`send_email(sender, recipients, subject, html_body, plain_text, app_password)`**
Envia via Gmail SMTP (porta 465, SSL) usando App Password. Envia e-mail MIME multipart com parte `plain` e parte `html`. Encerra com `sys.exit(1)` em erro de autenticação.

---

## Fluxo de dados completo

```
grant_scanner.py
  └─ run_grant_search(api_key)                     [src/pipeline/__init__.py]
       ├─ run_pass1()                               [src/pipeline/search.py]
       │    └─ SYSTEM_PROMPT + build_user_prompt()  [src/prompts/__init__.py]
       ├─ run_pass2(found_names)                    [src/pipeline/search.py]
       │    └─ build_second_pass_prompt()
       │         └─ build_sources_block()           [src/sources/__init__.py]
       ├─ validate_opportunity() × N               [src/utils/__init__.py]
       ├─ deduplicate_opportunities()
       ├─ filter expired (urgency ⚫)
       ├─ run_pass3()                               [src/pipeline/audit.py]
       │    └─ build_audit_prompt()                [src/prompts/__init__.py]
       ├─ apply_audit_results()                    [src/utils/__init__.py]
       ├─ validate_links()
       ├─ classify_urgency() + sort_opportunities()
       └─ filter_by_eligibility() → SearchResult
  └─ format_report_markdown(result)                [src/report/__init__.py]
  └─ build_email_html(report_md, result)           [src/report/email.py]
  └─ send_email(...)
  └─ save_report_data(result)                      [src/utils/__init__.py]
```

---

## Elegibilidade — como funciona

Cada oportunidade carrega dois campos combinados:

| `brazil_eligible` | `eligibility_confidence` | Seção no relatório |
|:-----------------:|:------------------------:|--------------------|
| `true` | `confirmed` | ✅ Confirmada |
| `true` | `likely` | ✅ Confirmada |
| `true` | `partial` | ⚠️ A verificar (Brasil só como parceiro) |
| `null` | `unverified` | ⚠️ A verificar |
| `false` | `confirmed` | Removida silenciosamente |

---

## Schedule do workflow

```yaml
schedule:
  # 07:00 BRT = 10:00 UTC (BRT = UTC-3)
  - cron: "0 10 * * 1-5"   # Segunda a sexta
```

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

**Erros de API Gemini**
- Confirme que a chave `GEMINI_API_KEY` é válida
- Verifique se o modelo configurado em `GEMINI_MODEL` está disponível na sua conta
- Revise os logs para mensagens de erro específicas

**JSON truncado / poucas oportunidades**
- O `_recover_truncated_json()` em `src/utils/__init__.py` tenta recuperar automaticamente
- Se o problema persistir, considere reduzir `max_output_tokens` ou simplificar os prompts
- A auditoria de elegibilidade pode ter removido muitas oportunidades — veja nos logs `"Pass 3 disqualified N opportunities"`

---

## Dependências

```
google-genai>=1.0.0   # SDK oficial do Google Gemini (genai.Client)
requests              # Validação de links HTTP
```

> O projeto usa `google-genai` (API `genai.Client`), **não** o pacote legado `google-generativeai`.

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
