---
title: Agent Complete
slug: agent-complete
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - agent
  - autonomous
  - decision-making
  - llm
  - reasoning
  - vectora
---

{{< lang-toggle >}}

Um **Agent Complete** é um agente autônomo capaz de tomar decisões informadas com base em contexto enriquecido, sem intervenção humana contínua. No Vectora, isso significa um agente que pode:

1. **Entender** a query do usuário em contexto
2. **Recuperar** código relevante via busca semântica
3. **Enriquecer** contexto com dependências e relacionamentos
4. **Raciocinar** sobre múltiplas hipóteses
5. **Executar** ferramentas para validação
6. **Sintetizar** uma resposta fundamentada

## Arquitetura Agent Complete

```text
Query do Usuário
    ↓
┌───────────────────────────────────────┐
│ 1. Entendimento (Claude sonnet-4-6)  │
│    └─ Decompor pergunta               │
│    └─ Identificar intenção            │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 2. Recuperação (VoyageAI + LanceDB)  │
│    └─ Buscar top-100 chunks similares │
│    └─ Reranking (XLM-RoBERTa)        │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 3. Enriquecimento (PostgreSQL + AST)  │
│    └─ Resolver dependências           │
│    └─ Adicionar metadados             │
│    └─ Conectar relacionamentos        │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 4. Raciocínio (LangGraph)            │
│    └─ Avaliar múltiplas hipóteses     │
│    └─ Decidir próxima ação            │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 5. Execução (Tool Use)               │
│    └─ Rodar testes                   │
│    └─ Validar código                 │
│    └─ Executar MCP tools             │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ 6. Síntese (Geração)                 │
│    └─ Estruturar resposta             │
│    └─ Justificar decisões             │
└───────────────────────────────────────┘
    ↓
Resposta Fundamentada
```

## Diferenças: Simples vs Complete

| Aspecto         | Simples           | Complete                       |
| --------------- | ----------------- | ------------------------------ |
| **Recuperação** | Top-10 chunks     | Top-100 + reranking            |
| **Contexto**    | Metadados básicos | Grafo completo de dependências |
| **Raciocínio**  | Uma passagem      | Multi-hop reasoning            |
| **Ferramentas** | Nenhuma           | MCP tools, testes, validação   |
| **Latência**    | <5s               | 10-30s                         |
| **Custo**       | Baixo             | Médio-Alto                     |
| **Qualidade**   | Boa               | Excelente                      |

## Implementação em LangGraph

Um agent complete usa **LangGraph** para orquestrar o fluxo:

```python
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-6")

# Estado compartilhado
class AgentState(TypedDict):
    query: str
    context: list[dict]
    reasoning: list[str]
    tools_executed: list[str]
    response: str

# Nós do grafo
def retrieve_context(state: AgentState):
    """Recuperar top-100 chunks"""
    results = lancedb_search(state["query"], top_k=100)
    return {"context": results}

def rerank_context(state: AgentState):
    """Reranking com XLM-RoBERTa"""
    scores = reranker.score(state["query"], state["context"])
    top_10 = sorted(zip(state["context"], scores), key=lambda x: x[1])[:10]
    return {"context": top_10}

def enrich_context(state: AgentState):
    """Adicionar dependências e metadados"""
    enriched = []
    for chunk in state["context"]:
        deps = resolve_dependencies(chunk["file"], chunk["class"])
        enriched.append({**chunk, "dependencies": deps})
    return {"context": enriched}

def reason(state: AgentState):
    """Raciocinar sobre hipóteses"""
    prompt = f"""Análise a seguinte pergunta e contexto.

    Pergunta: {state['query']}

    Contexto: {json.dumps(state['context'][:5])}

    Que hipóteses você tem? Qual ferramenta você usaria para validar?"""

    response = llm.invoke(prompt)
    return {"reasoning": [response.content]}

def execute_tools(state: AgentState):
    """Executar ferramentas para validação"""
    tools_used = []

    # Executar testes se relevante
    if "test" in state["query"]:
        test_results = run_tests(state["context"])
        tools_used.append("test_runner")

    return {"tools_executed": tools_used}

def synthesize(state: AgentState):
    """Sintetizar resposta final"""
    prompt = f"""Com base na análise acima, forneça uma resposta completa:

    Pergunta: {state['query']}
    Contexto: {json.dumps(state['context'])}
    Raciocínio: {json.dumps(state['reasoning'])}
    Ferramentas: {state['tools_executed']}"""

    response = llm.invoke(prompt)
    return {"response": response.content}

# Construir grafo
workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_context)
workflow.add_node("rerank", rerank_context)
workflow.add_node("enrich", enrich_context)
workflow.add_node("reason", reason)
workflow.add_node("execute", execute_tools)
workflow.add_node("synthesize", synthesize)

workflow.add_edge("retrieve", "rerank")
workflow.add_edge("rerank", "enrich")
workflow.add_edge("enrich", "reason")
workflow.add_edge("reason", "execute")
workflow.add_edge("execute", "synthesize")
workflow.add_edge("synthesize", END)

workflow.set_entry_point("retrieve")
agent = workflow.compile()
```

Executar agent:

```python
result = agent.invoke({
    "query": "Como funciona autenticação JWT neste codebase?",
    "context": [],
    "reasoning": [],
    "tools_executed": [],
    "response": ""
})

print(result["response"])
```

## Quando Usar Agent Complete

**Use se:**

- Query é complexa (multi-hop reasoning necessário)
- Qualidade é crítica (ex: refactoring de segurança)
- Contexto é grande (muitas dependências)

**Evite se:**

- Query é simples ("qual é o nome da função?")
- Latência é crítica (<5s)
- Orçamento de API é limitado

## Próximas Etapas

- Leia sobre [Context Enrichment](./context-enrichment.md)
- Explore [LangGraph Agent Loop](../langchain/langgraph/agent-loop.md)
- Veja [example Agent Complete](../langchain/langgraph/vectora-agent-example.md)

## External Linking

| Conceito                | Recurso                         | Link                                                                                       |
| ----------------------- | ------------------------------- | ------------------------------------------------------------------------------------------ |
| **LangGraph**           | Agentic framework               | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/)              |
| **Agent Architectures** | Research on agent design        | [arxiv.org/abs/2309.07870](https://arxiv.org/abs/2309.07870)                               |
| **ReAct Pattern**       | Reasoning + Acting framework    | [arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)                               |
| **Tool Use in LLMs**    | Function calling capabilities   | [python.langchain.com/docs/modules/tools](https://python.langchain.com/docs/modules/tools) |
| **Multi-hop Reasoning** | Complex reasoning in QA systems | [openreview.net/forum?id=fADP1HfqiXQ](https://openreview.net/forum?id=fADP1HfqiXQ)         |
