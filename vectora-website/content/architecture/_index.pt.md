---
title: "Arquitetura do Vectora"
slug: architecture
date: "2026-05-04T10:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - agentic-framework
  - architecture
  - context-engine
  - fastapi
  - lancedb
  - langchain
  - langgraph
  - postgresql
  - redis
  - vcr
  - vectora
  - voyage
  - xlm-roberta
draft: false
---

{{< lang-toggle >}}

{{< section-toggle >}}

O Vectora é composto por camadas ortogonais com responsabilidades bem definidas: protocolo, orquestração, inferência, armazenamento e persistência. Esta página documenta como esses componentes se relacionam.

## Visão em Camadas

```text
┌────────────────────────────────────────────────────────────┐
│                  Agente Principal                          │
│         (Claude Code, Cursor, Zed, qualquer IDE)           │
└───────────────────┬────────────────────────────────────────┘
                    │ REST / MCP / JSON-RPC
┌───────────────────▼────────────────────────────────────────┐
│                  FastAPI Backend                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Auth (JWT) │  │  RBAC (5 lvl)│  │  Rate Limiting   │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└───────────────────┬────────────────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────────────────┐
│                  VCR: Vectora Cognitive Runtime            │
│  ┌──────────────────────┐  ┌──────────────────────────┐   │
│  │  Intent Analysis     │  │  Faithfulness Validation  │   │
│  │  XLM-RoBERTa-small   │  │  score >= 0.70           │   │
│  │  LoRA r=16 + INT8    │  │  <10ms p99               │   │
│  └──────────────────────┘  └──────────────────────────┘   │
└───────────────────┬────────────────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────────────────┐
│                  Context Engine (RAG Pipeline)             │
│  Embed (VoyageAI) → HNSW (LanceDB) → Rerank (VCR) →      │
│  Compact (head/tail) → Validate (VCR)                      │
└───────┬───────────────────────┬────────────────────────────┘
        │                       │
┌───────▼───────┐   ┌───────────▼──────────────────────────┐
│   LanceDB     │   │  PostgreSQL + Redis                   │
│  (vetores)    │   │  sessions, rbac, cache (24h TTL)      │
│  local-first  │   │  via Docker Compose                   │
└───────────────┘   └──────────────────────────────────────┘
```

## Componentes e Responsabilidades

| Componente          | Tecnologia                      | Responsabilidade              | Latência                    |
| ------------------- | ------------------------------- | ----------------------------- | --------------------------- |
| **FastAPI Backend** | FastAPI + Pydantic              | REST/MCP/JSON-RPC, auth, RBAC | < 5ms overhead              |
| **VCR**             | XLM-RoBERTa-small + LoRA + INT8 | Intent analysis, faithfulness | < 10ms p99                  |
| **Context Engine**  | LangChain + LangGraph           | Orquestração do pipeline RAG  | < 500ms p95                 |
| **Embeddings**      | VoyageAI voyage-3-large         | Geração de vetores 1024D      | ~200ms (API) / <1ms (cache) |
| **Vector Search**   | LanceDB HNSW                    | Busca top-100 candidatos      | < 50ms                      |
| **Reranking**       | XLM-RoBERTa (VCR)               | Filtrar top-10 relevantes     | < 10ms                      |
| **PostgreSQL**      | pg8000                          | Usuários, sessões, RBAC, logs | < 5ms                       |
| **Redis**           | redis-py                        | Cache embeddings (24h TTL)    | < 1ms                       |

## Fluxo de uma Query

Uma requisição `search_context` percorre estas etapas em sequência:

1. **FastAPI** recebe a requisição, valida o JWT e verifica permissão `search:execute`.
2. **VCR** analisa a intent em < 8ms: escolhe estratégia `semantic` / `structural` / `hybrid`.
3. **Redis** verifica se o embedding da query está em cache (`embed:{sha256}`, TTL 86400s).
4. **VoyageAI** gera o vetor 1024D se não houver cache (~200ms), salva no Redis.
5. **LanceDB** executa busca HNSW com `metric="cosine"`, retorna top-100 candidatos (< 50ms).
6. **VCR Reranker** ordena por cross-encoder score, filtra top-10 (< 10ms).
7. **Context Engine** compacta com head/tail preservando assinatura e return statement.
8. **VCR Validator** calcula `faithfulness_score` — rejeita se < 0.70.
9. **FastAPI** retorna `{ results, metadata: { latency_ms, faithfulness, precision } }`.

## Isolamento e Segurança

O Vectora implementa dois mecanismos independentes de isolamento:

**RBAC de 5 níveis**: viewer < developer < operator < admin < superadmin. Cada role herda as permissões do anterior. As 15 permissões são verificadas em runtime via decorator `@permission_required("search:execute")`.

**Namespaces LanceDB**: cada codebase indexado fica em um namespace separado. O filtro `.where(f"file LIKE '{namespace}%'")` é aplicado na busca vetorial, garantindo que dados de projetos diferentes não se misturem.

## Protocolos de Acesso

| Protocolo        | Transporte           | Caso de Uso                             |
| ---------------- | -------------------- | --------------------------------------- |
| **REST API**     | HTTP/HTTPS           | Integração programática, webhooks       |
| **MCP**          | STDIO (stdin/stdout) | IDEs: Claude Code, Cursor, Zed          |
| **JSON-RPC 2.0** | HTTP                 | Comunicação inter-componentes           |
| **ACP**          | STDIO                | Controle de editor (edições de arquivo) |

## Princípio Local-First

O Vectora foi projetado para rodar inteiramente no ambiente do desenvolvedor:

- **LanceDB**: arquivos em disco local (`~/.vectora/lancedb/`), sem servidor.
- **XLM-RoBERTa**: inferência CPU, sem chamada de rede, INT8 para < 120MB RAM.
- **PostgreSQL + Redis**: via Docker Compose, locais.
- **VoyageAI**: única dependência externa — usada apenas para geração de embeddings. Pode ser substituída por `embedding_provider=local` (experimental).

## External Linking

| Conceito        | Recurso                        | Link                                                                          |
| --------------- | ------------------------------ | ----------------------------------------------------------------------------- |
| **LangGraph**   | Stateful agent orchestration   | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/) |
| **LanceDB**     | Local vector database          | [lancedb.com/docs](https://lancedb.com/docs)                                  |
| **XLM-RoBERTa** | Multilingual transformer model | [huggingface.co/xlm-roberta-small](https://huggingface.co/xlm-roberta-small)  |
| **VoyageAI**    | High-performance embeddings    | [voyageai.com](https://www.voyageai.com/)                                     |
| **FastAPI**     | Python web framework           | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)                         |
