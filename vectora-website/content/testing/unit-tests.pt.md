---
title: Testes Unitários
slug: unit-tests
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - testing
  - unit-tests
  - pytest
  - vectora
---

{{< lang-toggle >}}

**Testes unitários** isolam componentes e verificam o comportamento de uma unidade de código sem dependências externas. Em Vectora, testes unitários cobrem: VCR reranker, JWT tokens, RBAC, parsing de código.

## Estrutura de Testes Unitários

```text
tests/unit/
├── test_vcr.py          # Reranker XLM-RoBERTa
├── test_jwt.py          # Geração e validação de tokens
├── test_rbac.py         # Permissões e roles
├── test_chunker.py      # Divisão de código em chunks
├── test_embeddings.py   # Normalização de embeddings
└── conftest.py          # Fixtures compartilhadas
```

## Setup Básico

```python
# tests/unit/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_code():
    """Código de exemplo para testes"""
    return '''
def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid token")
'''

@pytest.fixture
def mock_embedding():
    """Mock de embedding vetorial"""
    import numpy as np
    return np.random.randn(1024).astype(np.float32)
```

## Testando VCR (Reranker)

```python
# tests/unit/test_vcr.py
import pytest
from vectora.vcr import LocalReranker
import numpy as np

@pytest.mark.unit
class TestLocalReranker:
    @pytest.fixture
    def reranker(self):
        return LocalReranker(model_name="xlm-roberta-small")

    def test_rerank_returns_top_k(self, reranker):
        """Verificar que retorna exatamente top_k resultados"""
        candidates = [
            {"content": "def validate_token(token: str) -> dict: ..."},
            {"content": "def create_user(email: str) -> User: ..."},
            {"content": "def send_email(to: str, subject: str): ..."},
            {"content": "def reset_password(email: str): ..."},
            {"content": "def login(email: str, password: str): ..."},
        ]

        query = "token validation"
        results = reranker.rerank(query, candidates, top_k=2)

        assert len(results) == 2
        assert all("rerank_score" in r for r in results)

    def test_rerank_scores_are_sorted(self, reranker):
        """Scores devem estar em ordem decrescente"""
        candidates = [
            {"content": "JWT validation logic"},
            {"content": "Database connection pool"},
            {"content": "Token verification algorithm"},
        ]

        results = reranker.rerank("jwt token", candidates, top_k=3)

        scores = [r["rerank_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_rerank_with_zero_candidates(self, reranker):
        """Tratar lista vazia graciosamente"""
        results = reranker.rerank("query", [], top_k=10)
        assert results == []
```

## Testando Autenticação (JWT)

```python
# tests/unit/test_jwt.py
import pytest
import time
from vectora.auth import create_access_token, decode_token, TokenExpiredError

@pytest.mark.unit
class TestJWTTokens:
    def test_create_access_token_includes_required_fields(self):
        """Token deve incluir sub, role, jti, type"""
        user_id = "user-123"
        role = "developer"

        token = create_access_token(user_id, role, expires_in=3600)

        assert isinstance(token, str)
        assert token.count(".") == 2  # JWT format: header.payload.signature

    def test_decode_token_returns_valid_payload(self):
        """Payload decodificado contém campos corretos"""
        user_id = "user-456"
        role = "admin"

        token = create_access_token(user_id, role)
        payload = decode_token(token)

        assert payload["sub"] == user_id
        assert payload["role"] == role
        assert payload["type"] == "access"
        assert "jti" in payload
        assert "iat" in payload
        assert "exp" in payload

    def test_decode_expired_token_raises_error(self):
        """Token expirado levanta TokenExpiredError"""
        token = create_access_token("user-789", "developer", expires_in=-1)

        with pytest.raises(TokenExpiredError):
            decode_token(token)

    def test_token_with_different_secret_fails(self):
        """Token assinado com chave diferente não valida"""
        from vectora.auth import decode_token, InvalidTokenError

        token = create_access_token("user-123", "developer")

        # Modificar o token (simular assinatura diferente)
        parts = token.split(".")
        modified_token = ".".join([parts[0], parts[1], "invalid_signature"])

        with pytest.raises(InvalidTokenError):
            decode_token(modified_token)
```

## Testando RBAC (Permissões)

```python
# tests/unit/test_rbac.py
import pytest
from vectora.auth import check_permission, Permission

@pytest.mark.unit
class TestRBAC:
    def test_admin_has_all_permissions(self):
        """Admin tem todas as permissões"""
        role = "admin"
        permissions = [
            Permission.READ_BUCKET,
            Permission.WRITE_BUCKET,
            Permission.DELETE_BUCKET,
            Permission.MANAGE_USERS,
            Permission.VIEW_LOGS,
        ]

        for perm in permissions:
            assert check_permission(role, perm)

    def test_developer_can_read_but_not_delete(self):
        """Developer pode ler, mas não pode deletar buckets"""
        role = "developer"

        assert check_permission(role, Permission.READ_BUCKET)
        assert check_permission(role, Permission.WRITE_BUCKET)
        assert not check_permission(role, Permission.DELETE_BUCKET)

    def test_viewer_can_only_read(self):
        """Viewer pode apenas ler, sem escrever"""
        role = "viewer"

        assert check_permission(role, Permission.READ_BUCKET)
        assert not check_permission(role, Permission.WRITE_BUCKET)
        assert not check_permission(role, Permission.DELETE_BUCKET)

    def test_invalid_role_has_no_permissions(self):
        """Role inválida não tem permissões"""
        role = "invalid_role"

        assert not check_permission(role, Permission.READ_BUCKET)
```

