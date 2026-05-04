---
title: "Context Engineering em Agentes"
slug: "langchain/context-engineering"
description: "Fornecer as informações corretas no formato certo para LLMs"
date: 2026-05-03
type: docs
sidebar:
  open: true
breadcrumbs: true
tags: ["langchain", "context", "engineering", "patterns", "prompting"]
---

{{< lang-toggle >}}

Context Engineering é o trabalho número 1 de engenheiros de IA. Agentes falham não porque o modelo é incapaz, mas porque **o contexto correto não foi fornecido ao LLM**.

## Os Três Tipos de Contexto

### 1. Model Context (Transiente)

Informações que entram em **cada chamada ao LLM**. Controlam o que o modelo vê:

```python
# System message - instruções base
system = "You are a helpful Python expert"

# Messages - histórico e contexto
messages = [
    SystemMessage(system),
    HumanMessage("Ajude com async/await"),
    AIMessage("Claro, vou explicar..."),
    HumanMessage("E sobre exception handling?")
]

# Tools - o que o modelo pode fazer
tools = [search_tool, code_executor]

# Model - qual LLM usar
model = ChatAnthropic(model="claude-3-opus")

response = model.invoke(messages, tools=tools)
```

**Estratégias:**
- **Few-shot**: Incluir exemplos de entrada/saída
- **Chain-of-thought**: Pedir raciocínio passo-a-passo
- **Prompt templates**: Reutilizar prompts estruturados
- **Dynamic prompts**: Mudar instruções baseado em contexto

### 2. Tool Context (Persistente)

Informações que **ferramentas podem acessar e produzir**. Definem o que acontece entre chamadas ao LLM:

```python
from langchain.tools import tool

@tool
def search_documents(query: str) -> str:
    """Busca em documentos do usuário"""
    # Acessa: contexto persistente (user_id, buckets, permissões)
    # Produz: resultados que voltam ao agente
    return results

# Tool tem acesso a runtime context
# State: memória de curto prazo (histórico)
# Context: configuração imutável (user_id, org_id)
# Store: memória persistente entre turnos
```

**O que controla:**
- Qual contexto cada ferramenta pode acessar
- Quais dados persistem entre turnos
- Isolamento por usuário/organização
- Auditoria e compliance

### 3. Lifecycle Context (Persistente)

Modificações ao longo da **execução do agente**. Controlam o que acontece entre etapas:

```python
# Antes do agente rodar
def pre_agent_hook(state):
    # Sumarizar histórico se muito longo
    if len(state["messages"]) > 20:
        state["messages"] = summarize_and_truncate(state["messages"])
    return state

# Depois do agente rodar
def post_agent_hook(state):
    # Guardrails: validar resposta
    if contains_sensitive_data(state["messages"][-1]):
        return "Resposta bloqueada por segurança"
    return state

# Entre cada ferramenta
def tool_middleware(tool_result):
    # Logging, monitoring, transformação
    log_tool_execution(tool_result)
    return enrich_result(tool_result)
```

**Casos de uso:**
- Sumarização automática de histórico longo
- Guardrails de segurança
- Logging e monitoramento
- Transformação de dados
- Validação de saídas

## Implementação com Middleware

Middleware é o mecanismo para controlar contexto:

```python
from langgraph.graph import StateGraph

def middleware_summarize(state):
    """Sumariza histórico se ficar grande"""
    if len(state["messages"]) > 30:
        old_messages = state["messages"][:-5]
        summary = summarize_messages(old_messages)
        state["messages"] = [
            SystemMessage(f"Histórico anterior: {summary}"),
            *state["messages"][-5:]
        ]
    return state

def middleware_guardrails(state):
    """Valida resposta antes de retornar"""
    if not is_safe(state["messages"][-1]):
        raise ValueError("Resposta bloqueada")
    return state

graph = StateGraph(State)
# ... adicionar nós ...
graph.add_node("summarize", middleware_summarize)
graph.add_node("validate", middleware_guardrails)
graph.add_edge("agent", "summarize")
graph.add_edge("summarize", "validate")
```

## Padrões Comuns

### RAG-based Context

Enrichir contexto com documentos relevantes:

```python
def add_rag_context(query: str, state: dict) -> dict:
    # Buscar documentos relevantes
    docs = vectorstore.similarity_search(query, k=5)
    
    # Adicionar ao contexto
    context = "\n".join([doc.page_content for doc in docs])
    
    state["system_context"] = f"Documentos relevantes:\n{context}"
    return state
```

### User-specific Context

Customizar contexto por usuário:

```python
def load_user_context(user_id: str, state: dict) -> dict:
    # Permissões
    state["permissions"] = get_user_permissions(user_id)
    
    # Preferências
    state["preferences"] = get_user_preferences(user_id)
    
    # Histórico pessoal
    state["history"] = get_user_history(user_id, limit=10)
    
    return state
```

### Knowledge Base Context

Integrar base de conhecimento:

```python
def add_knowledge_context(topic: str, state: dict) -> dict:
    # Buscar documentação, FAQs, exemplos
    kb_results = knowledge_base.search(topic, limit=3)
    
    system = state.get("system", "")
    system += f"\n\nRelevant documentation:\n"
    system += "\n".join(kb_results)
    
    state["system"] = system
    return state
```

## External Linking

| Conceito | Recurso | Link |
|----------|---------|------|
| Context Engineering | Overview | [https://docs.langchain.com/oss/python/langchain/context-engineering](https://docs.langchain.com/oss/python/langchain/context-engineering) |
| Prompting Strategy | Prompt Engineering | [https://docs.langchain.com/oss/python/langchain/guides/prompt_engineering](https://docs.langchain.com/oss/python/langchain/guides/prompt_engineering) |
| Few-shot Learning | Few-shot Patterns | [https://docs.langchain.com/oss/python/langchain/prompts/few_shot_examples](https://docs.langchain.com/oss/python/langchain/prompts/few_shot_examples) |
| RAG Patterns | Retrieval Augmented | [https://docs.langchain.com/oss/python/langchain/retrieval](https://docs.langchain.com/oss/python/langchain/retrieval) |
| Middleware | Runtime Context | [https://docs.langchain.com/oss/python/langchain/runnables](https://docs.langchain.com/oss/python/langchain/runnables) |
