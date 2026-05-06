---
title: "VoyageAI: Embeddings para Busca Semântica"
slug: voyage
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - embeddings
  - lancedb
  - models
  - rag
  - redis
  - semantic-search
  - vectora
  - voyage
draft: false
---

{{< lang-toggle >}}

{{< section-toggle >}}

O Vectora usa VoyageAI como provedor exclusivo de embeddings. O modelo voyage-4 converte código e texto em vetores 1024D otimizados para busca semântica em codebases — incluindo múltiplas linguagens de programação.

## Por que VoyageAI é Fixo

No Vectora, embeddings não são swappáveis no MVP por uma razão prática: **todos os vetores armazenados no LanceDB foram gerados com o mesmo modelo**. Trocar de provedor exigiria reindexar todo o codebase. VoyageAI voyage-4 foi escolhido por:

- MTEB Code retrieval ranking entre os melhores modelos de código
- Suporte nativo a múltiplas linguagens (Python, TypeScript, Go, Rust, Java)
- Preço competitivo: $0.10 por 2M tokens
- Dimensão 1024D — balanço ideal entre precisão e uso de disco no LanceDB

## Modelo: voyage-4

| Especificação        | Valor                                       |
| -------------------- | ------------------------------------------- |
| **Dimensões**        | 1024D                                       |
| **Contexto máximo**  | 32.000 tokens                               |
| **Preço**            | $0.10 / 2M tokens                           |
| **Latência (API)**   | ~150-200ms                                  |
| **Latência (cache)** | < 1ms (Redis)                               |
| **Suporte a código** | Python, TS, Go, Rust, Java, C++, e mais     |
| **Input types**      | `query` e `document` (otimizados separados) |

## Integração no Vectora

O pipeline de embedding segue este fluxo em toda requisição de busca:

```python
import voyageai
import redis
import hashlib

voyage = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
r = redis.Redis(host="localhost", port=6379)

def embed_query(query: str) -> list[float]:
    key = f"embed:{hashlib.sha256(query.encode()).hexdigest()}"

    cached = r.get(key)
    if cached:
        return json.loads(cached)  # < 1ms

    result = voyage.embed([query], model="voyage-4", input_type="query")
    vector = result.embeddings[0]

    r.setex(key, 86400, json.dumps(vector))  # TTL 24h
    return vector  # ~200ms
```

O parâmetro `input_type="query"` otimiza o vetor para consultas. Durante a indexação usa-se `input_type="document"` para os chunks de código.

## Indexação em Batch

Para indexar codebases grandes, o Vectora envia chunks em batches de 128 — limite da API VoyageAI:

```python
BATCH_SIZE = 128

def index_chunks(chunks: list[dict]) -> None:
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        texts = [c["content"] for c in batch]

        result = voyage.embed(
            texts,
            model="voyage-4",
            input_type="document",
        )

        rows = [
            {
                "id": c["id"],
                "file": c["file"],
                "content": c["content"],
                "embedding": emb,
            }
            for c, emb in zip(batch, result.embeddings)
        ]
        table.add(rows)
```

## Configuração

```bash
# Configurar chave de API
vectora config set voyage_api_key sk-voyage-xxx

# Verificar conexão
vectora health
# voyage: ok (quota: 1.8M/2M tokens)
```

Variável de ambiente alternativa:

```bash
export VOYAGE_API_KEY=sk-voyage-xxx
```

## Cache Redis

Embeddings são cacheados por query (não por documento). O cache usa SHA-256 da query como chave:

| Chave Redis               | TTL          | Conteúdo                                    |
| ------------------------- | ------------ | ------------------------------------------- |
| `embed:{sha256_da_query}` | 86400s (24h) | Vetor float32\[1024\] serializado como JSON |

Queries repetidas dentro de 24h custam 0 tokens e retornam em < 1ms.

## External Linking

| Conceito             | Recurso                                   | Link                                                                                     |
| -------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------- |
| **voyage-4**         | VoyageAI model docs                       | [docs.voyageai.com/docs/embeddings](https://docs.voyageai.com/docs/embeddings)           |
| **VoyageAI Pricing** | Pricing page                              | [voyageai.com/pricing](https://www.voyageai.com/pricing/)                                |
| **MTEB Benchmark**   | Embedding benchmark leaderboard           | [huggingface.co/spaces/mteb/leaderboard](https://huggingface.co/spaces/mteb/leaderboard) |
| **LanceDB**          | Vector storage that stores voyage vectors | [lancedb.com/docs](https://lancedb.com/docs)                                             |
