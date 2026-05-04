---
title: "RAG Pipeline: Orquestração Completa com LangChain"
slug: rag-pipeline-orchestration
date: "2026-05-03T15:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - rag
  - langchain
  - lancedb
  - voyageai
  - xlm-roberta
  - embeddings
  - reranker
  - pipeline
  - orchestration
  - vectora
  - deep-agents
---

{{< lang-toggle >}}

{{< section-toggle >}}

O pipeline RAG do Vectora é orquestrado por LangChain e cobre o ciclo completo: Indexação (chunking + embeddings + LanceDB) e Recuperação (busca + reranking + compactação). Este documento descreve cada etapa, com código e configuração.

## Ciclo Completo do RAG

```text
INDEXAÇÃO (offline)
  1. Chunking (arquivos de código)
  2. Embeddings (VoyageAI 1024D)
  3. Persistência (LanceDB)

RECUPERAÇÃO (online, por query)
  4. Embed da Query (VoyageAI, cached Redis)
  5. Vector Search (LanceDB HNSW, top-100)
  6. Reranking (XLM-RoBERTa local, top-10)
  7. Compactação (head/tail, reduz contexto)
  8. VCR Validation (score de qualidade)
  9. Resposta (LangChain chain com contexto)
```

## Fase 1: Indexação

### Chunking de Código

Vectora divide arquivos em chunks semânticos, respeitando funções e classes:

```python
from vectora.indexing.chunker import CodeChunker

chunker = CodeChunker(
    chunk_size=512,        # tokens por chunk
    chunk_overlap=64,      # tokens de sobreposição
    split_by="function",   # dividir por função/método
)

chunks = chunker.chunk_file("src/auth/jwt.py")
# Output: [
#   {"file": "src/auth/jwt.py", "lines": "1-30", "content": "def validate_token..."},
#   {"file": "src/auth/jwt.py", "lines": "31-60", "content": "def create_token..."},
# ]
```

### Geração de Embeddings (VoyageAI)

```python
import voyageai
import redis

r = redis.Redis()
voyage = voyageai.Client()

def embed_with_cache(texts: list[str]) -> list[list[float]]:
    results = []
    uncached = []
    uncached_indices = []

    for i, text in enumerate(texts):
        cache_key = f"embed:{hash(text)}"
        cached = r.get(cache_key)
        if cached:
            results.append(json.loads(cached))
        else:
            uncached.append(text)
            uncached_indices.append(i)
            results.append(None)

    if uncached:
        embeddings = voyage.embed(uncached, model="voyage-3-large").embeddings
        for i, embedding in zip(uncached_indices, embeddings):
            cache_key = f"embed:{hash(uncached[i - len(uncached_indices)])}"
            r.setex(cache_key, 86400, json.dumps(embedding))
            results[i] = embedding

    return results
```

### Persistência no LanceDB

```python
import lancedb

db = lancedb.connect("./data/lancedb")
table = db.create_table(
    "code_chunks",
    schema={
        "id": "string",
        "file": "string",
        "lines": "string",
        "content": "string",
        "embedding": "vector[1024]",
        "language": "string",
    },
    mode="overwrite",
)

# Inserir chunks com embeddings
records = []
for chunk in chunks:
    embedding = embed_with_cache([chunk["content"]])[0]
    records.append({
        "id": f"{chunk['file']}:{chunk['lines']}",
        "file": chunk["file"],
        "lines": chunk["lines"],
        "content": chunk["content"],
        "embedding": embedding,
        "language": detect_language(chunk["file"]),
    })

table.add(records)
```

## Fase 2: Recuperação

### LangChain Retriever com LanceDB

```python
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document

class VectoraRetriever(BaseRetriever):

    def __init__(self, table, voyageai_client, reranker, top_k=10):
        self.table = table
        self.voyageai = voyageai_client
        self.reranker = reranker
        self.top_k = top_k

    async def _aget_relevant_documents(self, query: str) -> list[Document]:
        # 1. Embed da query (com cache Redis)
        query_embedding = embed_with_cache([query])[0]

        # 2. Vector search no LanceDB (top-100)
        candidates = (
            self.table.search(query_embedding)
            .limit(100)
            .to_pandas()
        )

        # 3. Reranking com XLM-RoBERTa (top-10)
        scores = self.reranker.score(
            query=query,
            documents=candidates["content"].tolist()
        )
        ranked = sorted(
            zip(candidates.itertuples(), scores),
            key=lambda x: x[1],
            reverse=True
        )[:self.top_k]

        # 4. Converter para LangChain Documents
        documents = []
        for row, score in ranked:
            if score > 0.65:  # threshold de relevância
                documents.append(Document(
                    page_content=row.content,
                    metadata={
                        "file": row.file,
                        "lines": row.lines,
                        "score": score,
                    }
                ))

        return documents
```

