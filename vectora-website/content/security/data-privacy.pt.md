---
title: "Privacidade de Dados: Local-First no Vectora"
slug: data-privacy
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - lancedb
  - privacy
  - security
  - vectora
  - voyage
---

{{< lang-toggle >}}

{{< section-toggle >}}

O Vectora é local-first: nenhum arquivo de código sai da máquina sem escolha explícita do usuário. Embeddings são gerados via API VoyageAI (somente o texto do chunk é enviado), vetores são armazenados localmente no LanceDB, e o LLM recebe apenas os top-10 chunks relevantes — nunca o codebase inteiro.

## O Que Sai da Máquina

| Dado             | Destino                | Motivo                |
| ---------------- | ---------------------- | --------------------- |
| Texto dos chunks | VoyageAI API           | Geração de embeddings |
| Query do usuário | VoyageAI API           | Embedding da query    |
| Top-10 chunks    | LLM externo (opcional) | Geração de resposta   |
| Métricas de uso  | Nenhum                 | Não coletadas         |

O que **nunca** sai da máquina:

- Vetores numéricos (1024D) armazenados no LanceDB
- Estrutura completa do codebase
- Credenciais e tokens JWT
- Logs do VCR e histórico de sessões (PostgreSQL local)

## Fluxo de Dados

```text
Codebase local
  |
  +-> Chunker (local)
  |     -> divide em blocos de 512 tokens
  |
  +-> VoyageAI API (HTTPS)
  |     -> envia: texto dos chunks [SAIR DA MÁQUINA]
  |     <- recebe: vetores 1024D
  |
  +-> LanceDB (local)
        -> armazena: vetores + metadados
        -> never sent to external

Query do usuário
  |
  +-> VoyageAI API (HTTPS)
  |     -> envia: texto da query [SAIR DA MÁQUINA]
  |     <- recebe: vetor 1024D
  |
  +-> LanceDB (local) -> top-100 candidatos
  +-> XLM-RoBERTa (local) -> top-10 rerankeados
  |
  +-> LLM externo (opcional, HTTPS)
        -> envia: query + top-10 chunks [SAIR DA MÁQUINA]
        <- recebe: resposta gerada
```

## Cache Redis e Privacidade

Embeddings são cacheados no Redis local por SHA-256 do texto original. O Redis roda localmente — os vetores nunca são enviados para uma instância Redis remota na configuração padrão.

```python
cache_key = f"embed:{hashlib.sha256(text.encode()).hexdigest()}"
r.setex(cache_key, 86400, json.dumps(embedding))
```

Se configurar Redis remoto, os embeddings transitam pela rede — avalie se isso é aceitável para os dados do projeto.

## Modo Completamente Offline

Para projetos que não podem enviar dados para APIs externas, o Vectora suporta modo offline com modelo de embedding local (em desenvolvimento):

```bash
# Configurar modo offline
vectora config set embedding_provider local
vectora config set embedding_model sentence-transformers/all-MiniLM-L6-v2
```

Em modo offline:

- Sem VoyageAI API — embeddings gerados localmente via sentence-transformers
- Sem LLM externo — apenas busca semântica e reranking
- Qualidade de embedding inferior ao voyage-4

## Configuração de LLM Externo

O LLM externo é opcional. Sem configurar um LLM, o Vectora opera como motor de busca semântica pura — retorna chunks relevantes sem geração de texto.

```bash
# Sem LLM (busca semântica apenas)
vectora search "Como validar JWT?"
# Retorna: lista de arquivos relevantes com scores

# Com LLM (geração de resposta)
vectora config set llm_provider anthropic
vectora config set llm_model claude-sonnet-4-6
vectora agent run "Como validar JWT?"
# Retorna: resposta gerada com base nos chunks encontrados
```

## Auditoria de Dados

Para auditar quais dados foram enviados externamente:

```bash
# Ver chamadas VoyageAI (logs do servidor)
vectora logs --filter voyage --since 24h

# Ver chamadas LLM
vectora logs --filter llm --since 24h
```

Os logs registram apenas metadados (timestamp, modelo, tokens), não o conteúdo dos chunks.

## External Linking

| Conceito              | Recurso                            | Link                                                                                           |
| --------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------- |
| **VoyageAI Privacy**  | Voyage AI data processing          | [voyageai.com/privacy](https://www.voyageai.com/privacy/)                                      |
| **Anthropic Privacy** | Anthropic data policy              | [anthropic.com/privacy](https://www.anthropic.com/privacy)                                     |
| **GDPR**              | General Data Protection Regulation | [gdpr.eu](https://gdpr.eu/)                                                                    |
| **Data Minimization** | OWASP data minimization            | [owasp.org/www-community/Data_Minimization](https://owasp.org/www-community/Data_Minimization) |
