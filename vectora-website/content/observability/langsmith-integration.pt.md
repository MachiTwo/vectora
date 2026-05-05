---
title: LangSmith Integration
slug: langsmith-integration
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - langsmith
  - debugging
  - observability
  - llm
  - vectora
---

{{< lang-toggle >}}

**LangSmith** é a plataforma de debugging e observabilidade para agentes LLM. Em Vectora, LangSmith rastreia:

- Cada chamada de LLM (prompt, contexto, resposta)
- Uso de ferramentas (search, reranking)
- Decisões de agente (qual ferramenta usar, quando parar)
- Latência e tokens

## Setup do LangSmith

### 1. Criar Conta e Chave de API

1. Ir para [langsmith.smith.langchain.com](https://smith.langchain.com)
2. Registrar / Login
3. Ir para "Settings" → "API Keys"
4. Copiar chave de API

### 2. Instalar Bibliotecas

```bash
pip install langsmith langchain langchain-anthropic
```

### 3. Configurar Variáveis de Ambiente

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=<sua-api-key>
export LANGCHAIN_PROJECT="vectora-development"
```

Ou em `.env`:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=sk-lsmith-abc123...
LANGCHAIN_PROJECT=vectora-development
```

## Instrumentação Automática

Com as variáveis de ambiente configuradas, LangSmith rastreia automaticamente:

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

# Automaticamente rastreado em LangSmith
llm = ChatAnthropic(model="claude-sonnet-4-6")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um especialista em código."),
    ("human", "{question}")
])

chain = prompt | llm

# Cada invocação aparece em LangSmith
response = chain.invoke({"question": "Como implementar JWT?"})
```

## Rastreamento de Agentes

Para agentes LangGraph com Vectora:

```python
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from vectora import search_with_context

# Cada nó e execução é rastreada em LangSmith
graph = StateGraph(AgentState)

def search_tool(state):
    """Ferramenta de busca - rastreada automaticamente"""
    query = state["messages"][-1].content
    results = search_with_context(query, bucket_id="docs")
    return {"search_results": results}

def llm_node(state):
    """Nó LLM - rastreado automaticamente"""
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": messages + [response]}

graph.add_node("search", search_tool)
graph.add_node("llm", llm_node)
graph.add_conditional_edges("llm", should_search, {"yes": "search", "no": END})
graph.set_entry_point("llm")

# Compilar
app = graph.compile()

# Executar - tudo rastreado em LangSmith
state = app.invoke({"messages": [HumanMessage("Query")]})
```

## Dashboard LangSmith

### 1. Ver Traces

Dashboard mostra:

```text
Project: vectora-development
├─ Run 1: search_question
│  ├─ LLM Call: "What is JWT?"
│  │  └─ Tokens: 50 input, 200 output
│  ├─ Tool Call: search
│  │  └─ Results: 8 chunks
│  ├─ LLM Call: "Synthesize response"
│  │  └─ Tokens: 500 input, 150 output
│  └─ Total: 2.34s
│
├─ Run 2: semantic_search
│  ...
```

### 2. Análise de Performance

Para cada trace, LangSmith mostra:

- **Latência**: Tempo total + por componente
- **Tokens**: Input/output + custo
- **Erros**: Stack traces, exceções
- **Mensagens**: Prompts, respostas, contexto

### 3. Comparação de Runs

Comparar diferentes runs da mesma query:

```text
Run A (claude-sonnet-4-6):
├─ Latency: 2.1s
├─ Tokens: 550 input, 350 output
└─ Cost: $0.032

Run B (claude-opus-4-7):
├─ Latency: 3.2s
├─ Tokens: 520 input, 400 output
└─ Cost: $0.065

Run C (claude-haiku-4-5):
├─ Latency: 1.8s
├─ Tokens: 480 input: 280 output
└─ Cost: $0.011
```

## Rastreamento Customizado

### Rastrear Operações Específicas

```python
from langsmith import trace, wrappers

