---
title: Testes de Performance
slug: performance-testing
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - testing
  - performance
  - benchmarking
  - load-testing
  - vectora
---

{{< lang-toggle >}}

**Testes de performance** medem latência, throughput e consumo de recursos. Vectora monitora: latência de search (< 500ms p99), latência de reranking (< 10ms), taxa de erros.

## Tipos de Testes de Performance

| Tipo          | Propósito                 | Carga    |
| ------------- | ------------------------- | -------- |
| **Benchmark** | Medir componente isolado  | 1        |
| **Load**      | Múltiplas requisições     | 100+     |
| **Stress**    | Encontrar ponto de quebra | 1000+    |
| **Soak**      | Comportamento com tempo   | Normal x |

## Benchmarking de Componentes

```python
# tests/performance/test_component_latency.py
import pytest
import time
import statistics
from vectora.search import SearchPipeline
from vectora.vcr import LocalReranker

@pytest.mark.slow
class TestComponentLatency:
    @pytest.fixture
    def reranker(self):
        return LocalReranker(model_name="xlm-roberta-small")

    def test_reranker_latency_p99_under_10ms(self, reranker):
        """Reranking deve estar abaixo de 10ms p99"""

        candidates = [
            {"content": f"code snippet {i}" * 10}
            for i in range(100)
        ]
        latencies = []

        # Executar 100x
        for _ in range(100):
            start = time.perf_counter()
            reranker.rerank("query", candidates, top_k=10)
            latency_ms = (time.perf_counter() - start) * 1000
            latencies.append(latency_ms)

        # Calcular percentis
        latencies.sort()
        p50 = latencies[int(len(latencies) * 0.50)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]

        print(f"\nReranker latency:")
        print(f"  p50: {p50:.2f}ms")
        print(f"  p95: {p95:.2f}ms")
        print(f"  p99: {p99:.2f}ms")

        assert p99 < 10, f"P99 latency {p99:.2f}ms exceeds 10ms SLO"

    def test_embedding_latency_with_cache(self):
        """Embedding cached deve ser < 1ms"""
        from vectora.embeddings import embed_query

        query = "test query for caching"

        # Primeira chamada (sem cache)
        start = time.perf_counter()
        embed_query(query)
        first_latency = (time.perf_counter() - start) * 1000

        # Segunda chamada (com cache)
        start = time.perf_counter()
        embed_query(query)
        cached_latency = (time.perf_counter() - start) * 1000

        assert cached_latency < 1, f"Cached embedding took {cached_latency:.2f}ms"
```

## Teste de Carga com Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, constant
import random

