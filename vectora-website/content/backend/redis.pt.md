---
title: "Redis: Cache e Rate Limiting do Vectora"
slug: redis
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - backend
  - cache
  - embeddings
  - rate-limiting
  - redis
  - sessions
  - storage
  - vectora
---

{{< lang-toggle >}}

{{< section-toggle >}}

Redis é o cache in-memory do Vectora. Responsabilidade principal: armazenar embeddings VoyageAI por 24h, eliminando chamadas repetidas à API. Também gerencia rate limiting por usuário e dados de sessão temporária.

## Conexão

```python
import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)
```

Para produção com retry e timeout:

```python
r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
    retry_on_timeout=True,
)
```

## Namespace de Chaves

Todas as chaves seguem o padrão `prefix:{identificador}` para evitar colisões entre funcionalidades.

| Prefixo              | Conteúdo                              | TTL          |
| -------------------- | ------------------------------------- | ------------ |
| `embed:{sha256}`     | Embedding VoyageAI (JSON array 1024D) | 86400s (24h) |
| `rate:{user_id}`     | Contador de requests por minuto       | 60s          |
| `session:{token_id}` | Dados de sessão temporária            | 3600s (1h)   |
| `vcr:{query_hash}`   | Score VCR cacheado por query          | 3600s        |

## Cache de Embeddings

Padrão cache-aside: verifica Redis antes de chamar VoyageAI API.

```python
import hashlib
import json
import voyageai

voyage = voyageai.Client(api_key="...")

def embed_with_cache(texts: list[str]) -> list[list[float]]:
    results = [None] * len(texts)
    to_fetch: list[tuple[int, str]] = []

    for i, text in enumerate(texts):
        key = f"embed:{hashlib.sha256(text.encode()).hexdigest()}"
        cached = r.get(key)
        if cached:
            results[i] = json.loads(cached)
        else:
            to_fetch.append((i, text))

    if to_fetch:
        indices, fetch_texts = zip(*to_fetch)
        embeddings = voyage.embed(
            list(fetch_texts),
            model="voyage-4",
        ).embeddings

        pipe = r.pipeline()
        for idx, embedding in zip(indices, embeddings):
            key = f"embed:{hashlib.sha256(fetch_texts[list(indices).index(idx)].encode()).hexdigest()}"
            pipe.setex(key, 86400, json.dumps(embedding))
            results[idx] = embedding
        pipe.execute()

    return results
```

Pipeline Redis (`pipe.execute()`) agrupa os `SETEX` em uma única chamada de rede, reduzindo latência de N round-trips para 1.

## Rate Limiting

Limita requests por usuário usando o padrão sliding window com `INCR` + `EXPIRE`.

```python
def check_rate_limit(user_id: str, limit: int = 60) -> bool:
    key = f"rate:{user_id}"
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, 60)
    results = pipe.execute()
    count = results[0]
    return count <= limit

def require_rate_limit(user_id: str) -> None:
    if not check_rate_limit(user_id):
        raise RateLimitError(f"Rate limit exceeded for user {user_id}")
```

## Cache de Sessões Temporárias

Para dados de sessão que não precisam de persistência durável:

```python
import json

def set_session_data(token_id: str, data: dict, ttl: int = 3600) -> None:
    key = f"session:{token_id}"
    r.setex(key, ttl, json.dumps(data))

def get_session_data(token_id: str) -> dict | None:
    key = f"session:{token_id}"
    raw = r.get(key)
    if not raw:
        return None
    return json.loads(raw)

def revoke_session(token_id: str) -> None:
    r.delete(f"session:{token_id}")
```

## Cache de Scores VCR

Evita re-execução do reranker para queries idênticas:

```python
def get_cached_vcr_score(query: str) -> float | None:
    key = f"vcr:{hashlib.sha256(query.encode()).hexdigest()}"
    val = r.get(key)
    return float(val) if val else None

def cache_vcr_score(query: str, score: float, ttl: int = 3600) -> None:
    key = f"vcr:{hashlib.sha256(query.encode()).hexdigest()}"
    r.setex(key, ttl, str(score))
```

## Health Check

```python
def redis_healthy() -> bool:
    try:
        return r.ping()
    except redis.ConnectionError:
        return False
```

Exposto via `GET /health`:

```json
{
  "components": {
    "redis": { "status": "connected" }
  }
}
```

## Setup via Docker

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

`allkeys-lru` garante que quando a memória atingir 512MB, o Redis evicte as chaves menos usadas recentemente — adequado para cache de embeddings.

## External Linking

| Conceito         | Recurso                              | Link                                                                        |
| ---------------- | ------------------------------------ | --------------------------------------------------------------------------- |
| **Redis 7**      | Redis documentation                  | [redis.io/docs](https://redis.io/docs/)                                     |
| **redis-py**     | Python Redis client                  | [redis-py.readthedocs.io](https://redis-py.readthedocs.io/)                 |
| **LRU Eviction** | Redis eviction policies              | [redis.io/docs/manual/eviction](https://redis.io/docs/manual/eviction/)     |
| **Pipeline**     | Redis pipelining para batch commands | [redis.io/docs/manual/pipelining](https://redis.io/docs/manual/pipelining/) |
| **RESP3**        | Redis Serialization Protocol 3       | [redis.io/topics/resp3](https://redis.io/topics/resp3)                      |