@trace
def search_and_rerank(query: str, bucket_id: str):
    """Operação customizada rastreada em LangSmith"""

    # Tudo dentro desta função é um trace
    results = search_with_context(query, bucket_id)
    reranked = rerank_results(results, query)

    return reranked

# Usar a função
results = search_and_rerank("JWT authentication", "docs")
```

### Logging Customizado dentro de Traces

```python
from langsmith import get_trace_id

def search_with_logging(query: str):
    trace_id = get_trace_id()

    logger.info(f"Search started", extra={
        "trace_id": trace_id,
        "query": query
    })

    results = search_with_context(query)

    logger.info(f"Search completed", extra={
        "trace_id": trace_id,
        "num_results": len(results)
    })

    return results
```

## Feedback e Evaluação

### Registrar Feedback

```python
from langsmith import client

# Após executar agente
trace_id = "run-abc123"
feedback_value = 0.9  # Score de 0-1

client.create_feedback(
    run_id=trace_id,
    key="user_rating",
    score=feedback_value,
    comment="Resposta precisa e útil"
)
```

### Executar Evals Automáticas

```python
from langsmith.evaluation import EvaluationResult, evaluate

def correctness_eval(run, example):
    """Avaliar se a resposta está correta"""

    predicted = run.outputs.get("output")
    ground_truth = example.outputs.get("expected_output")

    # Usar LLM para julgar
    eval_prompt = f"""
    Pergunta: {example.inputs['question']}
    Resposta esperada: {ground_truth}
    Resposta gerada: {predicted}

    A resposta gerada responde corretamente à pergunta?
    """

    score = llm.invoke(eval_prompt)

    return EvaluationResult(
        key="correctness",
        score=score  # 0-1
    )

# Executar evaluação em todos os runs de um projeto
evaluate(
    correctness_eval,
    dataset_name="vectora-qa-dataset",
    experiment_prefix="claude-sonnet-eval"
)
```

## Troubleshooting

### Traces não aparecem em LangSmith

```bash
# 1. Verificar variáveis de ambiente
echo $LANGCHAIN_TRACING_V2
echo $LANGCHAIN_API_KEY

# 2. Se não configuradas, adicionar:
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=sk-lsmith-...

# 3. Reiniciar aplicação
```

### Erro de autenticação

```python
# Verificar se chave está correta
from langsmith import client as ls_client

try:
    ls_client.list_projects()
    print("Autenticação OK")
except Exception as e:
    print(f"Erro: {e}")
```

### Alto custo de tracing

```python
# Rastrear apenas fração de requisições
import random

if random.random() < 0.1:  # 10% amostragem
    # Rastrear
    response = llm.invoke(prompt)
else:
    # Não rastrear
    pass
```

## Integração com Observabilidade

Combinar LangSmith com outras ferramentas:

```python
import structlog
from langsmith import get_trace_id

# Adicionar trace_id aos logs
trace_id = get_trace_id()
logger = structlog.get_logger()
logger = logger.bind(trace_id=trace_id)

logger.info("Agent decision", action="search")
# Log aparece em estrutura JSON com trace_id

# Correlacionar logs com traces:
# - LangSmith mostra os spans
# - Log agregator (ELK, Datadog) mostra os logs
# - Ambos compartilham trace_id para correlação
```

## External Linking

| Conceito             | Recurso                  | Link                                                                               |
| -------------------- | ------------------------ | ---------------------------------------------------------------------------------- |
| **LangSmith**        | LLM debugging platform   | [smith.langchain.com](https://smith.langchain.com/)                                |
| **LangChain Docs**   | Framework documentation  | [python.langchain.com](https://python.langchain.com/)                              |
| **LangGraph**        | Agent framework          | [langchain.com/docs/langgraph](https://langchain.com/docs/langgraph)               |
| **OpenTelemetry**    | Instrumentation standard | [opentelemetry.io](https://opentelemetry.io/)                                      |
| **Evaluation Guide** | LangSmith evaluation     | [smith.langchain.com/docs/evaluation](https://smith.langchain.com/docs/evaluation) |