class VectoraUser(HttpUser):
    """Simular usuário fazendo requisições ao Vectora"""

    wait_time = constant(1)

    def on_start(self):
        """Login antes de iniciar requisições"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "load-test@vectora.dev",
            "password": "test-password",
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def search(self):
        """Busca (3x mais frequente)"""
        self.client.post("/api/v1/search", json={
            "query": random.choice([
                "jwt validation",
                "password hashing",
                "token refresh",
                "user authentication",
            ]),
            "top_k": 10,
        }, headers=self.headers)

    @task(1)
    def create_bucket(self):
        """Criar bucket (1x)"""
        self.client.post("/api/v1/buckets", json={
            "name": f"bucket-{random.randint(1, 1000)}",
        }, headers=self.headers)

# Rodar: locust -f tests/performance/locustfile.py
# Acessa http://localhost:8089
```

## Teste de Carga com pytest-benchmark

```python
# tests/performance/test_search_benchmark.py
import pytest

@pytest.mark.slow
def test_search_pipeline_benchmark(benchmark):
    """Benchmark de pipeline de search"""
    from vectora.search import SearchPipeline

    pipeline = SearchPipeline()

    def search_operation():
        return pipeline.search(
            query="jwt validation",
            top_k=10,
        )

    result = benchmark(search_operation)

    assert result is not None
    # pytest-benchmark gera relatório automaticamente

# Rodar: pytest tests/performance/test_search_benchmark.py --benchmark-only
```

## Teste de Stress

```python
# tests/performance/test_stress.py
import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

@pytest.mark.slow
@pytest.mark.asyncio
async def test_search_under_heavy_load():
    """Testar busca com 1000 requisições simultâneas"""
    from vectora.search import SearchPipeline

    pipeline = SearchPipeline()

    async def single_search():
        return await pipeline.search("test", top_k=5)

    # Criar 1000 tasks
    tasks = [single_search() for _ in range(1000)]

    # Executar e medir
    import time
    start = time.perf_counter()
    results = await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start

    # Validações
    assert len(results) == 1000
    assert all(r for r in results)  # Nenhum falhou

    throughput = 1000 / total_time
    print(f"\nThroughput: {throughput:.0f} req/s")

    # SLO: >100 req/s
    assert throughput > 100, f"Throughput {throughput} req/s below SLO of 100 req/s"
```

## Teste de Soak (Resistência)

```python
# tests/performance/test_soak.py
import pytest
import time
import psutil

@pytest.mark.slow
def test_memory_stability():
    """Verificar vazamento de memória após 10k requisições"""
    from vectora.search import SearchPipeline

    pipeline = SearchPipeline()
    process = psutil.Process()

    # Medir memória inicial
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # 10k requisições
    for i in range(10000):
        pipeline.search("test query", top_k=5)

        if (i + 1) % 1000 == 0:
            current_memory = process.memory_info().rss / 1024 / 1024
            print(f"\nAfter {i+1} requests: {current_memory:.1f} MB")

    # Medir memória final
    final_memory = process.memory_info().rss / 1024 / 1024
    memory_increase = final_memory - initial_memory

    print(f"\nMemory increase: {memory_increase:.1f} MB")

    # SLO: não crescer mais de 500MB
    assert memory_increase < 500, f"Memory grew {memory_increase:.1f} MB (target: <500 MB)"
```

## Profiling com cProfile

```python
# tests/performance/test_profiling.py
import pytest
import cProfile
import pstats
import io

@pytest.mark.slow
def test_search_profiling():
    """Identificar hotspots"""
    from vectora.search import SearchPipeline

    pipeline = SearchPipeline()

    # Profiling
    pr = cProfile.Profile()
    pr.enable()

    for _ in range(100):
        pipeline.search("test", top_k=10)

    pr.disable()

    # Gerar relatório
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(10)  # Top 10

    print(s.getvalue())
    # Salvar se quiser
    # ps.dump_stats("profile_stats.prof")
```

## Baseline e Regression

```python
# tests/performance/test_baseline.py
import pytest
import json

BASELINE = {
    "search_p99_ms": 500,
    "rerank_p99_ms": 10,
    "embedding_cached_ms": 1,
    "throughput_req_s": 100,
}

@pytest.fixture
def performance_metrics():
    """Coletar métricas"""
    from vectora.search import SearchPipeline
    import time

    pipeline = SearchPipeline()
    latencies = []

    for _ in range(100):
        start = time.perf_counter()
        pipeline.search("test", top_k=5)
        latencies.append((time.perf_counter() - start) * 1000)

    latencies.sort()
    return {
        "search_p99_ms": latencies[int(len(latencies) * 0.99)],
    }

@pytest.mark.slow
def test_no_regression(performance_metrics):
    """Comparar com baseline"""
    for metric, value in performance_metrics.items():
        baseline = BASELINE[metric]
        # Permitir 10% degradação
        assert value <= baseline * 1.1, \
            f"{metric} degraded: {value:.1f} > {baseline:.1f}"
```

## Relatório de Performance

```bash
# Gerar relatório pytest-benchmark
pytest tests/performance/ --benchmark-compare --benchmark-compare-fail=mean:10%

# Gerar perfil
python -m cProfile -o profile.prof -m pytest tests/performance/test_profiling.py
python -m pstats profile.prof
```

## External Linking

| Conceito             | Recurso             | Link                                                                                |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------- |
| **pytest-benchmark** | Benchmarking plugin | [pytest-benchmark.readthedocs.io](https://pytest-benchmark.readthedocs.io/)         |
| **Locust**           | Load testing tool   | [locust.io](https://locust.io/)                                                     |
| **cProfile**         | Python profiling    | [docs.python.org/3/library/profile](https://docs.python.org/3/library/profile.html) |
| **psutil**           | System monitoring   | [psutil.readthedocs.io](https://psutil.readthedocs.io/)                             |
| **Load Testing**     | Best practices      | [en.wikipedia.org/wiki/Load_testing](https://en.wikipedia.org/wiki/Load_testing)    |
