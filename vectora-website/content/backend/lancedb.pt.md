---
title: "LanceDB: Banco Vetorial Local do Vectora"
slug: lancedb
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - ai
  - backend
  - embeddings
  - hnsw
  - lancedb
  - rag
  - storage
  - vector-database
  - vector-search
  - vectora
---

{{< lang-toggle >}}

{{< section-toggle >}}

LanceDB é o banco vetorial local do Vectora. Armazena embeddings 1024D dos chunks de código com índice HNSW para busca por similaridade. Roda completamente em disco — sem servidor externo, sem dados enviados para a nuvem.

## Setup e Conexão

```python
import lancedb

db = lancedb.connect("./data/lancedb")
```

A conexão aponta para um diretório local. LanceDB cria a estrutura de arquivos automaticamente.

## Criação de Tabela

### Tabela de chunks de código

```python
import pyarrow as pa

schema = pa.schema([
    pa.field("id", pa.string()),
    pa.field("file", pa.string()),
    pa.field("language", pa.string()),
    pa.field("start_line", pa.int32()),
    pa.field("end_line", pa.int32()),
    pa.field("content", pa.string()),
    pa.field("embedding", pa.list_(pa.float32(), 1024)),
])

table = db.create_table(
    "code_chunks",
    schema=schema,
    mode="overwrite",
)
```

### Criação do índice HNSW

```python
table.create_index(
    metric="cosine",
    num_partitions=256,
    num_sub_vectors=96,
)
```

`num_partitions=256` e `num_sub_vectors=96` são parâmetros do índice IVF-PQ interno. Para codebases pequenos (< 100K chunks), os defaults são adequados.

## Indexação de Código

### Chunking e inserção em batch

```python
import voyageai

voyage = voyageai.Client(api_key="...")
BATCH_SIZE = 128

def index_chunks(chunks: list[dict]) -> None:
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        embeddings = voyage.embed(
            [c["content"] for c in batch],
            model="voyage-4",
        ).embeddings

        records = [
            {
                "id": c["id"],
                "file": c["file"],
                "language": c["language"],
                "start_line": c["start_line"],
                "end_line": c["end_line"],
                "content": c["content"],
                "embedding": emb,
            }
            for c, emb in zip(batch, embeddings)
        ]

        table.add(records)
```

## Busca Semântica

### Busca básica

```python
def search(query_embedding: list[float], top_k: int = 100) -> list[dict]:
    results = (
        table.search(query_embedding)
        .limit(top_k)
        .metric("cosine")
        .to_pandas()
    )
    return results.to_dict("records")
```

A coluna `_distance` retornada é a distância cosine: 0.0 = idêntico, 1.0 = completamente diferente.

### Busca com filtro por namespace

```python
def search_in_namespace(
    query_embedding: list[float],
    namespace: str,
    top_k: int = 50,
) -> list[dict]:
    results = (
        table.search(query_embedding)
        .where(f"file LIKE '{namespace}%'")
        .limit(top_k)
        .metric("cosine")
        .to_pandas()
    )
    return results.to_dict("records")
```

### Busca por linguagem

```python
def search_by_language(
    query_embedding: list[float],
    language: str,
    top_k: int = 50,
) -> list[dict]:
    results = (
        table.search(query_embedding)
        .where(f"language = '{language}'")
        .limit(top_k)
        .metric("cosine")
        .to_pandas()
    )
    return results.to_dict("records")
```

## Gerenciamento de Índices

### Listar tabelas

```python
tables = db.table_names()
# ["code_chunks", "doc_chunks"]
```

### Atualizar tabela (re-index)

```python
# Apaga e recria a tabela com dados atualizados
table = db.create_table(
    "code_chunks",
    schema=schema,
    mode="overwrite",
)
index_chunks(all_chunks)
```

### Deletar registros por arquivo

```python
table.delete(f"file = 'src/auth/old_module.py'")
```

## Performance

| Operação               | Latência (100K chunks) | Latência (1M chunks) |
| ---------------------- | ---------------------- | -------------------- |
| **Busca HNSW top-100** | < 10ms                 | < 50ms               |
| **Inserção batch 128** | ~500ms                 | ~500ms               |
| **Re-index completo**  | ~30s                   | ~5min                |

LanceDB usa formato columnar Apache Lance internamente, otimizado para scan vetorial em disco.

## Estrutura de Arquivos

```text
data/lancedb/
  code_chunks.lance/
    _latest.manifest
    data/
      0.lance
      1.lance
    _indices/
      hnsw_cosine/
```

O diretório pode ser incluído em backup ou `.gitignore` dependendo da política de dados.

## External Linking

| Conceito         | Recurso                                       | Link                                                                    |
| ---------------- | --------------------------------------------- | ----------------------------------------------------------------------- |
| **LanceDB**      | Vector database local documentation           | [lancedb.com/docs](https://lancedb.com/docs)                            |
| **Apache Lance** | Columnar format for ML workloads              | [lancedb.com/blog/lance-format](https://lancedb.com/blog/lance-format/) |
| **HNSW**         | Hierarchical Navigable Small World            | [arxiv.org/abs/1603.09320](https://arxiv.org/abs/1603.09320)            |
| **IVF-PQ**       | Inverted File Index with Product Quantization | [arxiv.org/abs/1702.08734](https://arxiv.org/abs/1702.08734)            |
| **PyArrow**      | Apache Arrow Python bindings                  | [arrow.apache.org/docs/python](https://arrow.apache.org/docs/python/)   |
