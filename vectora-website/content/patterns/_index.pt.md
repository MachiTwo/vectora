---
title: "Patterns: Paradigmas Arquiteturais"
slug: patterns
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - ai
  - architecture
  - concepts
  - langchain
  - langgraph
  - patterns
  - rag
  - sub-agents
  - trace
  - vcr
  - vectora
draft: false
---

{{< lang-toggle >}}

{{< section-toggle >}}

Os padrões operacionais do Vectora definem como os componentes do ecossistema se combinam para resolver problemas de engenharia com IA. Cada padrão é orquestrado pelo VCR (Vectora Cognitive Runtime) e executado via LangChain + LangGraph.

## Padrões Disponíveis

O VCR decide em tempo real qual padrão aplicar com base na query, no contexto disponível e na estratégia configurada (auto, semantic, structural, hybrid).

### RAG Conectado

RAG Conectado vai além da recuperação simples. Integra um pipeline de 5 etapas — embed (VoyageAI) → busca vetorial (LanceDB HNSW) → reranking (XLM-RoBERTa local) → compactação → validação (VCR) — garantindo que o contexto entregue ao LLM seja preciso e verificado contra o codebase real.

**[Ver RAG Conectado](./rag.md)**

### Sub-Agents

Sub-Agents implementa delegação controlada via LangGraph. O agente principal (orchestrator) decompõe tarefas complexas e delega sub-tarefas para agentes especializados com autoridade limitada, mantendo trilha de auditoria completa via ACP (Agent Communication Protocol).

**[Ver Sub-Agents](./sub-agents.md)**

### Trace

Trace é o sistema de observabilidade estruturada de execuções agênticas. Captura cada tool call, mudança de contexto, score do VCR e decisão do LangGraph state machine em formato estruturado para debugging e auditoria.

**[Ver Trace](./trace.md)**

## Matriz de Uso

| Padrão            | Caso de Uso                            | Orchestrador             |
| ----------------- | -------------------------------------- | ------------------------ |
| **RAG Conectado** | Busca e geração com contexto de código | VCR + LangChain          |
| **Sub-Agents**    | Tarefas multi-domínio (review + teste) | LangGraph state machine  |
| **Trace**         | Debugging e auditoria de decisões      | VCR metrics + Prometheus |

## External Linking

| Conceito          | Recurso                                 | Link                                                                                                    |
| ----------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **RAG**           | Retrieval-Augmented Generation          | [arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)                                            |
| **LangGraph**     | Stateful agent orchestration            | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/)                           |
| **OpenTelemetry** | Distributed tracing concepts            | [opentelemetry.io/docs/concepts/signals/traces](https://opentelemetry.io/docs/concepts/signals/traces/) |
| **ReAct**         | Reasoning and Acting in language models | [arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)                                            |
