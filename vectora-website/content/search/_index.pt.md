---
title: "Search: Pipeline de Busca Semântica"
slug: search
date: 2026-05-03T23:00:00-03:00
type: docs
sidebar:
  open: true
tags:
  - ai
  - architecture
  - concepts
  - embeddings
  - lancedb
  - rag
  - reranker
  - search
  - semantic-search
  - vector-search
  - vectora
  - voyage
  - xlm-roberta
draft: false
---

{{< lang-toggle >}}

{{< section-toggle >}}

Search é como o Vectora entende o que você está procurando e encontra o código mais relevante no repositório. O pipeline tem 4 etapas: Embedding (VoyageAI) → Busca Vetorial (LanceDB HNSW) → Reranking (XLM-RoBERTa local) → Compactação. Tudo roda localmente — sem servidores externos durante a recuperação.

## Componentes Principais

O motor de busca é composto por camadas especializadas que filtram e refinam informações em cada etapa de recuperação.

### Embeddings (VoyageAI)

Representação vetorial 1024D de código usando VoyageAI API (voyage-4). Resultados são cacheados em Redis por 24h para reduzir latência e custos.

**[Ver Embeddings](./embeddings.md)**

### Vector Search (LanceDB)

Busca de alta dimensionalidade usando HNSW (Hierarchical Navigable Small World) no LanceDB local. Índices armazenados em disco — sem servidor externo. Retorna top-100 candidatos em < 50ms.

**[Ver Vector Search](./vector-search.md)**

### Reranker Local (XLM-RoBERTa)

XLM-RoBERTa-small (parte do VCR) refina top-100 para top-10 com score de relevância. Roda em CPU, latência < 10ms. Substitui Voyage Rerank com modelo 100% local.

**[Ver Reranker Local](./reranker-local.md)**

## Fluxo do Pipeline

VCR orquestra o pipeline decidindo quando usar busca semântica, estrutural ou híbrida.

```text
Query
  |
  +-> VCR: Roteamento de estratégia (auto/semantic/structural/hybrid)
  |
  +-> Embeddings (VoyageAI, cached Redis) → vetor 1024D
  |
  +-> Vector Search (LanceDB HNSW) → top-100 candidatos
  |
  +-> Reranking (XLM-RoBERTa local) → top-10 relevantes
  |
  +-> Compactação (head/tail) → contexto reduzido
  |
  +-> VCR: Validação de faithfulness
  |
  +-> Resultado final
```

## Métricas de Performance

| Etapa                       | Latência Target                  | Custo           |
| --------------------------- | -------------------------------- | --------------- |
| **Embeddings (VoyageAI)**   | <200ms (uncached), <1ms (cached) | $0.10/2M tokens |
| **Vector Search (LanceDB)** | <50ms                            | Grátis (local)  |
| **Reranking (XLM-RoBERTa)** | <10ms                            | Grátis (local)  |
| **Total (sem LLM)**         | <500ms p95                       | ~$0.001/query   |

## External Linking

| Conceito        | Recurso                                | Link                                                                         |
| --------------- | -------------------------------------- | ---------------------------------------------------------------------------- |
| **LanceDB**     | Vector database local para RAG         | [lancedb.com/docs](https://lancedb.com/docs)                                 |
| **VoyageAI**    | High-performance embeddings para RAG   | [voyageai.com](https://www.voyageai.com/)                                    |
| **XLM-RoBERTa** | Modelo multilíngue de reranking        | [huggingface.co/xlm-roberta-small](https://huggingface.co/xlm-roberta-small) |
| **RAG**         | Retrieval-Augmented Generation         | [arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)                 |
| **HNSW**        | Efficient approximate nearest neighbor | [arxiv.org/abs/1603.09320](https://arxiv.org/abs/1603.09320)                 |
