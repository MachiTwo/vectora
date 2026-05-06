---
title: "Busca Vetorial com LanceDB"
slug: vector-search
date: "2026-05-03T09:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - ai
  - architecture
  - concepts
  - embeddings
  - hnsw
  - lancedb
  - rag
  - reranker
  - semantic-search
  - vector-database
  - vector-search
  - vectora
  - voyage
---

{{< lang-toggle >}}

{{< section-toggle >}}

Busca Vetorial permite encontrar informações não por palavras-chave exatas, mas por significado semântico. O Vectora usa LanceDB com HNSW para armazenar e buscar embeddings 1024D gerados por VoyageAI. Tudo roda localmente em disco — sem servidor externo.

## O Que é Busca Vetorial?

Imagine que você quer encontrar no seu código onde o sistema lida com "cancelamento de assinatura":

- **Busca Tradicional**: Procura por `cancel`, `subscription`, `unsub`. Se o programador usou `deactivateAccount`, a busca falha.
- **Busca Vetorial**: Entende que "deactivate account" e "cancel subscription" têm o mesmo significado semântico e encontra o resultado.

## Como Funciona: Do Código ao Vetor

### 1. Embedding (VoyageAI)

VoyageAI (voyage-4) processa um trecho de código e gera um vetor de 1024 números que representam o significado semântico:

- Código sobre "Auth" terá padrões altos nas dimensões de segurança.
- Código sobre "Database" terá padrões altos nas dimensões de persistência.

### 2. Espaço Vetorial (LanceDB)

LanceDB armazena esses vetores localmente em disco e usa HNSW para buscas eficientes. Código similar fica fisicamente próximo no espaço vetorial de 1024 dimensões.

### 3. Busca HNSW

HNSW (Hierarchical Navigable Small World) navega o espaço vetorial em múltiplas camadas:

1. A camada superior tem poucos pontos (pontos âncora distantes)
2. O algoritmo pula rapidamente entre pontos distantes
3. Conforme aproxima, desce para camadas mais densas

Resultado: encontra top-100 candidatos em < 50ms para bases com 1M+ vetores.

## LanceDB: Setup e Configuração

### Conectar ao banco

```python
import lancedb

db = lancedb.connect("./data/lancedb")
```

### Criar tabela com índice

```python
table = db.create_table(
    "code_chunks",
    schema={
        "id": "string",
        "file": "string",
        "content": "string",
        "embedding": "vector[1024]",
    },
    mode="overwrite",
)

# Criar índice HNSW
table.create_index(
    metric="cosine",
    num_partitions=256,
    num_sub_vectors=96,
)
```

### Busca Semântica

```python
query_embedding = voyageai.embed(["Como validar JWT?"], model="voyage-4").embeddings[0]

results = (
    table.search(query_embedding)
    .limit(100)
    .metric("cosine")
    .to_pandas()
)

# results columns: id, file, content, embedding, _distance
# _distance: 0.0 = idêntico, 1.0 = completamente diferente
```

### Busca com Filtros

```python
# Filtrar por linguagem ou namespace
results = (
    table.search(query_embedding)
    .where("file LIKE 'src/auth/%'")
    .limit(50)
    .to_pandas()
)
```

## Métricas de Similaridade

| Métrica                | Como Funciona                      | Quando Usar                           |
| ---------------------- | ---------------------------------- | ------------------------------------- |
| **Cosine Similarity**  | Ângulo entre vetores (normalizado) | Texto e código — padrão do Vectora    |
| **Euclidean Distance** | Distância em linha reta            | Dados numéricos puros                 |
| **Dot Product**        | Multiplicação direta               | Vetores já normalizados — mais rápido |

O Vectora usa **cosine similarity** por padrão.

## Comparativo: LanceDB vs MongoDB Atlas

| Característica  | LanceDB (Vectora)         | MongoDB Atlas              |
| --------------- | ------------------------- | -------------------------- |
| **Hosting**     | Local (arquivo)           | Nuvem (SaaS)               |
| **Privacidade** | Dados não saem da máquina | Dados na nuvem             |
| **Custo**       | Grátis                    | Pago (por storage/queries) |
| **Latência**    | < 50ms local              | 100-500ms (rede)           |
| **Setup**       | Zero config               | Conta + configuração       |
| **Escala**      | Até ~50M vetores em disco | Escala ilimitada           |

## FAQ

### Por que a busca traz resultados sem o texto que digitei?

Porque busca pelo significado, não pela palavra. "Segurança" traz `Bcrypt`, `JWT` e `validate_token` mesmo sem essas palavras na query.

### O Vectora entende código de qualquer linguagem?

Sim. VoyageAI (voyage-4) foi treinado em múltiplas linguagens. Python, TypeScript, Java, Go, Rust — todos produzem embeddings comparáveis.

### Qual é o limite de vetores?

LanceDB suporta eficientemente até ~50M vetores em disco. Para codebases típicos (< 1M chunks), performance é < 50ms por query.

## External Linking

| Conceito              | Recurso                                | Link                                                                                       |
| --------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------ |
| **LanceDB**           | Vector database local com HNSW         | [lancedb.com/docs](https://lancedb.com/docs)                                               |
| **VoyageAI**          | Embeddings de alta performance         | [voyageai.com](https://www.voyageai.com/)                                                  |
| **HNSW**              | Efficient approximate nearest neighbor | [arxiv.org/abs/1603.09320](https://arxiv.org/abs/1603.09320)                               |
| **Cosine Similarity** | Métricas de similaridade vetorial      | [en.wikipedia.org/wiki/Cosine_similarity](https://en.wikipedia.org/wiki/Cosine_similarity) |
| **ANN Benchmark**     | Benchmark de algoritmos ANN            | [ann-benchmarks.com](https://ann-benchmarks.com)                                           |
