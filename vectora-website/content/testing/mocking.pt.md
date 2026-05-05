---
title: Mocking e Fixtures
slug: mocking
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - testing
  - mocking
  - fixtures
  - pytest
  - vectora
---

{{< lang-toggle >}}

**Mocking** cria objetos falsificados para isolar componentes em testes unitários. **Fixtures** fornecem dados de teste reutilizáveis. Juntas, permitem testes rápidos e determinísticos.

## Quando Usar Mocks

| Situação         | Use Mock? | Reason                                      |
| ---------------- | --------- | ------------------------------------------- |
| Teste unitário   | ✅ Sim    | Isolado, rápido                             |
| Teste integração | ❌ Não    | BD real necessário                          |
| API externa      | ✅ Sim    | Independência do teste                      |
| Banco de dados   | Depende   | Mock para unitário, BD real para integração |

## Criando Mocks Básicos

```python
# tests/unit/test_with_mocks.py
from unittest.mock import Mock, patch, MagicMock
import pytest

@pytest.mark.unit
def test_search_with_mock_embedding():
    """Mock da função de embedding"""

    # Criar mock
    mock_embed = Mock(return_value=[0.1, 0.2, 0.3, ...])

    # Usar mock em código
    from vectora.search import search_simple

    with patch("vectora.embeddings.embed_query", mock_embed):
        results = search_simple("test query")

    # Validar que foi chamado
    mock_embed.assert_called_once_with("test query")

@pytest.mark.unit
def test_lancedb_with_mock():
    """Mock do LanceDB"""

    mock_db = Mock()
    mock_db.search.return_value = [
        {"content": "result 1"},
        {"content": "result 2"},
    ]

    # Código usa mock
    results = perform_search(mock_db, "query")

    assert len(results) == 2
    mock_db.search.assert_called_once()
```

## Mocks com Side Effects

```python
# tests/unit/test_side_effects.py
from unittest.mock import Mock, call

@pytest.mark.unit
def test_cache_fallback():
    """Simular comportamento de cache miss + hit"""

    mock_cache = Mock()
    # Primeira chamada: None (miss)
    # Segunda chamada: valor (hit)
    mock_cache.get.side_effect = [None, "cached_value"]

    result1 = mock_cache.get("key")
    result2 = mock_cache.get("key")

    assert result1 is None
    assert result2 == "cached_value"

@pytest.mark.unit
def test_error_handling_with_side_effect():
    """Mock que levanta exceção"""

    mock_api = Mock()
    mock_api.call.side_effect = TimeoutError("API timeout")

    with pytest.raises(TimeoutError):
        mock_api.call()
```

## Fixtures Reutilizáveis

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_embedding():
    """Embedding fake de 1024 dimensões"""
    import numpy as np
    return np.random.randn(1024).astype(np.float32)

@pytest.fixture
def mock_search_results():
    """Resultados de search mockados"""
    return [
        {
            "id": "chunk-1",
            "content": "def verify_token(...)",
            "score": 0.95,
            "file": "auth.py",
        },
        {
            "id": "chunk-2",
            "content": "def decode_jwt(...)",
            "score": 0.87,
            "file": "auth.py",
        },
    ]

@pytest.fixture
def mock_user():
    """Usuário fake para testes"""
    return {
        "id": "user-123",
        "email": "test@vectora.dev",
        "role": "developer",
        "created_at": "2026-05-04T00:00:00Z",
    }

@pytest.fixture
def mock_bucket():
    """Bucket fake para testes"""
    return {
        "id": "bucket-123",
        "name": "test-bucket",
        "owner_id": "user-123",
        "is_public": False,
        "chunk_count": 100,
    }
```

## Fixtures com Escopo

```python
# tests/conftest.py

