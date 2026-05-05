---
title: "LangChain: Framework de Orquestração"
slug: "langchain"
description: "Framework unificado para construir agentes e chains com LLMs"
date: 2026-05-03
type: docs
sidebar:
  open: true
breadcrumbs: true
tags: ["langchain", "framework", "orchestration", "agents", "chains"]
---

{{< lang-toggle >}}

LangChain é um framework open-source que fornece uma arquitetura unificada para construir aplicações poderosas com LLMs. Ele simplifica o processo de desenvolvimento de agentes, chains e aplicações de busca-aumentada gerativa (RAG).

## O que é LangChain?

LangChain combina:

- **Runnables** - Abstrações compostas para chains e workflows
- **Tools** - Definição e execução de ferramentas para agentes
- **Memory** - Sistemas de memória para conversas multi-turn
- **Retrieval** - Integração com vector stores e busca vetorial
- **Agents** - Orquestração inteligente de ações baseada em LLM

## Arquitetura

LangChain fornece uma camada unificada sobre diferentes LLMs e ferramentas, permitindo que você construa aplicações complexas sem se preocupar com detalhes de implementação específicos de cada provedor.

```text
Application Layer
    ↓
LangChain Framework
    ↓
Runnables → Tools → Memory → Retrieval
    ↓
LLM Providers (Claude, OpenAI, etc)
    ↓
External Services
```

## Por que LangChain?

- **Provedor-agnóstico** — Funciona com qualquer LLM (Claude, OpenAI, local)
- **Composição flexível** — Combine chains e tools via LCEL
- **Ecosistema completo** — LangGraph, LangSmith, Deep Agents
- **Production-ready** — Ferramentas para observabilidade e debugging
- **Comunidade ativa** — Milhares de contribuições e exemplos

## Próximas Seções

- **[Conceitos Principais](core-concepts.pt.md)** - Runnables, Tools, Memory, Retrieval
- **[LangGraph](langgraph/)** - Agentes stateful com decision loops
- **[LangSmith](langsmith/)** - Observabilidade em produção
- **[Deep Agents](deep-agents/)** - Framework para tarefas complexas
- **[Padrões de Integração](integration-patterns.pt.md)** - VCR, Multi-LLM routing, Tool composition

## External Linking

| Conceito           | Recurso                | Link                                                                                                 |
| ------------------ | ---------------------- | ---------------------------------------------------------------------------------------------------- |
| LangChain Official | LangChain Home         | [https://www.langchain.com/](https://www.langchain.com/)                                             |
| LangChain Docs     | Official Documentation | [https://docs.langchain.com/](https://docs.langchain.com/)                                           |
| Python Reference   | API Reference          | [https://reference.langchain.com/python/langchain](https://reference.langchain.com/python/langchain) |
| GitHub             | LangChain Repository   | [https://github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain)               |
| Getting Started    | Tutorial Guide         | [https://docs.langchain.com/oss/python/langchain/](https://docs.langchain.com/oss/python/langchain/) |
