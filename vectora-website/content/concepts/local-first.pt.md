---
title: Local-First Architecture
slug: local-first
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - architecture
  - cpu
  - inference
  - local-processing
  - privacy
  - vectora
---

{{< lang-toggle >}}

O Vectora favorece computação **local sempre que possível**: reranking roda em CPU, busca vetorial é serverless em disco, e parsing de código usa AST local. Apenas o LLM principal e embedding são remotos (necessariamente).

## Componentes Locais vs Remotos

| Componente                   | Localidade   | Razão               | Latência               |
| ---------------------------- | ------------ | ------------------- | ---------------------- |
| **LLM (Claude/GPT/Gemini)**  | Remoto       | API obrigatória     | 1-5s                   |
| **Embeddings (VoyageAI)**    | Remoto       | API especializada   | ~200ms (ou <1ms cache) |
| **Reranking (XLM-RoBERTa)**  | Local        | CPU rápido          | <10ms                  |
| **Busca Vetorial (LanceDB)** | Local        | Serverless em disco | <50ms                  |
| **Parsing (LST/AST)**        | Local        | Linguagem nativa    | <100ms                 |
| **PostgreSQL**               | Local/Remoto | Flexível            | <5ms (local)           |
| **Redis**                    | Local/Remoto | Flexível            | <1ms (local)           |

## Por que Local-First?

### 1. Privacidade

Código **nunca sai do seu servidor**:

```text
User Query
    ↓
LOCAL: Parse + analyze
LOCAL: Busca em LanceDB
LOCAL: Reranking (XLM-RoBERTa)
    ↓
REMOTO: LLM synthesis apenas
    ↓
Resposta (código + análise local)
```

Apenas o **prompt + query** vão para LLM, não o código completo.

### 2. Performance

Componentes locais são **muito mais rápidos** do que network round-trips:

```text
Reranking local:  < 10ms
Reranking remoto: ~ 500ms (rede + API)

Busca em LanceDB: < 50ms
Busca em serviço remoto: ~ 200ms (rede)
```

### 3. Custo

Reranking e busca local **reduzem chamadas de API**:

- VoyageAI: apenas embedding (com Redis cache)
- LLM: apenas síntese (menor payload)
- **Economia**: 90%+ em chamadas de API

## Reranking Local com XLM-RoBERTa

XLM-RoBERTa-small roda **100% localmente** em CPU:

```python
from sentence_transformers import CrossEncoder

# Modelo pré-treinado multilíngue (~120MB)
reranker = CrossEncoder('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1')

# Reranking de top-100 para top-10
query = "How to implement JWT authentication"
candidates = [
    "def verify_token(token: str) -> dict: ...",  # Score: 0.95
    "class AuthService: ...",                       # Score: 0.87
    "def decode_jwt(token: str): ...",             # Score: 0.82
    # ... 97 more
]

scores = reranker.predict([[query, cand] for cand in candidates])
top_10_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]
```

**Latência:**

- Load model: 100ms (one-time)
- Rerank 100 candidates: <10ms

**Custo:** Grátis (local)

## Busca Vetorial Local (LanceDB)

LanceDB é **serverless** — arquivo `.lance` em disco:

```python
import lancedb

# Conectar
db = lancedb.connect("./vectora-data")
table = db.open_table("bucket-123")

# Buscar
results = table.search(query_vector).limit(100).to_list()
# Latência: < 50ms (HNSW local)
```

**Vantagens:**

- Sem API calls
- Sem rede
- Sem serviço externo
- Sem custo operacional
- Backup simples (copiar arquivo)

## Parsing Local (LST/AST)

Análise sintática roda no seu servidor:

```python
import ast
from tree_sitter_language_pack import get_language

# Analisar código Python
tree = ast.parse(code)

# Extrair estrutura
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(f"Função: {node.name}")

# Para outras linguagens, usar tree-sitter
language = get_language("typescript")
parser = language.parser
tree = parser.parse(code.encode())
```

**Latência:** <100ms por arquivo

**Custo:** Grátis

## Tradeoffs: Local vs Remoto

### Local-First (Vectora padrão)

**Pros:**

- Privacidade garantida
- Performance máxima
- Custo mínimo
- Independência de rede

**Cons:**

- Requer recursos (CPU, RAM)
- Setup mais complexo
- Manutenção de índices

### Cloud-First (Alternativa)

**Pros:**

- Zero infraestrutura
- Escalabilidade automática
- Simples de usar

**Cons:**

- Código exposto
- Latência > rede
- Custo de API contínuo

Vectora escolhe **local-first** como padrão porque código é a coisa **mais valiosa** de proteger.

## Configuração

Habilitar/desabilitar componentes locais:

```bash
# Cache local (LanceDB)
vectora config set lancedb_enabled true
vectora config set lancedb_path ./vectora-data

# Reranking local
vectora config set reranking_enabled true
vectora config set reranking_model xlm-roberta-small

# Parsing local
vectora config set ast_parsing_enabled true
```

## Deployment com Local-First

Para produção, a arquitetura fica:

```text
┌──────────────────────┐
│   Your VPS Server    │
├──────────────────────┤
│  LanceDB (local)     │  ← Busca vetorial
│  XLM-RoBERTa (CPU)   │  ← Reranking
│  PostgreSQL (local)  │  ← Metadados
│  Redis (local)       │  ← Cache
│  Vectora app        │
└──────────────────────┘
         │
         │ REMOTO: embedding + LLM apenas
         ↓
  VoyageAI API + Claude API
```

Custo mensal:

- Servidor VPS: ~$10-50
- VoyageAI: ~$10-50 (com cache)
- Claude: ~$20-100 (com heavy usage)
- **Total: $40-200 (vs $1000+ para cloud-first)**

## External Linking

| Conceito         | Recurso                            | Link                                                                             |
| ---------------- | ---------------------------------- | -------------------------------------------------------------------------------- |
| **LanceDB**      | Local vector database              | [lancedb.com/docs](https://lancedb.com/docs)                                     |
| **XLM-RoBERTa**  | Multilingual cross-encoder         | [huggingface.co/cross-encoder](https://huggingface.co/cross-encoder)             |
| **tree-sitter**  | Code parser for multiple languages | [tree-sitter.github.io](https://tree-sitter.github.io/)                          |
| **Python AST**   | Abstract syntax trees              | [docs.python.org/3/library/ast](https://docs.python.org/3/library/ast.html)      |
| **Data Privacy** | Computing privacy principles       | [en.wikipedia.org/wiki/Data_privacy](https://en.wikipedia.org/wiki/Data_privacy) |
