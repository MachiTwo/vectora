---
title: "Sistemas Multi-Agent"
slug: "langchain/multi-agent-systems"
description: "5 padrões para coordenar múltiplos agentes"
date: 2026-05-03
type: docs
sidebar:
  open: true
breadcrumbs: true
tags: ["langchain", "multi-agent", "patterns", "coordination", "orchestration"]
---

{{< lang-toggle >}}

Existem **5 padrões fundamentais** para arquitetar sistemas multi-agente. A escolha depende de seus requisitos de controle, latência e contexto.

## Padrão 1: Subagentes

**Um agente principal coordena subagentes como ferramentas.**

**Como funciona:**
```
┌─ Agente Principal ─┐
│                    │
│ ├─ [Tool 1] → Subagent A
│ ├─ [Tool 2] → Subagent B
│ └─ [Tool 3] → Subagent C
│                    │
└──────────────────┘
```

**Implementação:**
```python
from langchain.tools import tool

@tool
def research_agent(topic: str) -> str:
    """Delega pesquisa para subagent especializado"""
    subagent = Agent(name="researcher", model="claude-opus")
    return subagent.invoke(f"Pesquise: {topic}")

@tool
def analyze_agent(data: str) -> str:
    """Delega análise para subagent especializado"""
    subagent = Agent(name="analyst", model="claude-opus")
    return subagent.invoke(f"Analise: {data}")

# Agente principal tem controle total
tools = [research_agent, analyze_agent]
main_agent = Agent(tools=tools, model="claude-opus")

result = main_agent.invoke("Pesquise AI e analise as tendências")
```

**Quando usar:**
- Desenvolvimento distribuído entre times
- Execução paralela de subagents
- Controle centralizado necessário

**Vantagens:**
- Controle total do fluxo
- Fácil de debugar
- Isolamento de responsabilidades

**Limitações:**
- Todas as chamadas passam pelo principal (bottleneck)
- Mais turnos = maior latência
- Contexto pode ficar grande

## Padrão 2: Handoffs

**Agentes transferem controle dinamicamente, cada um pode conversar com o usuário.**

**Como funciona:**
```
User
  ↕
Agente A ↔ Agente B ↔ Agente C
```

**Implementação:**
```python
def agent_a(user_input: str):
    """Agente A pode decidir transferir para B"""
    
    response = llm.invoke([
        SystemMessage("Você é especialista em X"),
        HumanMessage(user_input)
    ])
    
    # Se precisa de expertise em Y, transfere
    if needs_handoff_to_b(response):
        return handoff_to_agent_b(user_input)
    
    return response

def agent_b(user_input: str):
    """Agente B recebe contexto de A"""
    
    response = llm.invoke([
        SystemMessage("Você é especialista em Y"),
        SystemMessage(f"Contexto anterior: {previous_context}"),
        HumanMessage(user_input)
    ])
    
    if needs_handoff_to_c(response):
        return handoff_to_agent_c(user_input)
    
    return response
```

**Quando usar:**
- Requisições repetidas (economia 40-50% de chamadas)
- Especialização clara por domínio
- Usuários podem conversar com múltiplos agentes

**Vantagens:**
- Menos round-trips
- Cada agente especializado
- Flexível

**Limitações:**
- Mais complexo de coordenar
- Perda de contexto em transferências

## Padrão 3: Skills

**Um único agente carrega prompts especializados sob demanda.**

**Como funciona:**
```
┌─ Agente Universal ─────┐
│                        │
│ skills = {            │
│   "coding": prompt_a,  │
│   "writing": prompt_b, │
│   "math": prompt_c     │
│ }                      │
│                        │
└────────────────────────┘
```

**Implementação:**
```python
SKILLS = {
    "coding": """Você é um expert em Python.
    Ajude com debugging, refactoring, e best practices.""",
    
    "writing": """Você é um escritor criativo.
    Ajude com prosa, poesia, e storytelling.""",
    
    "math": """Você é um matemático.
    Resolva problemas, explique conceitos."""
}

def universal_agent(user_input: str, skill: str):
    """Mesmo agente, prompt diferente por skill"""
    
    system = SKILLS.get(skill, SKILLS["coding"])
    
    response = llm.invoke([
        SystemMessage(system),
        HumanMessage(user_input)
    ])
    
    return response
```

**Quando usar:**
- Mesma entidade, múltiplas responsabilidades
- Custo importante (menos contexto)
- Tarefas bem-definidas

**Vantagens:**
- Simples de implementar
- Sem overhead de múltiplos agentes
- Rápido

**Limitações:**
- Um agente pode não ser expert em tudo
- Difícil debugar qual skill falhou

## Padrão 4: Router

