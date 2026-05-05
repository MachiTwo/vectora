---
title: "LanceDB: Busca Vetorial Local"
slug: lancedb-vectors
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - hnsw
  - lancedb
  - semantic-search
  - similarity
  - storage
  - vector-database
  - vectora
---

{{< lang-toggle >}}

LanceDB é um banco de dados vetorial **local e serverless** que armazena índices HNSW (Hierarchical Navigable Small World) para busca semântica rápida (<50ms p99). Todos os embeddings do VoyageAI são indexados em LanceDB, não em um serviço remoto.

## Por que LanceDB no MVP

- **100% local** — sem latência de rede, sem dependência de serviço externo
- **Serverless** — arquivo `.lance` (formato comprimido)
- **HNSW nativo** — algoritmo de alta performance para busca k-NN
- **Integração LangChain** — suportado nativamente via `LanceDB` vector store

## Estrutura de Dados

Cada bucket (namespace) tem seu próprio índice `.lance`:

```text
vectora-data/
├── buckets/
│  ├── bucket-abc-123.lance/
│  │  ├── _metadata
│  │  ├── data/
│  │  └── indices/
│  ├── bucket-def-456.lance/
│  └── ...
```

Esquema de cada vetor armazenado:

```python
{
    "id": "chunk-uuid",
    "file": "src/utils/auth.py",
    "start_line": 42,
    "end_line": 67,
    "content": "def verify_token(token: str) -> dict: ...",
    "embedding": [0.123, -0.456, 0.789, ...],  # 1024D do voyage-3-large
    "bucket_id": "bucket-abc-123",
    "language": "python",
    "metadata": {
        "class": "AuthService",
        "imports": ["jwt", "datetime"]
    }
}
```

## Indexação com HNSW

O algoritmo HNSW cria uma estrutura hierárquica de vizinhos navegáveis para k-NN rápido:

```python
import lancedb

db = lancedb.connect("./vectora-data")
table = db.create_table(
    "bucket-abc-123",
    data=[
        {"id": "chunk-1", "content": "...", "embedding": [...]},
        {"id": "chunk-2", "content": "...", "embedding": [...]},
    ],
    mode="overwrite"  # ou "append" para adicionar chunks
)

# Criar índice HNSW explicitamente
table.create_index(
    "embedding",
    index_type="hnsw",
    metric="cosine",  # cosine, l2, ou dot
    num_partitions=256,
    accelerator="cpu"
)
```

Parâmetros HNSW:

| Parâmetro        | Padrão   | Descrição                               |
| ---------------- | -------- | --------------------------------------- |
| `metric`         | `cosine` | Distância: cosine, l2, dot              |
| `num_partitions` | 256      | Partições IVF para aceleração           |
| `accelerator`    | cpu      | Acelerador: cpu ou cuda (se disponível) |

## Busca Semântica

Buscar por similarity:

```python
# Query vetor (1024D)
query_embedding = voyage.embed(
    ["how to verify tokens"],
    model="voyage-3-large",
    input_type="query"
)[0]

# Buscar top-100 mais similares
results = table.search(query_embedding).limit(100).to_list()
# Retorna: [
#   {"id": "chunk-1", "content": "...", "_distance": 0.05},
#   {"id": "chunk-2", "content": "...", "_distance": 0.08},
#   ...
# ]
```

Score de distância (metric=cosine):

- **0** = idêntico
- **1** = ortogonal
- **2** = oposto

Usar top-100 e depois reranquear com XLM-RoBERTa para top-10.

## Configuração

Via ambiente:

```bash
export LANCEDB_PATH=./vectora-data
export LANCEDB_METRIC=cosine
```

Via config CLI:

```bash
vectora config set lancedb_path ./vectora-data
vectora config set lancedb_metric cosine
```

Criar banco de dados vazio:

```bash
vectora init
# Cria ./vectora-data com estrutura pronta
```

## Indexação de Codebase

Ao indexar um novo bucket:

```bash
vectora index add ./my-repo --bucket "my-repo"
# Lê arquivos Python/TS/Go/etc
# Cria chunks via LST (Language Server Tree)
# Gera embeddings VoyageAI (em batch de 128)
# Armazena em LanceDB
```

Processamento em batch (eficiente):

```python
BATCH_SIZE = 128  # Limite da API VoyageAI

chunks = load_chunks("my-repo")
for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i : i + BATCH_SIZE]
    embeddings = voyage.embed(
        [c["content"] for c in batch],
        model="voyage-3-large",
        input_type="document"
    )

    rows = [
        {**chunk, "embedding": emb}
        for chunk, emb in zip(batch, embeddings.embeddings)
    ]

    table.add(rows)  # Append ao LanceDB
```

## Manutenção

Verificar integridade do índice:

```bash
vectora index verify --bucket "my-repo"
# Validates HNSW structure, counts vectors, etc
```

Reindexar (se necessário):

```bash
vectora index rebuild --bucket "my-repo"
# Deleta índice antigo, reconstrói do zero
```

Deletar bucket (cuidado):

```bash
vectora bucket delete "my-repo"
# Remove ./vectora-data/buckets/my-repo.lance
```

## Performance

Latência esperada no Vectora:

```text
Query vetorial (HNSW): < 50ms p99
  ├─ Embedding query (Redis): < 1ms (cache) ou ~200ms (API)
  ├─ LanceDB search (top-100): < 10ms
  ├─ XLM-RoBERTa reranking (top-10): < 10ms
  └─ Context retrieval (PostgreSQL): < 5ms

Total (cache hit): ~ 70-100ms antes do LLM
Total (cache miss): ~ 250-350ms antes do LLM
```

Otimizações:

- Use Redis cache para embeddings (hit rate 80%+)
- Limite `num_partitions` se memória for limitada
- Considere `metric="dot"` ao invés de `cosine` para speed tradeoff

## Troubleshooting

**LanceDB não conecta:**

```bash
ls -la ./vectora-data/
# Verificar se diretório existe e tem permissões
```

**Índice corrompido:**

```bash
vectora index verify --bucket "my-repo"
# Se falhar, rebuild
vectora index rebuild --bucket "my-repo"
```

**Busca lenta (<100ms):**

```bash
vectora health
# Verificar se HNSW foi construído corretamente
```

**Espaço em disco alto:**

```bash
du -sh ./vectora-data/
# Cada 1M vetores ~= 4GB em LanceDB
```

## Exportar e Importar

Exportar índice para arquivo:

```bash
vectora export --bucket "my-repo" --format parquet > my-repo.parquet
```

Importar de volta:

```bash
vectora import ./my-repo.parquet --bucket "my-repo-restored"
```

## External Linking

| Conceito                | Recurso                            | Link                                                                                       |
| ----------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------ |
| **LanceDB Docs**        | Vector database documentation      | [lancedb.com/docs](https://lancedb.com/docs)                                               |
| **HNSW Paper**          | Hierarchical Navigable Small World | [arxiv.org/abs/1802.02413](https://arxiv.org/abs/1802.02413)                               |
| **LanceDB Python**      | Python API reference               | [lancedb.com/docs/integrations/python](https://lancedb.com/docs/integrations/python)       |
| **Vector Similarity**   | Understanding similarity metrics   | [en.wikipedia.org/wiki/Cosine_similarity](https://en.wikipedia.org/wiki/Cosine_similarity) |
| **VoyageAI Embeddings** | voyage-3-large model info          | [docs.voyageai.com/docs/embeddings](https://docs.voyageai.com/docs/embeddings)             |
