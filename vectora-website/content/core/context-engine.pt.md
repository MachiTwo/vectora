---
title: Context Engine
slug: context-engine
date: "2026-05-03T09:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - context-engine
  - lancedb
  - vector-search
  - rag
  - reranker
  - search
  - semantic
  - embeddings
  - concepts
  - ai
  - vectora
  - postgresql
  - redis
---

{{< lang-toggle >}}

{{< section-toggle >}}

O Context Engine é o coração da orquestração inteligente do Vectora. Ele decide o quê, como e quando buscar contexto em seu codebase, evitando ruído e overfetch. Não é apenas busca — é um pipeline de 5 etapas: Embed (VoyageAI) → Search (LanceDB) → Rerank (XLM-RoBERTa local) → Compact → Validate (VCR).

## O Desafio

Agentes genéricos retornam 50 arquivos irrelevantes para uma query simples. O Context Engine filtra por relevância semântica e estrutural, reduzindo para 5-10 chunks altamente relevantes, com latência controlada.

## Arquitetura: LanceDB + VoyageAI + XLM-RoBERTa Local

O Context Engine é composto por quatro camadas:

```text
Query de Usuário
    |
    +-> Embeddings (VoyageAI API, cached no Redis)
    |
    +-> Vector Search (LanceDB com HNSW local)
    |
    +-> Reranking (XLM-RoBERTa-small, <10ms, no Redis)
    |
    +-> Compaction (Redução de contexto)
    |
    +-> VCR Validation (Qualidade do contexto)
    |
    +-> Resultado Final
```

### 1. Embeddings (VoyageAI + Redis Cache)

Query é convertida para embedding 1024D via VoyageAI API. Resultados são cacheados em Redis por 24h para reduzir custos.

```python
# Pseudocódigo
embedding = redis.get(f"query_embedding:{query_hash}")
if not embedding:
    embedding = voyageai.embed(query, model="voyage-4")
    redis.setex(f"query_embedding:{query_hash}", 86400, embedding)
```

### 2. Vector Search (LanceDB com HNSW)

LanceDB executa busca semântica com HNSW (Hierarchical Navigable Small World) em índices locais. Retorna top-100 candidatos ordenados por similaridade.

```python
# Pseudocódigo
results = lancedb.search(embedding, top_k=100)
# Exemplo output: [
#   {id: 1, distance: 0.91, file: "src/auth/jwt.py", ...},
#   {id: 2, distance: 0.88, file: "src/auth/guards.py", ...},
# ]
```

### 3. Reranking (XLM-RoBERTa Local)

XLM-RoBERTa-small executado no CPU refina top-100 para top-10 com score de relevância. Latência < 10ms p99.

```python
# Pseudocódigo
candidates = lancedb.search(embedding, top_k=100)
scores = xlmroberta_reranker(query, [c["content"] for c in candidates])
ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:10]
```

### 4. Compaction (Head/Tail Reduction)

Reduz tamanho de contexto mantendo informação crítica:

- **Head**: Primeiras linhas (imports, definições)
- **Tail**: Últimas linhas (lógica principal)
- **Omit**: Linhas intermediárias (comentários, espaços em branco)

## Estratégias de Busca

### Estratégia 1: Semântica

Usa embeddings para similaridade funcional. Ideal para "Como validar tokens?" ou "Onde está o middleware de CORS?".

### Estratégia 2: Estrutural (AST)

Usa análise de sintaxe para relações de código. Ideal para "Quem chama getUserById?" ou "Que funções herdam de BaseClass?".

### Estratégia 3: Híbrida

Combina semântica + estrutura com BM25 (busca léxica). Ideal para refatoração de módulos ou busca de dependências.

## Configuração

```yaml
context_engine:
  embeddings:
    provider: "voyageai"
    model: "voyage-4"
    dimension: 1024
    cache_ttl: 86400
  search:
    backend: "lancedb"
    index_type: "hnsw"
    top_k: 100
  reranking:
    enabled: true
    model: "xlm-roberta-small"
    cache_ttl: 3600
  compaction:
    enabled: true
    head_lines: 5
    tail_lines: 10
  strategy: "auto"
```

## Fluxo Completo: Exemplo

**Query**: "Como validar tokens JWT?"

```text
Entrada:
  Query: "Como validar tokens JWT?"
  Strategy: auto
  Top-k: 10

Processamento:
  1. Embed (VoyageAI): Query → vetor 1024D
     Latência: 200ms
     Cached: sim (reutilizar próximas 24h)

  2. Search (LanceDB): HNSW → top-100 candidatos
     Latência: 50ms
     Candidatos: [
       {file: "src/auth/jwt.py", score: 0.94, lines: 1-45},
       {file: "src/auth/guards.py", score: 0.87, lines: 12-34},
       ...
     ]

  3. Rerank (XLM-RoBERTa): top-100 → top-10
     Latência: 8ms
     Resultado: [
       {file: "src/auth/jwt.py", score: 0.96, rank: 1},
       {file: "src/auth/guards.py", score: 0.89, rank: 2},
       {file: "src/middleware/auth.py", score: 0.82, rank: 3},
       ...
     ]

  4. Compact: Reduz 25KB → 6KB
     Ratio: 0.24

  5. VCR Validate: Checksum de qualidade
     Faithfulness: 0.91 (alvo > 0.65)

Saída:
  chunks: [
    {
      file: "src/auth/jwt.py",
      lines: "1-5, 20-30",
      score: 0.96,
      content: "def validate_token(token):\n    ..."
    },
    ...
  ]
  metadata: {
    total_latency_ms: 258,
    total_searched: 10000,
    compaction_ratio: 0.24,
    precision: 0.91,
    recall: 0.85
  }
```

## Métricas e Targets

O Context Engine monitora continuamente:

- **Retrieval Precision**: Alvo ≥ 0.80 (% de top-10 realmente relevantes)
- **Retrieval Recall**: Alvo ≥ 0.75 (% de chunks relevantes encontrados)
- **Total Latency P95**: Alvo < 500ms
- **Compaction Ratio**: Alvo < 0.30 (máximo 30% do tamanho original)
- **Cache Hit Rate**: Alvo > 70% (para queries frequentes)

## External Linking

| Conceito                | Recurso                                   | Link                                                                           |
| ----------------------- | ----------------------------------------- | ------------------------------------------------------------------------------ |
| **LanceDB**             | Vector database local de código aberto    | [lancedb.com/docs](https://lancedb.com/docs)                                   |
| **VoyageAI**            | Embeddings de alta performance para RAG   | [voyageai.com/](https://www.voyageai.com/)                                     |
| **VoyageAI Embeddings** | Documentação de embeddings                | [docs.voyageai.com/docs/embeddings](https://docs.voyageai.com/docs/embeddings) |
| **XLM-RoBERTa**         | Modelo multilíngue para reranking         | [huggingface.co/xlm-roberta-small](https://huggingface.co/xlm-roberta-small)   |
| **HNSW**                | Estrutura de indexação vetorial eficiente | [github.com/nmslib/hnswlib](https://github.com/nmslib/hnswlib)                 |
