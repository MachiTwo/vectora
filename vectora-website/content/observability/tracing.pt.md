---
title: Rastreamento Distribuído
slug: tracing
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - tracing
  - distributed-tracing
  - jaeger
  - observability
  - vectora
---

{{< lang-toggle >}}

**Rastreamento distribuído** permite visualizar o caminho completo de uma requisição através de múltiplos serviços. Em Vectora, rastreia-se desde a requisição HTTP → search → embedding → LanceDB → LLM.

## Conceitos de Tracing

| Conceito    | Descrição                                   |
| ----------- | ------------------------------------------- |
| **Trace**   | Caminho completo de uma requisição          |
| **Span**    | Segmento de uma operação dentro de um trace |
| **Context** | Identificadores propagados entre spans      |

## Fluxo de Trace em Vectora

```text
POST /search (trace_id: abc123)
  │
  ├─ span: "validate_query"
  │  ├─ span: "check_bucket_access"
  │  └─ latency: 2ms
  │
  ├─ span: "embed_query"
  │  ├─ span: "redis_get_cache"
  │  └─ latency: 150ms (API)
  │
  ├─ span: "lancedb_search"
  │  ├─ span: "hnsw_search"
  │  └─ latency: 45ms
  │
  ├─ span: "rerank"
  │  ├─ span: "xlm_roberta"
  │  └─ latency: 8ms
  │
  └─ TOTAL: 205ms
```

## Setup do Jaeger

### 1. Iniciar Jaeger

```bash
# Docker (recomendado)
docker run -d \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 6831:6831/udp \
  -p 16686:16686 \
  jaegertracing/all-in-one

# Acessar: http://localhost:16686
```

### 2. Instalar Bibliotecas Python

```bash
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-exporter-jaeger-thrift
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-instrumentation-requests
```

## Instrumentação com OpenTelemetry

### Configuração Global

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Configurar tracer
jaeger_exporter = JaegerExporter(
    agent_host_name='localhost',
    agent_port=6831,
)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrumentar FastAPI e requests
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Obter tracer
tracer = trace.get_tracer(__name__)
```

### Spans Customizados

```python
from vectora.search import search_with_tracing

def search_with_tracing(query: str, bucket_id: str, top_k: int = 10):
    # Span pai (automático via FastAPI)
    with tracer.start_as_current_span("search_operation") as span:
        span.set_attribute("query", query)
        span.set_attribute("bucket_id", bucket_id)
        span.set_attribute("top_k", top_k)

        # Span filho 1: Embeddings
        with tracer.start_as_current_span("embed_query") as embed_span:
            embed_span.set_attribute("query_length", len(query))
            try:
                embedding = embed_query(query)
                embed_span.set_attribute("cache_hit", True)
            except Exception as e:
                embed_span.set_attribute("error", True)
                embed_span.record_exception(e)
                raise

        # Span filho 2: LanceDB search
        with tracer.start_as_current_span("lancedb_search") as search_span:
            search_span.set_attribute("num_candidates", 100)
            results = lancedb_search(embedding, top_k=100)
            search_span.set_attribute("num_results", len(results))

        # Span filho 3: Reranking
        with tracer.start_as_current_span("rerank") as rerank_span:
            rerank_span.set_attribute("reranker_model", "xlm-roberta")
            reranked = rerank(results, query, top_k=top_k)
            rerank_span.set_attribute("num_reranked", len(reranked))

        span.set_attribute("total_results", len(reranked))
        return reranked
```

## Propagação de Contexto

Para requisições em cadeia (ex: Vectora chamando LLM API):

```python
from opentelemetry.propagate import inject
from opentelemetry.propagators.textmap import DefaultGetter, DefaultSetter
import requests

def call_llm_with_trace(prompt: str):
    # Incluir contexto de trace no header
    headers = {}
    inject(headers)

    # Requisição HTTP carrega o trace
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={**headers, "Authorization": f"Bearer {API_KEY}"},
        json={"model": "claude-sonnet-4-6", "messages": [{"role": "user", "content": prompt}]}
    )
    return response.json()
```

## Visualização em Jaeger

### 1. Acessar Dashboard

- URL: `http://localhost:16686`
- Selecionar serviço: `vectora`
- Ver traces com latência

### 2. Análise de Trace

Para uma requisição de search:

```text
Trace ID: abc123def456
Service: vectora
Duration: 205ms
Status: Success

Spans:
├─ POST /search (205ms)
│  ├─ validate_query (2ms)
│  ├─ embed_query (150ms)  ← slowest
│  ├─ lancedb_search (45ms)
│  └─ rerank (8ms)
```

## Rastreamento de LLM Calls

Rastrear chamadas para Claude/OpenAI:

```python
def invoke_llm_with_trace(prompt: str, model: str):
    with tracer.start_as_current_span("llm_invocation") as span:
        span.set_attribute("model", model)
        span.set_attribute("prompt_tokens", len(prompt.split()))

        # Propagar contexto
        headers = {}
        inject(headers)

        response = client.messages.create(
            model=model,
            headers=headers,
            messages=[{"role": "user", "content": prompt}]
        )

        span.set_attribute("output_tokens", response.usage.output_tokens)
        span.set_attribute("total_tokens",
                          response.usage.input_tokens + response.usage.output_tokens)
        return response
```

## Troubleshooting

### Traces não aparecem em Jaeger

```bash
# 1. Verificar Jaeger está rodando
docker ps | grep jaeger

# 2. Verificar conectividade
telnet localhost 6831

# 3. Verificar configuração em código
# - JaegerExporter com host/port correto
# - TracerProvider registrado
# - Spans criados

# 4. Verificar logs
docker logs <jaeger_container>
```

### Alto latency de traces

```python
# Usar BatchSpanProcessor ao invés de SimpleSpanProcessor
# (por padrão, já usa batch)

# Configurar tamanho do batch
processor = BatchSpanProcessor(
    jaeger_exporter,
    schedule_delay_millis=5000,  # 5s
    max_queue_size=2048,
    max_export_batch_size=512,
)
```

### Traces perdidos

```yaml
# Aumentar buffer do Jaeger
SPAN_STORAGE_TYPE: badger
BADGER_EPHEMERAL: false
BADGER_DIRECTORY_VALUE: /badger/data
BADGER_DIRECTORY_KEY: /badger/key
```

## External Linking

| Conceito                | Recurso                    | Link                                                                                                    |
| ----------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------- |
| **OpenTelemetry**       | Instrumentation standard   | [opentelemetry.io](https://opentelemetry.io/)                                                           |
| **Jaeger**              | Distributed tracing        | [www.jaegertracing.io](https://www.jaegertracing.io/)                                                   |
| **Distributed Tracing** | Concepts and patterns      | [opentelemetry.io/docs/concepts/signals/traces](https://opentelemetry.io/docs/concepts/signals/traces/) |
| **W3C Trace Context**   | Standard for propagation   | [w3c.github.io/trace-context](https://w3c.github.io/trace-context/)                                     |
| **Zipkin**              | Alternative tracing system | [zipkin.io](https://zipkin.io/)                                                                         |
