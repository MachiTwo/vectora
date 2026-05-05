---
title: "Redis: Cache e Sessões"
slug: redis-memory
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - cache
  - embedding-cache
  - memory
  - redis
  - session
  - storage
  - ttl
  - vectora
---

{{< lang-toggle >}}

Redis armazena **cache TTL (Time To Live)** de embeddings gerados pela API VoyageAI e **sessões JWT** de usuários autenticados. Ele é essencial para latência baixa (<1ms em cache hit) e reduzir custos de embedding.

## Estratégia de Cache

### Cache de Embeddings

Toda query é embedada pela VoyageAI e o resultado é cacheado no Redis por **24 horas** (86400 segundos).

```python
import redis
import hashlib

r = redis.Redis(host="localhost", port=6379)

# Gerar chave: SHA256 da query
query = "how to implement vector search"
key = f"embed:{hashlib.sha256(query.encode()).hexdigest()}"

# Verificar cache
cached = r.get(key)
if cached:
    vector = json.loads(cached)  # < 1ms
    return vector

# Se não encontrou, chamar VoyageAI
result = voyage.embed([query], model="voyage-3-large", input_type="query")
vector = result.embeddings[0]

# Guardar no cache com TTL de 24h
r.setex(key, 86400, json.dumps(vector))
return vector
```

**Benefícios:**

- Queries repetidas custam **0 tokens** de embedding
- Latência reduzida de ~200ms (VoyageAI API) para <1ms (Redis)
- Economias de até 90% em custos VoyageAI para workloads com queries frequentes

### Cache de Sessões

Tokens JWT refresh são armazenados para revogação e validação:

```python
# Revogar token (logout)
token_jti = decode_jwt(token)["jti"]
r.setex(f"revoked:{token_jti}", 604800, "1")  # 7 dias = 604800s

# Verificar se token foi revogado
is_revoked = r.exists(f"revoked:{token_jti}")
if is_revoked:
    raise UnauthorizedError("Token revoked")
```

## Estrutura de Chaves

| Padrão                      | TTL          | Conteúdo                    | Exemplo               |
| --------------------------- | ------------ | --------------------------- | --------------------- |
| `embed:{sha256}`            | 86400s (24h) | Vetor float32[1024] em JSON | `embed:a3b5...`       |
| `session:{user_id}`         | 604800s (7d) | Dados de sessão             | `session:usr-123`     |
| `revoked:{jti}`             | 604800s (7d) | Token revogado              | `revoked:abc-xyz`     |
| `rate:{user_id}:{endpoint}` | 60s          | Contador de requisições     | `rate:usr-123:search` |

## Configuração

Via ambiente:

```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0
export REDIS_PASSWORD=  # vazio se sem senha
```

Via config CLI:

```bash
vectora config set redis_host localhost
vectora config set redis_port 6379
vectora config set redis_db 0
```

Verificar conexão:

```bash
vectora health
# redis: ok (uptime 123h, mem 52.4M)
```

## Policies de Eviction

Se o Redis atingir `maxmemory`, ele remove chaves baseado na política configurada:

```bash
# Mostrar config atual
redis-cli CONFIG GET maxmemory
redis-cli CONFIG GET maxmemory-policy

# Configurar (exemplo: 2GB, remove LRU mais antigo)
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

Policies recomendadas:

| Policy           | Comportamento                               | Ideal para            |
| ---------------- | ------------------------------------------- | --------------------- |
| `allkeys-lru`    | Remove chave LRU (menos recentemente usada) | Cache genérico        |
| `volatile-lru`   | Remove chave LRU com TTL                    | Cache com expiração   |
| `allkeys-random` | Remove aleatoriamente                       | Workloads previsíveis |
| `noeviction`     | Recusa escrita se cheio                     | Dados críticos        |

O Vectora recomenda **`volatile-lru`** para não perder sessões ativas:

```bash
redis-cli CONFIG SET maxmemory-policy volatile-lru
redis-cli CONFIG REWRITE  # Salvar para redis.conf
```

## Monitoramento

Ver uso de memória:

```bash
redis-cli INFO memory
# used_memory: 52428800 (50M)
# used_memory_peak: 104857600 (100M)
# mem_fragmentation_ratio: 1.2
```

Ver chaves armazenadas:

```bash
# Contar chaves por padrão
redis-cli --scan --pattern "embed:*" | wc -l
redis-cli --scan --pattern "session:*" | wc -l

# Listar chaves grandes (potencial otimização)
redis-cli --bigkeys
```

Monitorar hits vs misses:

```bash
redis-cli INFO stats
# keyspace_hits: 45000
# keyspace_misses: 5000
# Hit rate: 90%
```

## Backup e Replicação

Configurar RDB (snapshot) e AOF (log):

```bash
# redis.conf
save 900 1       # Snapshot a cada 900s com 1 mudança
save 300 10      # Snapshot a cada 300s com 10 mudanças
appendonly yes   # Enable AOF
appendfsync everysec  # Fsync a cada segundo
```

Fazer backup manual:

```bash
redis-cli BGSAVE
# Background saving started
redis-cli LASTSAVE
# 1625097600
```

Para alta disponibilidade, usar **Redis Sentinel** ou **Redis Cluster**:

```bash
# Sentinel monitoring (sentinel.conf)
sentinel monitor vectora-master 127.0.0.1 6379 1
sentinel down-after-milliseconds vectora-master 5000
sentinel parallel-syncs vectora-master 1
sentinel failover-timeout vectora-master 10000
```

## Troubleshooting

**Redis não conecta:**

```bash
redis-cli ping
# PONG (sucesso)
# Error: Connection refused (falha)
```

**Memória alta:**

```bash
redis-cli MEMORY STATS
# Find largest keys
redis-cli --bigkeys
# Delete old embeddings manually
redis-cli DEL "embed:*"  # Cuidado!
```

**Performance degradada:**

```bash
# Checar latência
redis-cli --latency
# Min: 0.01ms, Max: 5.23ms, Avg: 0.18ms

# Monitorar comandos lentos
redis-cli CONFIG SET slowlog-log-slower-than 10000  # 10ms
redis-cli SLOWLOG GET 10
```

## External Linking

| Conceito              | Recurso                               | Link                                                                                 |
| --------------------- | ------------------------------------- | ------------------------------------------------------------------------------------ |
| **Redis Official**    | Redis documentation and community     | [redis.io/docs](https://redis.io/docs/)                                              |
| **Redis Python**      | redis-py client library               | [github.com/redis/redis-py](https://github.com/redis/redis-py)                       |
| **Eviction Policies** | Understanding Redis memory management | [redis.io/docs/reference/eviction](https://redis.io/docs/reference/eviction)         |
| **Redis Sentinel**    | High availability for Redis           | [redis.io/docs/management/sentinel](https://redis.io/docs/management/sentinel)       |
| **Redis Persistence** | RDB and AOF persistence               | [redis.io/docs/management/persistence](https://redis.io/docs/management/persistence) |
