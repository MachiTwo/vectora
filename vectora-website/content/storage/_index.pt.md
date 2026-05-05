---
title: Armazenamento e Persistência
slug: storage
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - database
  - lancedb
  - persistence
  - postgresql
  - redis
  - storage
  - vectora
---

{{< lang-toggle >}}

O Vectora utiliza três camadas de armazenamento especializadas: **PostgreSQL** para metadados e contexto estruturado, **Redis** para cache de embeddings e sessões, e **LanceDB** para busca vetorial local.

Cada camada tem uma responsabilidade bem definida e não pode ser substituída no MVP:

| Camada         | Função                                    | Localidade   | Tradeoff                    |
| -------------- | ----------------------------------------- | ------------ | --------------------------- |
| **PostgreSQL** | Metadados, contexto, usuários, permissões | Remoto/Local | ACID, escalabilidade        |
| **Redis**      | Cache TTL (embeddings, sessões)           | Remoto/Local | Volatilidade, latência <1ms |
| **LanceDB**    | Índices vetoriais HNSW (busca semântica)  | Local        | Não distribuído, <50ms p99  |

## Fluxo de Dados

```text
Query → Redis (cache)
     ├─ HIT: vetor em < 1ms
     └─ MISS: VoyageAI API (~200ms) → Redis + LanceDB
           → LanceDB (HNSW search) → <50ms
           → PostgreSQL (metadados + contexto)
           → XLM-RoBERTa reranking (local, <10ms)
           → LLM (Claude/GPT/Gemini) → 1-5s
```

## Próximas Etapas

1. **[PostgreSQL](./postgresql.md)** — Configuração, schema, queries
2. **[Redis](./redis-memory.md)** — Cache de embeddings, TTL, eviction policies
3. **[LanceDB](./lancedb-vectors.md)** — Índices vetoriais HNSW, busca semântica

## External Linking

| Conceito              | Recurso                             | Link                                                                           |
| --------------------- | ----------------------------------- | ------------------------------------------------------------------------------ |
| **PostgreSQL**        | Official PostgreSQL documentation   | [postgresql.org/docs](https://www.postgresql.org/docs/)                        |
| **Redis**             | Redis data structures and commands  | [redis.io/docs/data-types](https://redis.io/docs/data-types)                   |
| **LanceDB**           | Vector database for AI applications | [lancedb.com/docs](https://lancedb.com/docs)                                   |
| **HNSW Algorithm**    | Hierarchical Navigable Small World  | [arxiv.org/abs/1802.02413](https://arxiv.org/abs/1802.02413)                   |
| **Voyage Embeddings** | voyage-3-large model specs          | [docs.voyageai.com/docs/embeddings](https://docs.voyageai.com/docs/embeddings) |