**Uma etapa de roteamento classifica e direciona para agentes especializados.**

**Como funciona:**
```
User Input → [Router] → {
                          ├─ Agent A (Expert em X)
                          ├─ Agent B (Expert em Y)
                          └─ Agent C (Expert em Z)
                        } → Synthesizer → Output
```

**Implementação:**
```python
def router(user_input: str) -> str:
    """Classifica entrada e retorna nome do agente"""
    
    classification = llm.invoke([
        SystemMessage("""Classifique a entrada como:
        - 'coding': Perguntas sobre programação
        - 'analysis': Análise de dados
        - 'general': Tópicos gerais"""),
        HumanMessage(user_input)
    ])
    
    return classification.lower()

def synthesize(results: dict) -> str:
    """Combina resultados de múltiplos agentes"""
    
    response = llm.invoke([
        SystemMessage("Sintetize estes resultados em uma resposta coerente"),
        HumanMessage(f"Resultados: {results}")
    ])
    
    return response

# Orquestração
def multi_agent_routing(user_input: str):
    # Roteie
    route = router(user_input)
    
    # Execute agentes especializados em paralelo
    results = {}
    results["coding"] = agents["coding"].invoke(user_input)
    results["analysis"] = agents["analysis"].invoke(user_input)
    
    # Sintetize
    return synthesize(results)
```

**Quando usar:**
- Entradas variadas, múltiplos caminhos
- Execução paralela importante
- Resultado final requer síntese

**Vantagens:**
- Execução paralela
- Especialização clara
- Flexível para novas entradas

**Limitações:**
- Overhead de múltiplas chamadas
- Síntese pode ser complexa

## Padrão 5: Custom Workflow

**LangGraph com lógica determinística + comportamento agentico.**

**Como funciona:**
```
Etapa 1: Validação (determinística)
    ↓
Etapa 2: Roteamento (agentico)
    ↓
Etapa 3: Execução (paralelo)
    ↓
Etapa 4: Agregação (determinística)
```

**Implementação:**
```python
from langgraph.graph import StateGraph, START, END

class MultiAgentState(TypedDict):
    input: str
    route: str
    results: dict
    output: str

def validate(state):
    if len(state["input"]) > 1000:
        raise ValueError("Input muito longo")
    state["validated"] = True
    return state

def route_node(state):
    classification = llm.invoke(state["input"])
    state["route"] = classification
    return state

def execute_agents(state):
    if state["route"] == "coding":
        state["results"]["code"] = agents["coding"].invoke(state["input"])
    elif state["route"] == "analysis":
        state["results"]["analysis"] = agents["analysis"].invoke(state["input"])
    return state

def aggregate(state):
    state["output"] = synthesize_results(state["results"])
    return state

graph = StateGraph(MultiAgentState)
graph.add_node("validate", validate)
graph.add_node("route", route_node)
graph.add_node("execute", execute_agents)
graph.add_node("aggregate", aggregate)

graph.add_edge(START, "validate")
graph.add_edge("validate", "route")
graph.add_edge("route", "execute")
graph.add_edge("execute", "aggregate")
graph.add_edge("aggregate", END)

app = graph.compile()
```

**Quando usar:**
- Workflows complexos
- Mix de lógica determinística + agentica
- Controle fino necessário

**Vantagens:**
- Máxima flexibilidade
- Controle total
- Combina o melhor de tudo

**Limitações:**
- Mais complexo de implementar
- Requer compreensão de LangGraph

## Decisão Rápida

| Padrão | Controle | Latência | Complexidade | Melhor para |
|--------|----------|----------|--------------|------------|
| Subagentes | Alto | Média | Baixa | Time distribuído |
| Handoffs | Médio | Baixa | Média | Domínios claros |
| Skills | Alto | Baixa | Baixa | Custo importante |
| Router | Médio | Médio | Média | Entradas variadas |
| Custom | Alto | Variável | Alta | Workflows complexos |

## External Linking

| Conceito | Recurso | Link |
|----------|---------|------|
| Multi-Agent | Overview | [https://docs.langchain.com/oss/python/langchain/multi-agent/index](https://docs.langchain.com/oss/python/langchain/multi-agent/index) |
| Subagents | Pattern Guide | [https://docs.langchain.com/oss/python/langchain/multi-agent/subagents](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents) |
| Handoffs | Agent Transfer | [https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs) |
| Router | Routing Pattern | [https://docs.langchain.com/oss/python/langchain/multi-agent/router](https://docs.langchain.com/oss/python/langchain/multi-agent/router) |
| LangGraph | Orchestration | [https://docs.langchain.com/oss/python/langgraph/](https://docs.langchain.com/oss/python/langgraph/) |
