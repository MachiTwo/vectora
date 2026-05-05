---
title: Python SDK
slug: python-sdk
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - sdk
  - python
  - client
  - vectora
---

{{< lang-toggle >}}

O **Vectora Python SDK** (`vectora-py`) fornece um cliente full-featured com type hints, retry logic, streaming e suporte completo para todas as operações da API.

## Instalação

```bash
# Via pip
pip install vectora

# Via uv (recomendado)
uv add vectora

# Via Poetry
poetry add vectora
```

## Setup Básico

```python
from vectora import VectoraClient

client = VectoraClient(
    api_key="vec_your_api_key_here",
    base_url="https://api.vectora.dev",  # Opcional, padrão
    timeout=30,  # Segundos
)
```

## Buscas Simples

```python
# Busca simples
results = client.search(
    query="como autenticar com JWT?",
    bucket_id="docs",
    top_k=5,
)

for result in results:
    print(f"Score: {result.score}")
    print(f"Content: {result.content[:200]}...")
    print(f"File: {result.metadata.get('file')}")
```

## Buscas Avançadas com Filtros

```python
# Busca com filtros de metadados
results = client.search(
    query="token validation",
    bucket_id="docs",
    top_k=10,
    filters={
        "file_type": "python",
        "language": "en",
    },
    min_score=0.7,
)
```

## Gerenciamento de Buckets

```python
# Criar bucket
bucket = client.buckets.create(
    name="my-docs",
    is_public=False,
    description="Documentação interna",
)

# Listar buckets
buckets = client.buckets.list()
for bucket in buckets:
    print(f"ID: {bucket.id}, Name: {bucket.name}")

# Obter bucket específico
bucket = client.buckets.get("docs")

# Deletar bucket
client.buckets.delete("docs")
```

## Indexação de Documentos

```python
# Indexar documentos
documents = [
    {
        "id": "doc-1",
        "content": "def verify_token(token: str) -> bool: ...",
        "metadata": {"file": "auth.py", "line": 10},
    },
    {
        "id": "doc-2",
        "content": "def refresh_token(old_token: str) -> str: ...",
        "metadata": {"file": "auth.py", "line": 25},
    },
]

client.documents.index(
    bucket_id="docs",
    documents=documents,
)

# Deletar documento
client.documents.delete(bucket_id="docs", document_id="doc-1")

# Atualizar documento
client.documents.update(
    bucket_id="docs",
    document_id="doc-2",
    content="novo conteúdo",
)
```

## Streaming de Respostas

```python
# Streaming para buscas
for chunk in client.search_stream(
    query="autenticação",
    bucket_id="docs",
):
    print(f"Score: {chunk.score}")
    print(f"Content: {chunk.content}")
```

## Retry Logic e Resiliência

```python
from vectora import VectoraClient, RetryConfig

client = VectoraClient(
    api_key="...",
    retry_config=RetryConfig(
        max_retries=3,
        initial_delay=1.0,
        backoff_factor=2.0,
        max_delay=60.0,
    ),
)
```

## Error Handling

```python
from vectora import VectoraError, NotFoundError, UnauthorizedError

try:
    results = client.search(
        query="test",
        bucket_id="nonexistent",
    )
except NotFoundError:
    print("Bucket não encontrado")
except UnauthorizedError:
    print("API key inválida")
except VectoraError as e:
    print(f"Erro na API: {e}")
```

## Async Support

```python
import asyncio
from vectora import AsyncVectoraClient

async def search_documents():
    async with AsyncVectoraClient(api_key="...") as client:
        results = await client.search(
            query="autenticação",
            bucket_id="docs",
        )
        return results

# Rodar async
results = asyncio.run(search_documents())
```

## Batch Operations

```python
# Buscar múltiplas queries em paralelo
queries = [
    "JWT validation",
    "password hashing",
    "token refresh",
]

results = client.search_batch(
    queries=queries,
    bucket_id="docs",
    top_k=5,
)

# results[i] contém resultados para queries[i]
```

## Rate Limiting

```python
from vectora import RateLimiter

# Cliente com rate limiting customizado
client = VectoraClient(
    api_key="...",
    rate_limiter=RateLimiter(
        requests_per_second=10,
    ),
)
```

## Context Manager

```python
# Usar com context manager para cleanup automático
with VectoraClient(api_key="...") as client:
    results = client.search(query="test", bucket_id="docs")
    # Conexão fechada automaticamente
```

## Logging

```python
import logging

# Habilitar logs detalhados
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("vectora")

client = VectoraClient(api_key="...")
# Todas as requisições serão logadas
```

## Exemplos Completos

### Busca e Processamento

```python
from vectora import VectoraClient

client = VectoraClient(api_key="vec_...")

# Buscar documentos relevantes
results = client.search(
    query="como fazer autenticação?",
    bucket_id="docs",
    top_k=3,
)

# Processar resultados
for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result.score:.2%}")
    print(f"   File: {result.metadata['file']}")
    print(f"   Content: {result.content[:100]}...")
```

### Indexação em Lote

```python
from pathlib import Path

def index_python_files(directory: str, bucket_id: str):
    documents = []

    for py_file in Path(directory).glob("**/*.py"):
        with open(py_file) as f:
            content = f.read()

        documents.append({
            "id": str(py_file),
            "content": content,
            "metadata": {
                "file": str(py_file),
                "size": len(content),
            },
        })

    client.documents.index(
        bucket_id=bucket_id,
        documents=documents,
    )

index_python_files("./src", "my-codebase")
```

## External Linking

| Conceito               | Recurso               | Link                                                                                |
| ---------------------- | --------------------- | ----------------------------------------------------------------------------------- |
| **Vectora Python SDK** | GitHub Repository     | [github.com/vectora-io/vectora-py](https://github.com/vectora-io/vectora-py)        |
| **PyPI Package**       | Package Registry      | [pypi.org/project/vectora](https://pypi.org/project/vectora/)                       |
| **Async Python**       | asyncio documentation | [docs.python.org/3/library/asyncio](https://docs.python.org/3/library/asyncio.html) |
| **Type Hints**         | Python typing guide   | [docs.python.org/3/library/typing](https://docs.python.org/3/library/typing.html)   |
| **Requests Library**   | HTTP client library   | [requests.readthedocs.io](https://requests.readthedocs.io/)                         |
