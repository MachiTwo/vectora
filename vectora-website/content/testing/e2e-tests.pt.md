---
title: Testes End-to-End
slug: e2e-tests
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - testing
  - e2e-tests
  - api
  - vectora
---

{{< lang-toggle >}}

**Testes end-to-end** (E2E) verificam o pipeline completo da perspectiva do usuário: fazer requisições HTTP para a API e validar as respostas. Requerem servidor rodando.

## Estrutura E2E

Testes E2E não usam mocks. Enviam requisições HTTP reais:

```text
Cliente de teste HTTP
        │
        ├─→ POST /api/v1/search
        │   └─→ Server (FastAPI real)
        │       ├─→ Verificar token JWT
        │       ├─→ Buscar em LanceDB
        │       ├─→ Reranking XLM-RoBERTa
        │       └─→ Retornar JSON
        │
        └─→ Validar resposta
```

## Setup E2E

```python
# tests/e2e/conftest.py
import pytest
import httpx
from vectora import app

BASE_URL = "http://localhost:8000"

@pytest.fixture
async def http_client():
    """Cliente HTTP para testes E2E"""
    async with httpx.AsyncClient(app=app, base_url=BASE_URL) as client:
        yield client

@pytest.fixture
async def authenticated_client(http_client, test_user):
    """Cliente HTTP com token de autenticação"""
    # Login para obter token
    response = await http_client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": "test-password",
    })
    token = response.json()["access_token"]

    # Adicionar header de autorização
    http_client.headers["Authorization"] = f"Bearer {token}"
    return http_client
```

## Testando Endpoints de Search

```python
# tests/e2e/test_api_search.py
import pytest

@pytest.mark.e2e
class TestSearchAPI:
    @pytest.mark.asyncio
    async def test_search_requires_authentication(self, http_client):
        """Requisição sem token retorna 401"""
        response = await http_client.post("/api/v1/search", json={
            "query": "jwt validation",
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_search_returns_results(self, authenticated_client):
        """Search com token retorna resultados"""
        response = await authenticated_client.post("/api/v1/search", json={
            "query": "how to validate tokens",
            "bucket_id": "docs",
            "top_k": 5,
        })

        assert response.status_code == 200
        data = response.json()

        assert "results" in data
        assert isinstance(data["results"], list)
        assert all("content" in r for r in data["results"])
        assert all("score" in r for r in data["results"])

    @pytest.mark.asyncio
    async def test_search_respects_top_k(self, authenticated_client):
        """Limiar top_k é respeitado"""
        response = await authenticated_client.post("/api/v1/search", json={
            "query": "test",
            "top_k": 3,
        })

        data = response.json()
        assert len(data["results"]) <= 3

    @pytest.mark.asyncio
    async def test_search_with_invalid_bucket(self, authenticated_client):
        """Bucket inexistente retorna 404"""
        response = await authenticated_client.post("/api/v1/search", json={
            "query": "test",
            "bucket_id": "nonexistent-bucket",
        })

        assert response.status_code == 404
```

## Testando Fluxo de Autenticação

```python
# tests/e2e/test_api_auth.py
@pytest.mark.e2e
class TestAuthenticationAPI:
    @pytest.mark.asyncio
    async def test_login_returns_tokens(self, http_client, test_user):
        """Login retorna access + refresh tokens"""
        response = await http_client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": "test-password",
        })

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_invalid_credentials_returns_401(self, http_client):
        """Credenciais inválidas retornam 401"""
        response = await http_client.post("/api/v1/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrong-password",
        })

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_updates_access(self, http_client, test_user):
        """Usar refresh token gera novo access token"""

        # Login
        login_response = await http_client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": "test-password",
        })
        refresh_token = login_response.json()["refresh_token"]

        # Usar refresh
        refresh_response = await http_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert refresh_response.status_code == 200
        assert "access_token" in refresh_response.json()
```

## Testando Streaming SSE

```python
# tests/e2e/test_api_streaming.py
@pytest.mark.e2e
class TestStreamingAPI:
    @pytest.mark.asyncio
    async def test_agent_stream_returns_events(self, authenticated_client):
        """Streaming agent retorna eventos SSE"""

        async with authenticated_client.stream(
            "POST",
            "/api/v1/agent/chat",
            json={"query": "explain jwt"},
        ) as response:
            assert response.status_code == 200

            events = []
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    events.append(json.loads(line[6:]))

            # Deve ter múltiplos eventos
            assert len(events) > 0

            # Último evento deve ser "done"
            assert events[-1].get("type") == "done"
```

## Testando Bucket Management

```python
# tests/e2e/test_api_buckets.py
@pytest.mark.e2e
class TestBucketAPI:
    @pytest.mark.asyncio
    async def test_create_bucket(self, authenticated_client):
        """Criar novo bucket via API"""
        response = await authenticated_client.post(
            "/api/v1/buckets",
            json={"name": "new-bucket", "is_public": False},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "new-bucket"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_buckets(self, authenticated_client):
        """Listar buckets do usuário"""
        response = await authenticated_client.get("/api/v1/buckets")

        assert response.status_code == 200
        buckets = response.json()["buckets"]
        assert isinstance(buckets, list)

    @pytest.mark.asyncio
    async def test_delete_bucket(self, authenticated_client, test_bucket):
        """Deletar bucket"""
        response = await authenticated_client.delete(
            f"/api/v1/buckets/{test_bucket['id']}"
        )

        assert response.status_code == 204

        # Verificar que foi deletado
        get_response = await authenticated_client.get(
            f"/api/v1/buckets/{test_bucket['id']}"
        )
        assert get_response.status_code == 404
```

## Validação de Respostas

```python
# tests/e2e/test_response_validation.py
import jsonschema

SEARCH_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "score": {"type": "number", "minimum": 0, "maximum": 1},
                    "file": {"type": "string"},
                },
                "required": ["content", "score"],
            },
        },
        "metadata": {
            "type": "object",
            "properties": {
                "total_latency_ms": {"type": "number"},
                "num_results": {"type": "integer"},
            },
        },
    },
    "required": ["results"],
}

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_search_response_schema(authenticated_client):
    """Validar que resposta segue o schema esperado"""
    response = await authenticated_client.post("/api/v1/search", json={
        "query": "test",
    })

    data = response.json()
    jsonschema.validate(data, SEARCH_RESPONSE_SCHEMA)
```

## Executar Testes E2E

```bash
# Requer servidor rodando:
# uvicorn vectora.main:app --reload

# Todos os E2E
uv run pytest tests/e2e/ -v

# Com timeout
uv run pytest tests/e2e/ -v --timeout=30

# Apenas um teste
uv run pytest tests/e2e/test_api_search.py::TestSearchAPI::test_search_returns_results -v

# Com logging de requisições
uv run pytest tests/e2e/ -v -s --log-cli-level=DEBUG
```

## External Linking

| Conceito        | Recurso            | Link                                                                                                                |
| --------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| **httpx**       | HTTP client        | [www.python-httpx.org](https://www.python-httpx.org/)                                                               |
| **API Testing** | Best practices     | [testapi.org](https://testapi.org/)                                                                                 |
| **JSON Schema** | Validation         | [json-schema.org](https://json-schema.org/)                                                                         |
| **SSE**         | Server-sent events | [html.spec.whatwg.org/multipage/server-sent-events](https://html.spec.whatwg.org/multipage/server-sent-events.html) |
| **httpx Docs**  | Testing FastAPI    | [www.python-httpx.org/advanced/#asgi](https://www.python-httpx.org/advanced/#asgi)                                  |
