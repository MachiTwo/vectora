---
title: Métricas e Prometheus
slug: metrics
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - metrics
  - prometheus
  - monitoring
  - observability
  - vectora
---

{{< lang-toggle >}}

**Métricas** em Vectora rastreiam a saúde operacional: latência de requisições, taxa de erro, uso de memória, quantidade de embeddings. Vectora expõe métricas no formato **Prometheus** em `/metrics`.

## Tipos de Métricas

| Tipo      | Descrição                | Exemplo                |
| --------- | ------------------------ | ---------------------- |
| Counter   | Valor que só aumenta     | Total de queries       |
| Gauge     | Valor que sobe e desce   | Memória em uso         |
| Histogram | Distribuição de latência | Latência de busca      |
| Summary   | Quantis de latência      | p50, p95, p99 latência |

## Métricas Padrão do Vectora

Vectora coleta automaticamente:

```text
# Latência HTTP
http_request_duration_seconds{method="POST", path="/search", status="200"}: 0.145

# Taxa de requisição
http_requests_total{method="POST", path="/search", status="200"}: 1234

# Taxa de erro
http_requests_total{method="POST", path="/search", status="500"}: 45

# Memória em uso
process_resident_memory_bytes: 524288000

# Cache hits
vectora_cache_hits_total{type="embedding"}: 5000
vectora_cache_misses_total{type="embedding"}: 1250

# LanceDB performance
vectora_search_latency_ms{bucket="docs"}: [distribution]
vectora_rerank_latency_ms{model="xlm-roberta"}: [distribution]

# Índices
vectora_indexed_chunks_total{bucket="docs"}: 5000
vectora_indexed_files_total{bucket="docs"}: 125
```

## Setup do Prometheus

### 1. Instalar Prometheus

```bash
# Download
curl -OL https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xzf prometheus-2.45.0.linux-amd64.tar.gz

# Configurar
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'vectora'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
EOF

# Executar
./prometheus --config.file=prometheus.yml
```

### 2. Acessar Prometheus

Abra `http://localhost:9090` no navegador.

## Instrumentation em Código Python

### Middleware de Métricas

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Definir métricas
request_count = Counter(
    'vectora_requests_total',
    'Total de requisições',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'vectora_request_duration_seconds',
    'Latência de requisição',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'vectora_active_requests',
    'Requisições em andamento',
    ['method', 'endpoint']
)

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        method = scope['method']
        path = scope['path']

        active_requests.labels(method=method, endpoint=path).inc()
        start = time.time()

        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                status = message['status']
                duration = time.time() - start

                request_count.labels(
                    method=method,
                    endpoint=path,
                    status=status
                ).inc()

                request_duration.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)

                active_requests.labels(method=method, endpoint=path).dec()

            await send(message)

        await self.app(scope, receive, send_wrapper)
```

### Métricas Customizadas

```python
from prometheus_client import Histogram, Counter

# Latência de search
search_latency = Histogram(
    'vectora_search_latency_ms',
    'Latência de busca vetorial',
    ['bucket', 'top_k'],
    buckets=(10, 50, 100, 250, 500, 1000)
)

# Hits de cache
cache_hits = Counter(
    'vectora_cache_hits_total',
    'Cache hits',
    ['type']
)

cache_misses = Counter(
    'vectora_cache_misses_total',
    'Cache misses',
    ['type']
)

# Exemplo de uso
@search_latency.labels(bucket='docs', top_k=10).time()
def search_with_metric(query: str, bucket_id: str):
    embedding = get_embedding(query)
    if embedding in cache:
        cache_hits.labels(type='embedding').inc()
    else:
        cache_misses.labels(type='embedding').inc()

    return lancedb_search(embedding)
```

## Dashboard com Grafana

### 1. Conectar Prometheus a Grafana

```bash
# Instalação Grafana
docker run -d -p 3000:3000 grafana/grafana

# Abrir http://localhost:3000
# Username: admin, Password: admin
```

### 2. Adicionar Data Source

1. Ir para "Configuration" → "Data Sources"
2. Clicar "Add data source"
3. Selecionar "Prometheus"
4. URL: `http://localhost:9090`
5. Salvar

### 3. Criar Dashboard

```text
Panel 1: Request Rate
  Query: rate(http_requests_total[5m])

Panel 2: P99 Latency
  Query: histogram_quantile(0.99, http_request_duration_seconds)

Panel 3: Error Rate
  Query: rate(http_requests_total{status=~"5.."}[5m])

Panel 4: Cache Hit Ratio
  Query: vectora_cache_hits_total / (vectora_cache_hits_total + vectora_cache_misses_total)
```

## SLOs e Alertas

### Definir SLO (Service Level Objective)

```text
Availability: 99.9% de requisições bem-sucedidas
Latency P99:  < 500ms para 99% das requisições
Error Rate:   < 0.1% de erros 5xx
```

### Alertas Prometheus

```yaml
groups:
  - name: vectora_alerts
    rules:
      # Alta latência
      - alert: HighLatency
        expr: histogram_quantile(0.99, http_request_duration_seconds) > 0.5
        for: 5m
        annotations:
          summary: "P99 latency > 500ms"

      # Taxa de erro alta
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.001
        for: 2m
        annotations:
          summary: "Error rate > 0.1%"

      # Cache hit ratio baixo
      - alert: LowCacheHitRatio
        expr: vectora_cache_hits_total / (vectora_cache_hits_total + vectora_cache_misses_total) < 0.5
        for: 10m
        annotations:
          summary: "Cache hit ratio < 50%"
```

## Troubleshooting

### Métricas não aparecem em `/metrics`

```bash
# Verificar se middleware está registrado
curl http://localhost:8000/metrics

# Se 404: adicionar à aplicação FastAPI
from prometheus_client import make_wsgi_app
from werkzeug.serving import run_simple

app.add_middleware(...)
metrics_app = make_wsgi_app()
```

### Prometheus não scrapa Vectora

```bash
# Verificar prometheus.yml
curl http://localhost:8000/metrics

# Se erro de conexão, verificar firewall
telnet localhost 8000
```

### Alto uso de memória do Prometheus

```yaml
# Limitar retenção de dados
global:
  scrape_interval: 15s
  retention_time: 15d # Manter últimos 15 dias
```

## External Linking

| Conceito              | Recurso                  | Link                                                                                                           |
| --------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------- |
| **Prometheus**        | Metrics and alerting     | [prometheus.io](https://prometheus.io/)                                                                        |
| **Grafana**           | Visualization platform   | [grafana.com](https://grafana.com/)                                                                            |
| **OpenMetrics**       | Metrics standard         | [openmetrics.io](https://openmetrics.io/)                                                                      |
| **SLO Guide**         | Service Level Objectives | [sre.google/sre-book/service-level-objectives](https://sre.google/sre-book/chapters/service-level-objectives/) |
| **Prometheus Python** | Python client library    | [github.com/prometheus/client_python](https://github.com/prometheus/client_python)                             |
