---
title: Testes de Integração
slug: integration-tests
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - testing
  - integration-tests
  - database
  - vectora
---

{{< lang-toggle >}}

**Testes de integração** verificam o comportamento quando múltiplos componentes trabalham juntos contra infraestrutura real: PostgreSQL, Redis, LanceDB. Não usam mocks de banco de dados.

## Filosofia de Testes de Integração

```text
Unitário (componente isolado):
  search() com mock de BD

Integração (todos os componentes reais):
  search() com PostgreSQL + Redis + LanceDB reais

E2E (pipeline completo via HTTP):
  POST /api/v1/search com servidor rodando
```

## Setup de Integração

```python
# tests/integration/conftest.py
import pytest
import asyncpg
import redis
import lancedb
from vectora import app

@pytest.fixture(scope="session")
async def pg_pool():
    """Connection pool PostgreSQL para testes"""
    pool = await asyncpg.create_pool(
        host="localhost",
        database="vectora_test",
        user="vectora",
        password="test-password",
        min_size=5,
        max_size=20,
    )
    yield pool
    await pool.close()

@pytest.fixture(scope="session")
def redis_client():
    """Redis client para testes (DB separado)"""
    r = redis.Redis(host="localhost", port=6379, db=15)
    yield r
    r.flushdb()

@pytest.fixture(scope="session")
def lancedb_client(tmp_path_factory):
    """LanceDB local para testes"""
    db_path = tmp_path_factory.mktemp("lancedb")
    db = lancedb.connect(str(db_path))
    yield db

@pytest.fixture
async def test_user(pg_pool):
    """Criar usuário de teste no banco real"""
    async with pg_pool.acquire() as conn:
        user = await conn.fetchrow('''
            INSERT INTO users (email, password_hash, role)
            VALUES ($1, $2, $3)
            RETURNING id, email, role
        ''', "test@vectora.dev", "hashed_password", "developer")
    yield user

    async with pg_pool.acquire() as conn:
        await conn.execute("DELETE FROM users WHERE id = $1", user["id"])

@pytest.fixture
async def test_bucket(pg_pool, test_user):
    """Criar bucket de teste no banco real"""
    async with pg_pool.acquire() as conn:
        bucket = await conn.fetchrow('''
            INSERT INTO buckets (name, owner_id, is_public)
            VALUES ($1, $2, $3)
            RETURNING id, name, owner_id
        ''', "test-bucket", test_user["id"], False)
    yield bucket

    async with pg_pool.acquire() as conn:
        await conn.execute("DELETE FROM buckets WHERE id = $1", bucket["id"])
```

## Testando Pipeline de Search

```python
# tests/integration/test_search.py
import pytest
from vectora.search import SearchPipeline
from vectora.embeddings import embed_query
from vectora.reranking import rerank_results

@pytest.mark.integration
class TestSearchPipeline:
    @pytest.mark.asyncio
    async def test_search_returns_results(self, test_bucket, redis_client):
        """Search completo: embedding -> HNSW -> rerank"""

        # Setup: indexar alguns chunks
        chunks = [
            {"content": "def verify_token(token: str) -> dict: ..."},
            {"content": "def refresh_token(old_token: str) -> str: ..."},
            {"content": "def create_user(email: str) -> User: ..."},
        ]

        for i, chunk in enumerate(chunks):
            embedding = await embed_query(chunk["content"])
            await index_chunk(chunk, embedding, test_bucket["id"])

        # Act: executar search
        pipeline = SearchPipeline(redis_client=redis_client)
        results = await pipeline.search(
            query="token validation",
            bucket_id=test_bucket["id"],
            top_k=2,
        )

        # Assert
        assert len(results) > 0
        assert all("content" in r for r in results)
        assert all("rerank_score" in r for r in results)
        assert all("latency_ms" in r for r in results)

    @pytest.mark.asyncio
    async def test_embedding_cache_works(self, redis_client):
        """Cache de embeddings funciona entre chamadas"""

        query = "test cache"

        # Primeira chamada - miss
        result1 = await embed_query(query)
        assert result1 is not None

        # Verificar que foi armazenado em cache
        cache_key = f"embed:{hashlib.sha256(query.encode()).hexdigest()}"
        assert redis_client.exists(cache_key)

        # Segunda chamada - hit
        result2 = await embed_query(query)

        # Resultados devem ser idênticos (mesma fonte de cache)
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_search_respects_bucket_permissions(
        self, test_bucket, test_user, pg_pool
    ):
        """Usuário só vê buckets que tem acesso"""

        # Criar outro usuário
        async with pg_pool.acquire() as conn:
            other_user = await conn.fetchrow('''
                INSERT INTO users (email, password_hash, role)
                VALUES ($1, $2, $3)
                RETURNING id
            ''', "other@vectora.dev", "hashed", "developer")

        # Bucket privado do primeiro usuário
        # Outro usuário não pode acessar
        pipeline = SearchPipeline()

        with pytest.raises(PermissionError):
            await pipeline.search(
                query="test",
                bucket_id=test_bucket["id"],
                user_id=other_user["id"],
            )
```

## Testando Autenticação com BD Real

