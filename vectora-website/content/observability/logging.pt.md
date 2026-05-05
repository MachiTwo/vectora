---
title: Logging Estruturado
slug: logging
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - logging
  - structured-logs
  - observability
  - json
  - vectora
---

{{< lang-toggle >}}

**Logging estruturado** em Vectora significa registrar eventos como JSON com contexto consistente. Cada log contém: `timestamp`, `level`, `message`, `request_id`, `user_id`, `latency_ms`, `error_type`.

## Configuração de Logging

Vectora usa `structlog` com formatação JSON:

```python
import structlog

# Setup global
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

## Níveis de Log

| Nível    | Uso                    | Exemplo                 |
| -------- | ---------------------- | ----------------------- |
| DEBUG    | Informação detalhada   | Cache hit, SQL query    |
| INFO     | Eventos significativos | Índice adicionado       |
| WARNING  | Situações incomuns     | Cache miss, retentativa |
| ERROR    | Erro tratável          | Embedding falhou        |
| CRITICAL | Falha do sistema       | Banco de dados offline  |

## Estrutura de Log Padrão

Cada log deve incluir:

```json
{
  "timestamp": "2026-05-04T12:34:56.789Z",
  "level": "INFO",
  "logger_name": "vectora.search",
  "message": "Query executed",
  "request_id": "req-abc123",
  "user_id": "user-456",
  "operation": "search",
  "bucket_id": "docs",
  "query": "authentication pattern",
  "latency_ms": 145,
  "top_k": 10,
  "reranked": true,
  "num_results": 8
}
```

## Logging em Contexto de Request

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())

        # Bind request_id ao contexto
        logger.bind(request_id=request_id)
        logger.info("Request received", method=request.method, path=request.url.path)

        start = time.time()
        response = await call_next(request)
        latency_ms = (time.time() - start) * 1000

        logger.info("Request completed", status=response.status_code, latency_ms=latency_ms)
        return response
```

## Logging de Operações Críticas

### Search Operation

```python
def search_with_logging(query: str, bucket_id: str, top_k: int = 10):
    logger = structlog.get_logger()

    logger.info("Search started", query=query, bucket_id=bucket_id, top_k=top_k)

    try:
        # 1. Embeddings
        logger.debug("Embedding query", query_len=len(query))
        embedding = embed_query(query)  # May hit cache
        logger.debug("Embedding retrieved", cache_hit=True, latency_ms=1)

        # 2. LanceDB search
        logger.debug("LanceDB search starting")
        results = lancedb_search(embedding, top_k=100)
        logger.info("LanceDB search completed", num_results=len(results), latency_ms=45)

        # 3. Reranking
        logger.debug("Reranking", num_candidates=len(results))
        reranked = rerank(results, query, top_k=top_k)
        logger.info("Reranking completed", num_reranked=len(reranked), latency_ms=8)

        # 4. Success
        logger.info("Search successful", num_results=len(reranked))
        return reranked

    except Exception as e:
        logger.error("Search failed", error_type=type(e).__name__, error_msg=str(e))
        raise
```

### LLM Call Logging

```python
async def invoke_llm_with_logging(prompt: str, model: str):
    logger = structlog.get_logger()

    logger.info("LLM invocation starting", model=model, prompt_tokens=len(prompt.split()))

    try:
        start = time.time()
        response = await client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        latency_ms = (time.time() - start) * 1000

        logger.info("LLM invocation completed",
                   model=model,
                   output_tokens=response.usage.output_tokens,
                   latency_ms=latency_ms)
        return response

    except Exception as e:
        logger.error("LLM invocation failed", model=model, error=str(e))
        raise
```

## Exportando Logs

### Arquivo Local

```python
import logging.handlers

file_handler = logging.handlers.RotatingFileHandler(
    'vectora.log',
    maxBytes=100_000_000,  # 100MB
    backupCount=10
)
file_handler.setLevel(logging.INFO)
```

### Stdout para Docker/Kubernetes

```python
# JSON é automaticamente enviado para stdout
# Container logs são capturados por Docker/K8s

# Ver logs em tempo real:
# docker logs -f vectora_container
```

### Elasticsearch/ELK Stack

```python
from pythonjsonlogger import jsonlogger
import logging

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

## Troubleshooting

### Logs não aparecem

```bash
# Verificar level de log configurado
vectora config get log_level
# output: INFO

# Aumentar verbosidade
vectora config set log_level DEBUG

# Reiniciar aplicação
systemctl restart vectora
```

### Logs muito grandes

```bash
# Limitar retenção a 7 dias
vectora config set log_retention_days 7

# Compactar logs antigos
find ./logs -name "*.log" -mtime +7 -exec gzip {} \;
```

### Informação sensível em logs

```python
# NUNCA logar:
# - API keys, tokens
# - Senhas, dados de usuário
# - Conteúdo de requisições privadas

# BOM:
logger.info("User search", user_id=user_id, bucket_id=bucket_id)

# RUIM:
logger.info(f"User {user.email} searched for {query_content}")
```

## External Linking

| Conceito            | Recurso                         | Link                                                                                 |
| ------------------- | ------------------------------- | ------------------------------------------------------------------------------------ |
| **structlog**       | Structured logging library      | [www.structlog.org](https://www.structlog.org/)                                      |
| **JSON Logging**    | Best practices guide            | [12factor.net/logs](https://12factor.net/logs)                                       |
| **Python logging**  | Standard library                | [docs.python.org/3/library/logging](https://docs.python.org/3/library/logging.html)  |
| **ELK Stack**       | Elasticsearch, Logstash, Kibana | [www.elastic.co/what-is/elk-stack](https://www.elastic.co/what-is/elk-stack)         |
| **Log Aggregation** | Centralized log collection      | [en.wikipedia.org/wiki/Log_management](https://en.wikipedia.org/wiki/Log_management) |
