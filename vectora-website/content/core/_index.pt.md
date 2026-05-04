---
title: "Core: Sistema Inteligente do Vectora"
slug: core
date: 2026-05-03T23:00:00-03:00
type: docs
sidebar:
  open: true
tags:
  - langchain
  - deep-agents
  - vcr
  - agentic-framework
  - ai
  - architecture
  - concepts
  - context-engine
  - core
  - lancedb
  - state
  - system
  - vectora
draft: false
---

{{< lang-toggle >}}

{{< section-toggle >}}

O Core é o coração inteligente do Vectora. Ele contém os componentes que tornam o Vectora um agente especialista auto-corrigível, capaz de raciocínio profundo, busca de contexto governada e inferência local segura.

Ao integrar LangChain com Deep Agents, orquestração de raciocínio avançado com uma profunda consciência de contexto, o Core garante que cada interação seja fundamentada na realidade da sua base de código, executada localmente e sem alucinações.

## Componentes Principais

A inteligência do Vectora é construída sobre três motores principais que trabalham em conjunto para fornecer insights precisos e acionáveis.

### Deep Agents Framework

O sistema nervoso distribuído do Vectora, construído sobre LangChain e LangGraph. Uma máquina de estado que executa planejamento multi-etapas, chaining de ferramentas e recuperação automática de falhas. Deep Agents orquestra a sequência de ações; FastAPI executa as ações no backend.

**Saiba como**: [Ver Deep Agents Framework](./agentic-framework.md)

### Context Engine

O curador inteligente de contexto do Vectora, um pipeline de 5 etapas que decide o quê, como e quando buscar contexto no codebase. Usa LanceDB para busca semântica, VoyageAI para embeddings e XLM-RoBERTa local para reranking. Filtra ruído e evita o excesso de dados (overfetch).

**Saiba como**: [Ver Context Engine](./context-engine.md)

### Vectora Cognitive Runtime (VCR)

O cérebro tático do Core, uma camada de inferência local baseada em PyTorch + XLM-RoBERTa-small com LoRA fine-tuning. VCR orquestra a política de decisão entre Deep Agents e Context Engine, garantindo que cada ação seja segura, auditável e livre de alucinações. Latência < 10ms p99 em CPU.

**Saiba como**: [Ver Vectora Cognitive Runtime](../models/vectora-cognitive-runtime.md)

## Como Trabalham Juntos

Deep Agents formula o plano de execução usando LangChain, enquanto o Context Engine fornece o contexto governado em tempo real via LanceDB. VCR valida cada etapa localmente com PyTorch. Juntos, transformam consultas simples em respostas precisas e modificações de código confiáveis, tudo sem sair da máquina local.

## External Linking

| Conceito        | Recurso                                           | Link                                                                               |
| --------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **LangChain**   | Framework de orquestração LLM                     | [python.langchain.com/docs](https://python.langchain.com/docs)                     |
| **LangGraph**   | State machine para multi-etapa workflows          | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/)      |
| **Deep Agents** | Framework de planejamento e execução multi-etapas | [github.com/langchain-ai/deep-agents](https://github.com/langchain-ai/deep-agents) |
| **LanceDB**     | Vector database local de código aberto            | [lancedb.com/docs](https://lancedb.com/docs)                                       |
| **PyTorch**     | Framework de deep learning para VCR               | [pytorch.org/docs](https://pytorch.org/docs)                                       |

---

_Parte do ecossistema Vectora_ · [Open Source (MIT)](https://github.com/Kaffyn/Vectora) · [Contribuidores](https://github.com/Kaffyn/Vectora/graphs/contributors)