```python
# tests/integration/test_auth.py
import pytest
from vectora.auth import (
    create_access_token,
    create_refresh_token,
    verify_and_refresh_token,
)

@pytest.mark.integration
class TestAuthenticationFlow:
    @pytest.mark.asyncio
    async def test_login_creates_tokens(self, test_user, pg_pool):
        """Login retorna access + refresh tokens"""

        from vectora.auth import authenticate_user

        # Act
        tokens = await authenticate_user(
            email=test_user["email"],
            password="test-password",
            pg_pool=pg_pool,
        )

        # Assert
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_token_flow(self, test_user):
        """Refresh token gera novo access token"""

        access_token = create_access_token(test_user["id"], test_user["role"])
        refresh_token = create_refresh_token(test_user["id"])

        # Esperar um pouco para garantir novo token
        import time
        time.sleep(0.1)

        # Act: usar refresh token
        new_access = await verify_and_refresh_token(
            refresh_token=refresh_token,
            user_id=test_user["id"],
        )

        # Assert
        assert new_access is not None
        assert new_access != access_token  # Token novo, não o mesmo

    @pytest.mark.asyncio
    async def test_token_revocation(self, test_user, pg_pool):
        """Revogar token invalida ele"""

        token = create_access_token(test_user["id"], test_user["role"])

        # Revogar
        from vectora.auth import revoke_token
        await revoke_token(token, pg_pool)

        # Tentar usar deveria falhar
        from vectora.auth import verify_token, TokenRevokedError
        with pytest.raises(TokenRevokedError):
            verify_token(token)
```

## Testando Fluxo de Índexação

```python
# tests/integration/test_indexing.py
import pytest
from vectora.indexing import Indexer
from vectora.storage import LanceDB

@pytest.mark.integration
class TestIndexing:
    @pytest.mark.asyncio
    async def test_index_creates_vectors(self, test_bucket, lancedb_client):
        """Indexar código cria embeddings em LanceDB"""

        indexer = Indexer(lancedb=lancedb_client)

        chunks = [
            {"id": 1, "content": "def func1(): ..."},
            {"id": 2, "content": "def func2(): ..."},
            {"id": 3, "content": "def func3(): ..."},
        ]

        # Act
        await indexer.index_chunks(
            bucket_id=test_bucket["id"],
            chunks=chunks,
        )

        # Assert: verificar que foram indexados
        count = await lancedb_client.count_vectors(
            bucket_id=test_bucket["id"]
        )
        assert count == 3

    @pytest.mark.asyncio
    async def test_index_update_replaces_old_vectors(
        self, test_bucket, lancedb_client
    ):
        """Indexar novamente substitui vetores antigos"""

        indexer = Indexer(lancedb=lancedb_client)

        # Primeira indexação
        chunks_v1 = [{"id": 1, "content": "version 1"}]
        await indexer.index_chunks(test_bucket["id"], chunks_v1)

        # Segunda indexação
        chunks_v2 = [
            {"id": 1, "content": "version 2"},
            {"id": 2, "content": "new chunk"},
        ]
        await indexer.index_chunks(test_bucket["id"], chunks_v2)

        # Assert: 2 chunks (novo + atualizado)
        count = await lancedb_client.count_vectors(test_bucket["id"])
        assert count == 2
```

## Cleanup e Isolamento

```python
# tests/integration/conftest.py

@pytest.fixture(autouse=True)
async def cleanup_after_test(pg_pool, redis_client):
    """Limpar banco de dados após cada teste"""
    yield

    # Cleanup PostgreSQL
    async with pg_pool.acquire() as conn:
        await conn.execute("DELETE FROM embeddings")
        await conn.execute("DELETE FROM chunks")
        await conn.execute("DELETE FROM buckets")
        await conn.execute("DELETE FROM users")

    # Cleanup Redis
    redis_client.flushdb()
```

## Executar Testes de Integração

```bash
# Todos os testes de integração
uv run pytest tests/integration/ -v

# Requer PostgreSQL e Redis rodando
# Criar BD de testes:
# createdb vectora_test

# Com output detalhado de erros
uv run pytest tests/integration/ -v --tb=long

# Apenas um arquivo
uv run pytest tests/integration/test_search.py -v

# Com cobertura
uv run pytest tests/integration/ --cov=vectora --cov-report=html
```

## Diferenças: Unitário vs Integração

| Aspecto         | Unitário      | Integração        |
| --------------- | ------------- | ----------------- |
| **Banco dados** | Mock          | Real (PostgreSQL) |
| **Cache**       | Mock          | Real (Redis)      |
| **Vetores**     | Mock          | Real (LanceDB)    |
| **Velocidade**  | Milissegundos | Segundos          |
| **Isolation**   | Independentes | Requerem cleanup  |
| **Frequência**  | Sempre (CI)   | Less (noites)     |

## External Linking

| Conceito              | Recurso            | Link                                                                                                |
| --------------------- | ------------------ | --------------------------------------------------------------------------------------------------- |
| **pytest-asyncio**    | Async test support | [pytest-asyncio.readthedocs.io](https://pytest-asyncio.readthedocs.io/)                             |
| **asyncpg**           | PostgreSQL driver  | [magicstack.github.io/asyncpg](https://magicstack.github.io/asyncpg/)                               |
| **Redis Python**      | Redis client       | [redis.io/docs/clients/python](https://redis.io/docs/clients/python/)                               |
| **Database Fixtures** | Testing patterns   | [docs.pytest.org/en/stable/how-to/fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) |
| **Transaction Tests** | Best practices     | [en.wikipedia.org/wiki/Integration_testing](https://en.wikipedia.org/wiki/Integration_testing)      |
