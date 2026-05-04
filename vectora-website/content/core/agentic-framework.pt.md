---
title: "Deep Agents Framework: O Sistema Nervoso do Vectora"
slug: agentic-framework
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - deep-agents
  - langchain
  - langgraph
  - ai
  - architecture
  - concepts
  - errors
  - orchestration
  - rag
  - security
  - state
  - system
  - tools
  - vectora
  - planning
---

{{< lang-toggle >}}

{{< section-toggle >}}

Deep Agents é o sistema nervoso distribuído do Vectora — construído sobre LangChain e LangGraph. É a inteligência que permeia cada camada, observando, planejando, executando e corrigindo o comportamento em tempo real. Diferente de sistemas RAG tradicionais que apenas enviam dados para uma LLM, Deep Agents torna o Vectora auto-consciente e auto-corretivo, garantindo que as respostas sejam precisas, seguras e contextualizadas.

## O Que Deep Agents Realmente É

Deep Agents é um framework de **planejamento e execução multi-etapas** que gerencia o ciclo de vida de cada interação do usuário.

- **Planejamento Estruturado**: O agente formula um plano de ação antes de executar, usando LLM reasoning e VCR validação.
- **Execução com Observação**: Após cada ferramenta executada, o agente observe o resultado e ajusta seu raciocínio imediatamente.
- **Meta-cognição**: O sistema avalia sua confiança e decide autonomamente quando deve iterar, corrigir ou delegar a VCR.
- **Auditoria Completa**: Cada decisão e erro é persistido via LangGraph state persistence, permitindo auditoria e aprendizado.

## Arquitetura: LangChain + LangGraph + VCR

Deep Agents é composto por três camadas:

```text
Loop Principal (Deep Agents)
    |
    +-> LangChain (orquestração de tools, prompts, embeddings)
    |
    +-> LangGraph State Machine (estado imutável, persistência)
    |
    +-> VCR Policy Engine (validação local, < 10ms decisões)
```

### 1. LangChain Orchestration

LangChain gerencia:

- **Tool Registry**: Descoberta automática e binding de ferramentas disponíveis
- **Prompts e Templates**: Prompts estruturados para planejamento e execução
- **Memory Strategies**: Truncate, delete, summarize para gerenciar contexto
- **Output Parsing**: Extração estruturada de decisões e resultados

### 2. LangGraph State Machine

LangGraph implementa:

- **State Schema**: Tipagem forte de estado (typed AgentState)
- **Graph Topology**: Nós representam etapas; arestas representam transições
- **Persistence**: Snapshots de estado para auditoria e recuperação
- **Conditional Routing**: Decisões determinísticas baseadas em estado atual

### 3. VCR Policy Engine

VCR fornece:

- **Local Validation**: Cada decisão é validada por XLM-RoBERTa-small antes de execução
- **Sub-10ms Inference**: PyTorch quantizado (INT8) garante latência < 10ms p99
- **Recovery Strategies**: Políticas de recuperação quando precisão < 0.65
- **Confidence Scoring**: Cada ação tem score de confiança auditável

## Padrões de Execução

### Padrão 1: Single-Agent Planning-Execution

Um agente principal formula um plano e executa ferramentas sequencialmente:

```text
User Query
    |
    +-> Deep Agent (Planejamento com LLM)
    |
    +-> VCR Validação do Plano (< 10ms)
    |
    +-> LangGraph State: Execute Step 1
    |
    +-> Observe Resultado, Ajuste Plano
    |
    +-> Repeat até completion
    |
    +-> Return Response
```

### Padrão 2: Sub-Agent Delegation

Agente principal delega a sub-agentes especializados:

```text
Principal Agent (Planejamento)
    |
    +-> Delega a Sub-Agent 1 (Busca de Contexto via Context Engine)
    |
    +-> Delega a Sub-Agent 2 (Análise de Código)
    |
    +-> Delega a Sub-Agent 3 (Validação de Segurança)
    |
    +-> Aguarda resultados, Integra Respostas
```

## Métricas de Performance

Deep Agents monitora em cada iteração:

- **Planning Quality**: Alvo ≥ 0.85. Se cair, replanejar com contexto expandido.
- **Tool Success Rate**: Alvo ≥ 0.95. Ferramentas devem executar confiably.
- **VCR Confidence**: Alvo ≥ 0.70. Score de confiança da decisão local.
- **Total Latency P95**: Alvo < 2000ms para iteração completa.
- **Context Window Usage**: Monitorar % de tokens usados vs. disponível.

## External Linking

| Conceito          | Recurso                              | Link                                                                                                |
| ----------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------- |
| **LangChain**     | Framework de orquestração LLM        | [python.langchain.com/docs](https://python.langchain.com/docs)                                      |
| **LangGraph**     | State machine para agentic workflows | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/)                       |
| **Deep Agents**   | Planning e multi-step execution      | [github.com/langchain-ai/deep-agents](https://github.com/langchain-ai/deep-agents)                  |
| **ReAct Pattern** | Reasoning + Acting para agentes      | [arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)                                        |
| **Tool Use**      | LLM tool calling specification       | [openai.com/docs/guides/function-calling](https://platform.openai.com/docs/guides/function-calling) |

---

_Parte do ecossistema Vectora_ · [Open Source (MIT)](https://github.com/Kaffyn/Vectora) · [Contribuidores](https://github.com/Kaffyn/Vectora/graphs/contributors)
