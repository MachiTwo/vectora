---
title: "Embeddings: VoyageAI no Vectora"
slug: embeddings
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - ai
  - architecture
  - concepts
  - embeddings
  - rag
  - reranker
  - redis
  - vector-search
  - vectora
  - voyage
---

{{< lang-toggle >}}

{{< section-toggle >}}

O Vectora usa VoyageAI (modelo voyage-4) para converter código e texto em vetores 1024D. Resultados são cacheados em Redis por 24h para reduzir custos e latência. Embeddings genéricas falham com código — VoyageAI foi otimizado especificamente para código estruturado e documentação técnica.

## O Problema das Embeddings Genéricas

Embeddings treinadas apenas em texto não capturam conceitos fundamentais de programação:

- Não distinguem entre uma assinatura de função e seu corpo.
- Não relacionam `verifyToken` e `validateJWT` como equivalentes semânticos.
- Não entendem padrões de concorrência (`async/await` vs callbacks).

VoyageAI foi treinado em um corpus massivo de código real, capturando a semântica intrínseca de estruturas de programação.

## Especificações: voyage-4

| Aspecto               | Detalhe                        |
| --------------------- | ------------------------------ |
| **Modelo**            | voyage-4                       |
| **Dimensionalidade**  | 1024 dimensões                 |
| **Custo**             | ~$0.10 por 2M tokens           |
| **Latência (API)**    | ~200ms por request             |
| **Latência (cached)** | <1ms (Redis)                   |
| **Suporte**           | 100+ linguagens de programação |

## Arquitetura Interna

### 1. Tokenização Semântica

VoyageAI compreende a estrutura semântica do código: reconhece parâmetros, tipos de retorno, blocos de controle de fluxo e mapeia esses elementos para o espaço vetorial.

### 2. Encoding Vetorial 1024D

Cada uma das 1024 dimensões captura um aspecto semântico específico: autenticação, persistência, concorrência, tratamento de erros, etc. Código com a mesma função lógica em linguagens diferentes (Python e TypeScript) são mapeados para posições próximas.

### 3. Normalização L2

Todos os vetores são normalizados (L2), garantindo que cosine similarity funcione via produto escalar (dot product) — 4x mais rápido que distância euclidiana.

## Integração: VoyageAI + Redis Cache

```python
import voyageai
import redis
import json
import hashlib

voyage = voyageai.Client(api_key="sk-voyage-xxx")
r = redis.Redis()

def embed(texts: list[str]) -> list[list[float]]:
    results = []
    to_fetch = []
    indices = []

    for i, text in enumerate(texts):
        cache_key = f"embed:{hashlib.sha256(text.encode()).hexdigest()}"
        cached = r.get(cache_key)
        if cached:
            results.append(json.loads(cached))
        else:
            to_fetch.append(text)
            indices.append(i)
            results.append(None)

    if to_fetch:
        embeddings = voyage.embed(to_fetch, model="voyage-4").embeddings
        for idx, embedding in zip(indices, embeddings):
            cache_key = f"embed:{hashlib.sha256(to_fetch[indices.index(idx)].encode()).hexdigest()}"
            r.setex(cache_key, 86400, json.dumps(embedding))
            results[idx] = embedding

    return results
```

## Capacidades Multimodais

- **Código Puro**: Encontra validadores mesmo que a query use palavras diferentes das usadas no código.
- **Documentação + Código**: Relaciona comentários e docstrings com implementações reais.
- **Cross-Language**: Python e TypeScript com a mesma lógica têm embeddings similares.
- **Semântica Avançada**: Identifica padrões como "race conditions", "deadlocks", "null safety".

## Performance e Otimização

### Cache Redis (TTL 24h)

Queries repetidas usam embedding cacheado:

```text
Primeira query "Como validar JWT?": 200ms (VoyageAI API)
Segunda query "Como validar JWT?": <1ms (Redis cache)
Economia de custo: 99.9% nas queries repetidas
```

### Batching para Indexação

Ao indexar um codebase completo, agrupe chunks em batches de 128:

```python
BATCH_SIZE = 128

for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i:i + BATCH_SIZE]
    embeddings = voyage.embed(
        [c["content"] for c in batch],
        model="voyage-4"
    ).embeddings
    # Inserir no LanceDB
```

## External Linking

| Conceito          | Recurso                              | Link                                                                                     |
| ----------------- | ------------------------------------ | ---------------------------------------------------------------------------------------- |
| **VoyageAI**      | High-performance embeddings para RAG | [voyageai.com](https://www.voyageai.com/)                                                |
| **VoyageAI Docs** | Documentação de embeddings           | [docs.voyageai.com/docs/embeddings](https://docs.voyageai.com/docs/embeddings)           |
| **Redis**         | In-memory cache para embeddings      | [redis.io/docs](https://redis.io/docs/)                                                  |
| **LanceDB**       | Vector database local                | [lancedb.com/docs](https://lancedb.com/docs)                                             |
| **MTEB**          | Benchmark de modelos de embedding    | [huggingface.co/spaces/mteb/leaderboard](https://huggingface.co/spaces/mteb/leaderboard) |