### RAG Chain com LangChain

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_template("""
Você é um assistente especialista em código.

Contexto do codebase:
{context}

Pergunta: {question}

Responda com base no contexto acima. Se não souber, diga explicitamente.
""")

def format_docs(docs: list[Document]) -> str:
    return "\n\n".join([
        f"[{doc.metadata['file']}:{doc.metadata['lines']}]\n{doc.page_content}"
        for doc in docs
    ])

# Pipeline RAG completo
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

# Uso
answer = await rag_chain.ainvoke("Como validar tokens JWT neste codebase?")
```

## Pipeline Completo com VCR

```python
from vectora.vcr.runtime import VCR

vcr = VCR.from_config()

async def rag_with_vcr(query: str) -> dict:
    # 1. VCR valida a query
    plan_validation = await vcr.validate_plan(query=query)
    if plan_validation["confidence"] < 0.5:
        return {"error": "Query inválida", "confidence": plan_validation["confidence"]}

    # 2. Recuperar contexto
    docs = await retriever.aget_relevant_documents(query)

    # 3. VCR valida o contexto recuperado
    context_validation = await vcr.validate_context(
        query=query,
        context=[doc.page_content for doc in docs]
    )

    # Se contexto insuficiente, expandir busca
    if context_validation["context_sufficiency"] < 0.65:
        docs = await retriever.aget_relevant_documents(query, top_k=200)

    # 4. Gerar resposta
    context = format_docs(docs)
    response = await rag_chain.ainvoke(query)

    # 5. VCR valida a resposta
    response_validation = await vcr.validate_response(
        response=response,
        context=context,
    )

    return {
        "answer": response,
        "sources": [doc.metadata for doc in docs],
        "vcr": {
            "faithfulness": response_validation["faithfulness"],
            "hallucination_risk": response_validation["hallucination_risk"],
        }
    }
```

## Estratégias de Compactação

Quando o contexto é grande, Vectora usa compactação para reduzir tokens:

```python
def compact_context(docs: list[Document], max_tokens: int = 3000) -> list[Document]:
    total_tokens = sum(len(doc.page_content.split()) for doc in docs)

    if total_tokens <= max_tokens:
        return docs

    # Head/tail compaction: manter início e fim de cada chunk
    compacted = []
    for doc in docs:
        lines = doc.page_content.split("\n")
        head = "\n".join(lines[:5])    # primeiras 5 linhas
        tail = "\n".join(lines[-10:])  # últimas 10 linhas
        compacted_content = f"{head}\n...\n{tail}"
        compacted.append(Document(
            page_content=compacted_content,
            metadata=doc.metadata
        ))

    return compacted
```

## Métricas do Pipeline

| Etapa                       | Latência Target  | Métrica de Qualidade |
| --------------------------- | ---------------- | -------------------- |
| **Embedding (VoyageAI)**    | <200ms           | N/A (API externa)    |
| **Vector Search (LanceDB)** | <50ms            | Recall >0.85         |
| **Reranking (XLM-RoBERTa)** | <10ms            | Precision >0.80      |
| **LLM Response**            | <3000ms          | Faithfulness >0.80   |
| **Total Pipeline**          | <500ms (sem LLM) | VCR Score >0.70      |

## External Linking

| Conceito          | Recurso                        | Link                                                                                                                       |
| ----------------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| **LangChain RAG** | RAG com LangChain              | [python.langchain.com/docs/use_cases/question_answering](https://python.langchain.com/docs/use_cases/question_answering/)  |
| **LanceDB**       | Vector database para RAG       | [lancedb.com/docs](https://lancedb.com/docs)                                                                               |
| **VoyageAI**      | Embeddings de alta performance | [voyageai.com](https://www.voyageai.com/)                                                                                  |
| **RAG Paper**     | Retrieval-Augmented Generation | [arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)                                                               |
| **Reranking**     | Cross-encoder reranking        | [sbert.net/examples/applications/retrieve_rerank](https://www.sbert.net/examples/applications/retrieve_rerank/README.html) |
