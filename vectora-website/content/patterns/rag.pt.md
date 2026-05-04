---
title: "RAG Conectado: Pipeline de Recuperação do Vectora"
slug: rag
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - ai
  - architecture
  - concepts
  - context-engine
  - embeddings
  - lancedb
  - langchain
  - patterns
  - rag
  - reranker
  - vector-search
  - vcr
  - vectora
  - voyage
  - xlm-roberta
---

{{< lang-toggle >}}

{{< section-toggle >}}

RAG Conectado é a implementação de Retrieval-Augmented Generation do Vectora — um pipeline de 5 etapas que transforma uma query em contexto verificado e compactado, pronto para o LLM. Diferente do RAG tradicional, valida os resultados contra o codebase real via VCR antes de gerar a resposta.

## O Problema do RAG Tradicional em Código

O RAG tradicional trata código como texto: busca por similaridade semântica e entrega os fragmentos mais próximos ao LLM. Isso falha em software porque:

| Problema                 | Causa                         | Consequência                   |
| ------------------------ | ----------------------------- | ------------------------------ |
| Dependências ignoradas   | Busca por fragmentos isolados | LLM não vê que A chama B       |
| Contexto desconectado    | Top-K sem relação estrutural  | Sugestões inválidas no projeto |
| Hallucination de imports | Sem validação pós-recuperação | Código que não compila         |
| Contexto excessivo       | Sem compactação               | Latência e custo altos         |

## Pipeline de 5 Etapas

O Vectora resolve esses problemas com um pipeline sequencial onde cada etapa filtra e valida os dados.

```text
Query
  |
  +-> [1] Embed (VoyageAI voyage-3-large)
  |       -> vetor 1024D, cacheado no Redis por 24h
  |
  +-> [2] Vector Search (LanceDB HNSW)
  |       -> top-100 candidatos, < 50ms
  |
  +-> [3] Rerank (XLM-RoBERTa-small local)
  |       -> top-10 por relevância, < 10ms
  |
  +-> [4] Compact (head/tail)
  |       -> trunca chunks grandes preservando início e fim
  |
  +-> [5] Validate (VCR faithfulness check)
          -> score >= 0.70 para aceitar contexto
```

## Etapa 1: Embedding com VoyageAI

A query é convertida em vetor 1024D pelo modelo voyage-3-large, com cache Redis para evitar chamadas repetidas.

```python
import voyageai
import redis
import hashlib
import json

voyage = voyageai.Client(api_key="...")
r = redis.Redis()

def embed_query(query: str) -> list[float]:
    cache_key = f"embed:{hashlib.sha256(query.encode()).hexdigest()}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    embedding = voyage.embed([query], model="voyage-3-large").embeddings[0]
    r.setex(cache_key, 86400, json.dumps(embedding))
    return embedding
```

## Etapa 2: Busca Vetorial com LanceDB

O vetor da query é usado para buscar os 100 candidatos mais similares via HNSW.

```python
import lancedb

db = lancedb.connect("./data/lancedb")
table = db.open_table("code_chunks")

def vector_search(query_embedding: list[float], top_k: int = 100) -> list[dict]:
    results = (
        table.search(query_embedding)
        .limit(top_k)
        .metric("cosine")
        .to_pandas()
    )
    return results.to_dict("records")
```

## Etapa 3: Reranking com XLM-RoBERTa

Os 100 candidatos são reclassificados pelo reranker local (cross-encoder). Apenas os top-10 avançam.

```python
from vectora.vcr import LocalReranker

reranker = LocalReranker(model_path="models/vcr_reranker_int8.pt")

def rerank(query: str, candidates: list[dict]) -> list[dict]:
    return reranker.rerank(query, candidates, top_k=10)
```

O reranker processa cada par (query, documento) simultaneamente, capturando relações diretas que o bi-encoder não detecta.

## Etapa 4: Compactação head/tail

Chunks grandes são truncados preservando o início (assinatura da função, imports) e o fim (return statement, exceções).

```python
def compact_context(chunks: list[dict], max_tokens: int = 200) -> list[dict]:
    compacted = []
    for chunk in chunks:
        content = chunk["content"]
        tokens = content.split()

        if len(tokens) <= max_tokens:
            compacted.append(chunk)
            continue

        head = tokens[: max_tokens // 2]
        tail = tokens[-(max_tokens // 2) :]
        compacted.append({
            **chunk,
            "content": " ".join(head) + "\n...\n" + " ".join(tail),
        })

    return compacted
```

## Etapa 5: Validação VCR

Antes de entregar o contexto ao LLM, o VCR valida se os fragmentos são fiéis à query (faithfulness check).

```python
import httpx

async def validate_context(query: str, context: list[dict]) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/vcr/validate-plan",
            json={"query": query, "context": context},
            headers={"Authorization": f"Bearer {token}"},
        )
    result = response.json()
    return result["faithfulness"] >= 0.70
```

Se faithfulness < 0.70, o VCR pode acionar recovery: ampliar top_k, mudar estratégia de busca ou retornar erro explicativo ao usuário.

## Integração LangChain LCEL

O pipeline completo é expresso como uma chain LCEL (LangChain Expression Language):

```python
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-6")

rag_chain = (
    RunnablePassthrough.assign(
        embedding=RunnableLambda(lambda x: embed_query(x["query"])),
    )
    | RunnablePassthrough.assign(
        candidates=RunnableLambda(lambda x: vector_search(x["embedding"])),
    )
    | RunnablePassthrough.assign(
        reranked=RunnableLambda(lambda x: rerank(x["query"], x["candidates"])),
    )
    | RunnablePassthrough.assign(
        context=RunnableLambda(lambda x: compact_context(x["reranked"])),
    )
    | RunnableLambda(lambda x: f"Context:\n{x['context']}\n\nQuestion: {x['query']}")
    | llm
    | StrOutputParser()
)

result = await rag_chain.ainvoke({"query": "Como validar tokens JWT?"})
```

## Métricas do Pipeline

| Etapa               | Latência target | Custo           |
| ------------------- | --------------- | --------------- |
| **Embed (cached)**  | < 1ms           | Grátis          |
| **Embed (API)**     | < 200ms         | $0.10/2M tokens |
| **Vector Search**   | < 50ms          | Grátis (local)  |
| **Rerank**          | < 10ms          | Grátis (local)  |
| **Compact**         | < 1ms           | Grátis          |
| **VCR Validate**    | < 10ms          | Grátis (local)  |
| **Total (sem LLM)** | < 500ms p95     | ~$0.001/query   |

## External Linking

| Conceito           | Recurso                        | Link                                                                                        |
| ------------------ | ------------------------------ | ------------------------------------------------------------------------------------------- |
| **RAG**            | Retrieval-Augmented Generation | [arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)                                |
| **LangChain LCEL** | LangChain Expression Language  | [python.langchain.com/docs/concepts/lcel](https://python.langchain.com/docs/concepts/lcel/) |
| **LanceDB**        | Vector database local com HNSW | [lancedb.com/docs](https://lancedb.com/docs)                                                |
| **VoyageAI**       | Embeddings de alta performance | [voyageai.com](https://www.voyageai.com/)                                                   |
| **XLM-RoBERTa**    | Multilingual cross-encoder     | [huggingface.co/xlm-roberta-small](https://huggingface.co/xlm-roberta-small)                |