@pytest.fixture(scope="function")
def temp_file():
    """Criado e deletado a cada teste"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test data")
        path = f.name
    yield path
    import os
    os.unlink(path)

@pytest.fixture(scope="session")
def static_config():
    """Carregado uma vez por sessão de testes"""
    return {
        "api_key": "test-key-123",
        "base_url": "http://localhost:8000",
        "timeout": 30,
    }

@pytest.fixture(scope="module")
def module_db():
    """Criado uma vez por módulo de testes"""
    db = setup_test_database()
    yield db
    cleanup_test_database(db)
```

## Parametrizing Fixtures

```python
# tests/unit/test_parametrized.py
import pytest

@pytest.fixture(params=[
    {"query": "jwt", "expected_results": True},
    {"query": "xyz", "expected_results": False},
])
def search_params(request):
    """Fixture parametrizada"""
    return request.param

@pytest.mark.unit
def test_search_with_various_queries(search_params):
    """Roda 2x com diferentes parâmetros"""
    results = search(search_params["query"])
    assert bool(results) == search_params["expected_results"]
```

## Fixture Factories

```python
# tests/conftest.py

@pytest.fixture
def user_factory():
    """Factory para criar múltiplos usuários de teste"""
    def create_user(
        email="test@vectora.dev",
        role="developer",
        **kwargs
    ):
        return {
            "id": "user-" + uuid.uuid4().hex[:8],
            "email": email,
            "role": role,
            **kwargs,
        }
    return create_user

# Usar factory
@pytest.mark.unit
def test_multiple_users(user_factory):
    admin = user_factory(role="admin")
    developer = user_factory(role="developer")
    viewer = user_factory(role="viewer")

    assert admin["role"] == "admin"
    assert developer["role"] == "developer"
```

## Testando Código Async com Mocks

```python
# tests/unit/test_async_mocks.py
from unittest.mock import AsyncMock
import pytest

@pytest.mark.asyncio
async def test_async_with_mock():
    """Mockar função async"""

    mock_api = AsyncMock()
    mock_api.search.return_value = {"results": ["item1", "item2"]}

    result = await mock_api.search("query")

    assert result["results"] == ["item1", "item2"]
    mock_api.search.assert_called_once_with("query")
```

## Validando Chamadas a Mocks

```python
# tests/unit/test_mock_assertions.py

@pytest.mark.unit
def test_mock_called_correctly():
    """Validar como mock foi chamado"""

    mock = Mock()
    mock("arg1", kwarg="value")

    # Assert básicos
    mock.assert_called()
    mock.assert_called_once()
    mock.assert_called_with("arg1", kwarg="value")

    # Assert chamadas múltiplas
    mock.reset_mock()
    mock("call1")
    mock("call2")

    assert mock.call_count == 2
    mock.assert_has_calls([
        call("call1"),
        call("call2"),
    ])
```

## Boas Práticas

### ❌ Evitar: Testes Acoplados a Mocks

```python
# Ruim - teste sabe demais sobre implementação
def test_search():
    mock_embed = Mock()
    mock_db = Mock()
    mock_rerank = Mock()

    search(mock_embed, mock_db, mock_rerank)

    # Assertar muitos detalhes
    assert mock_embed.called
    assert mock_db.called
    assert mock_rerank.called
```

### ✅ Fazer: Testar Comportamento

```python
# Bom - testa resultado, não implementação
def test_search_returns_results(mock_db):
    results = search_with_mock_db(mock_db)

    assert len(results) > 0
    assert all("score" in r for r in results)
```

## External Linking

| Conceito            | Recurso                 | Link                                                                                                                    |
| ------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **unittest.mock**   | Official Python mocking | [docs.python.org/3/library/unittest.mock](https://docs.python.org/3/library/unittest.mock.html)                         |
| **pytest Fixtures** | Fixture documentation   | [docs.pytest.org/en/stable/how-to/fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)                     |
| **pytest Marks**    | Test markers            | [docs.pytest.org/en/stable/how-to/mark](https://docs.pytest.org/en/stable/how-to/mark.html)                             |
| **Async Mocks**     | AsyncMock guide         | [docs.python.org/3/library/unittest.mock#async-mocks](https://docs.python.org/3/library/unittest.mock.html#async-mocks) |
| **Parametrize**     | pytest parametrization  | [docs.pytest.org/en/stable/how-to/parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)               |