## Testando Chunking de Código

```python
# tests/unit/test_chunker.py
import pytest
from vectora.chunking import CodeChunker

@pytest.mark.unit
class TestCodeChunker:
    @pytest.fixture
    def chunker(self):
        return CodeChunker(max_chunk_size=500, overlap=50)

    def test_chunk_python_function(self, chunker, sample_code):
        """Dividir código Python em chunks lógicos"""
        chunks = chunker.chunk_python(sample_code)

        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)

    def test_chunks_respect_max_size(self, chunker, sample_code):
        """Chunks não excedem tamanho máximo"""
        chunks = chunker.chunk_python(sample_code)

        for chunk in chunks:
            assert len(chunk) <= 500

    def test_chunks_preserve_structure(self, chunker, sample_code):
        """Chunks mantêm código válido"""
        chunks = chunker.chunk_python(sample_code)

        # Concatenar chunks deve gerar código similar
        reconstructed = "\n".join(chunks)
        assert "def verify_token" in reconstructed
        assert "jwt.decode" in reconstructed

    def test_empty_code_returns_empty_list(self, chunker):
        """Código vazio retorna lista vazia"""
        chunks = chunker.chunk_python("")
        assert chunks == []
```

## Fixtures Reutilizáveis

```python
# tests/unit/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_redis():
    """Mock do Redis client"""
    mock = Mock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    return mock

@pytest.fixture
def mock_pg_conn():
    """Mock da conexão PostgreSQL"""
    mock = Mock()
    mock.query.return_value = [
        {"id": 1, "email": "user@vectora.dev", "role": "developer"}
    ]
    return mock

@pytest.fixture
def sample_bucket():
    """Bucket de exemplo para testes"""
    return {
        "id": "bucket-123",
        "name": "test-bucket",
        "owner_id": "user-456",
        "is_public": False,
        "created_at": "2026-05-04T12:00:00Z"
    }
```

## Executar Testes Unitários

```bash
# Todos os testes unitários
uv run pytest tests/unit/ -v

# Um arquivo específico
uv run pytest tests/unit/test_jwt.py -v

# Uma classe específica
uv run pytest tests/unit/test_jwt.py::TestJWTTokens -v

# Um teste específico
uv run pytest tests/unit/test_jwt.py::TestJWTTokens::test_create_access_token_includes_required_fields -v

# Com cobertura
uv run pytest tests/unit/ --cov=vectora --cov-report=term-missing

# Stop on first failure
uv run pytest tests/unit/ -x

# Verbose output
uv run pytest tests/unit/ -vv
```

## Boas Práticas

### Nomes de Testes Descritivos

```python
# ❌ Ruim
def test_token():
    ...

# ✅ Bom
def test_create_access_token_includes_all_required_fields():
    ...
```

### Arrange-Act-Assert

```python
# ✅ Padrão AAA
def test_rerank_returns_sorted_results(self, reranker):
    # Arrange
    candidates = [{"content": "..."}, {"content": "..."}]
    query = "test"

    # Act
    results = reranker.rerank(query, candidates)

    # Assert
    assert len(results) > 0
```

### Evitar Dependências Externas

```python
# ❌ Evitar - testes lentos, não isolados
def test_query_database_directly():
    conn = psycopg2.connect(...)
    result = conn.execute("SELECT ...")

# ✅ Usar mocks
@pytest.fixture
def mock_db():
    return Mock()

def test_with_mock_db(mock_db):
    mock_db.query.return_value = [{"id": 1}]
```

## External Linking

| Conceito         | Recurso                     | Link                                                                                                |
| ---------------- | --------------------------- | --------------------------------------------------------------------------------------------------- |
| **pytest**       | Testing framework           | [docs.pytest.org](https://docs.pytest.org/)                                                         |
| **pytest Guide** | Official documentation      | [docs.pytest.org/en/stable](https://docs.pytest.org/en/stable/)                                     |
| **Fixtures**     | pytest fixtures guide       | [docs.pytest.org/en/stable/how-to/fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) |
| **Mock Objects** | unittest.mock documentation | [docs.python.org/3/library/unittest.mock](https://docs.python.org/3/library/unittest.mock.html)     |
| **Coverage**     | Code coverage reporting     | [coverage.readthedocs.io](https://coverage.readthedocs.io/)                                         |
