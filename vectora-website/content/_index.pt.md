---
title: Vectora
slug: vectora
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
breadcrumbs: true
tags:
  - agentic-framework
  - agents
  - ai
  - architecture
  - auth
  - claude
  - concepts
  - context-engine
  - embeddings
  - fastapi
  - jwt
  - lancedb
  - langchain
  - langgraph
  - mcp
  - mcp-protocol
  - postgresql
  - rag
  - rbac
  - redis
  - reranker
  - security
  - vector-search
  - vcr
  - vectora
  - voyage
  - xlm-roberta
---

{{< lang-toggle >}}

O **Vectora** é um **Hub de Conhecimento Local-First** que capacita agentes de IA a operarem com contexto governado, sem alucinações e com privacidade total. Construído com **FastAPI + LangChain + Deep Agents**, combina busca vetorial de alta performance (LanceDB + VoyageAI), análise cognitiva (VCR com PyTorch + XLM-RoBERTa) e orquestração de RAG para fornecer contexto preciso via REST/MCP/JSON-RPC.

> [!IMPORTANT] **Fórmula Central**: `Agente Especialista = LangChain + Deep Agents + VCR (PyTorch + XLM-RoBERTa) + Contexto Governado (LanceDB + PostgreSQL + Redis)`

## O Problema que o Vectora Resolve

A tabela abaixo descreve como o Vectora aborda as falhas comuns em agentes genéricos e seu impacto prático no desenvolvimento.

| Falha em Agentes Genéricos     | Impacto Prático                                                  | Como o Vectora Mitiga                                                                                       |
| ------------------------------ | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Contexto Raso**              | Busca por "autenticação" retorna 50 arquivos irrelevantes        | Reranker local (XLM-RoBERTa) filtra por relevância semântica real, não apenas similaridade de cosseno bruta |
| **Sem Validação Pré-Execução** | Chamadas de ferramentas perigosas rodam antes de serem auditadas | VCR intercepta, valida faithfulness e aplica recovery policy antes da execução                              |
| **Falta de Isolamento**        | Dados do projeto vazam entre sessões                             | RBAC de 5 níveis com 15 permissões validadas em tempo de execução                                           |
| **Consumo Imprevisível**       | LLMs geram excesso de dados, desperdiçando tokens em boilerplate | Context Engine aplica compactação head/tail e injeta apenas o que é relevante                               |
| **Privacidade**                | Código enviado para serviços externos sem controle               | LanceDB e XLM-RoBERTa rodam 100% local — nenhum vetor sai da máquina                                        |

## A Solução: Camada de Inteligência Local-First

O Vectora é exposto via **REST, MCP e JSON-RPC**. Ele opera como uma camada de pré-pensamento e governança, enriquecendo agentes com contexto preciso e artefatos de decisão estruturados.

```text
Agente Principal (Claude Code, Cursor, etc)
  |
  +-> REST / MCP / JSON-RPC
  |
  +-> FastAPI Backend
  |     -> VCR: Pré-Pensamento (PyTorch + XLM-RoBERTa, <10ms)
  |     -> Context Engine (embed + HNSW + rerank + compact)
  |
  +-> LanceDB (Vector Search, local)
  +-> VoyageAI (Embeddings API)
  +-> PostgreSQL + Redis (Metadata + Cache, local)
  |
  +-> LangChain + Deep Agents (Orchestration)
        -> Contexto Governado + Métricas
```

## Componentes Principais

O sistema é dividido em módulos especializados que garantem integridade, performance e segurança na recuperação de contexto.

| Módulo                                                                    | Responsabilidade                                                                  | Tecnologia                       |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------- |
| **[VCR: Vectora Cognitive Runtime](./models/vectora-cognitive-runtime/)** | Pré-pensamento: análise de intenção, reranking, validação de faithfulness (<10ms) | PyTorch + XLM-RoBERTa + LoRA     |
| **[FastAPI Backend](./backend/)**                                         | Servidor REST/MCP/JSON-RPC, auth JWT, RBAC, gestão de estado                      | FastAPI + Pydantic + asyncio     |
| **[LangChain + Deep Agents](./langchain/)**                               | Orchestração, planning engine, executor de ferramentas, memória                   | LangChain + LangGraph            |
| **[Context Engine](./core/context-engine/)**                              | Busca semântica, compactação, reranking local, validação VCR                      | LanceDB + VoyageAI + XLM-RoBERTa |
| **[Vector Storage](./backend/lancedb/)**                                  | Armazenamento vetorial nativo, índices HNSW, busca semântica rápida               | LanceDB (local-first)            |
| **[Metadata + Cache](./backend/postgresql/)**                             | Persistência de metadados, sessões, histórico, RBAC                               | PostgreSQL + Redis               |
| **[Protocols](./protocols/)**                                             | REST API, MCP server, JSON-RPC 2.0, ACP para integrações de editor                | HTTP, stdin/stdout, JSON-RPC     |

## Stack Tecnológico

O Vectora é construído com tecnologias **comprovadas, de código aberto** e otimizadas para **operação local-first** com máxima privacidade.

| Camada                          | Tecnologia                   | Razão                                                                    |
| ------------------------------- | ---------------------------- | ------------------------------------------------------------------------ |
| **Orquestração + Planejamento** | LangChain + LangGraph        | Abstração limpa sobre LLMs, planning nativo, estado persistido           |
| **Pré-Pensamento (VCR)**        | PyTorch + XLM-RoBERTa-small  | Inferência local (<10ms p99), LoRA fine-tuning, zero dependência de rede |
| **API Backend**                 | FastAPI (Python 3.12)        | Async nativo, validação Pydantic, REST/MCP/JSON-RPC em um servidor       |
| **Embeddings**                  | VoyageAI (voyage-4)          | 1024D, otimizado para código, $0.10/2M tokens                            |
| **Reranking Local**             | XLM-RoBERTa via VCR          | Cross-encoder (<10ms p99), zero chamadas externas                        |
| **Vector Storage**              | LanceDB                      | Nativo, sem servidor, índices HNSW, busca rápida, local-first            |
| **Dados Estruturados**          | PostgreSQL (pg8000)          | Metadados, sessões, histórico, RBAC, totalmente local                    |
| **Cache + Sessões**             | Redis                        | Cache de embeddings (24h TTL), rate limiting, sessões                    |
| **Frontend**                    | React 19 + TypeScript + Vite | Type-safe, performance, real-time updates via SSE                        |
| **CLI + TUI**                   | Python + Textual + pystray   | Acessível, intuitivo, system tray Windows                                |

> [!IMPORTANT] **Local-First, Privacy-Preserving**: O Vectora é designed para **rodar por completo no seu ambiente** — PostgreSQL, Redis, LanceDB, VCR são todos locais. **Seus dados ficam seus.** Sem envio para a nuvem (exceto chamadas opcionais a VoyageAI para embeddings).

## Fluxo de Operação

O processo de funcionamento do Vectora segue um fluxo rigoroso de validação e enriquecimento de contexto.

1. **Detecção**: O agente principal identifica a necessidade de contexto e dispara `vectora_search` via MCP ou REST.
2. **Pré-Pensamento (VCR)**: O VCR analisa a intent e decide a estratégia (auto / semantic / structural / hybrid) em < 8ms.
3. **Embedding**: A query é convertida em vetor 1024D via VoyageAI (ou cache Redis).
4. **Busca Vetorial**: LanceDB retorna top-100 candidatos via HNSW em < 50ms.
5. **Reranking**: XLM-RoBERTa reordena para top-10 por relevância real em < 10ms.
6. **Compactação**: head/tail trunca chunks grandes preservando assinatura e return.
7. **Validação**: VCR valida faithfulness >= 0.70 antes de entregar o contexto.
8. **Resposta Estruturada**: Contexto validado + métricas são retornados ao agente principal.

## Por onde começar?

Explore os guias abaixo para entender como integrar e operar o Vectora no seu dia a dia.

| Categoria         | Documento                                          | Descrição                                  |
| ----------------- | -------------------------------------------------- | ------------------------------------------ |
| **Início Rápido** | [Primeiros Passos](./getting-started/)             | Instalação, setup VoyageAI, integração MCP |
| **Core**          | [Deep Agents Framework](./core/agentic-framework/) | LangChain + LangGraph + VCR                |
| **Search**        | [Pipeline de Busca](./search/)                     | VoyageAI + LanceDB HNSW + XLM-RoBERTa      |
| **Backend**       | [Banco de Dados](./backend/)                       | PostgreSQL + Redis + LanceDB               |
| **Auth**          | [Autenticação](./auth/)                            | JWT HS256 + RBAC 5 níveis                  |
| **Protocolos**    | [REST / MCP / JSON-RPC](./protocols/)              | Todos os endpoints e integrações           |
| **Segurança**     | [Modelo de Segurança](./security/)                 | Privacidade local-first, injeção, RBAC     |
| **CLI**           | [Interface de Linha de Comando](./cli/)            | Typer, TUI Textual, system tray            |
| **Frontend**      | [React 19 + TypeScript](./frontend/)               | SPA com TanStack Query + streaming SSE     |

## Guia de Navegação

Acesse as seções principais da documentação para aprofundar seu conhecimento.

- [**Primeiros Passos**](./getting-started/) — Instalação, setup e integração MCP.
- [**Core**](./core/) — Deep Agents Framework, Context Engine, VCR.
- [**Search**](./search/) — Embeddings, vector search, reranking local.
- [**Backend**](./backend/) — PostgreSQL, Redis, LanceDB.
- [**Auth**](./auth/) — JWT, RBAC.
- [**Protocolos**](./protocols/) — REST API, MCP, JSON-RPC, ACP.
- [**Segurança**](./security/) — Privacidade, injeção, RBAC.
- [**LangChain**](./langchain/) — Integração LangChain, RAG, chains.
- [**Modelos**](./models/) — VCR (XLM-RoBERTa), VoyageAI.
- [**CLI**](./cli/) — Interface de linha de comando e TUI.
- [**Testing**](./testing/) — pytest, integração, E2E, performance.
- [**DevOps**](./devops/) — Docker, Jenkins CI/CD.

## External Linking

| Conceito        | Recurso                              | Link                                                                                   |
| --------------- | ------------------------------------ | -------------------------------------------------------------------------------------- |
| **LangChain**   | LangChain documentation              | [python.langchain.com](https://python.langchain.com/)                                  |
| **LanceDB**     | Vector database local                | [lancedb.com/docs](https://lancedb.com/docs)                                           |
| **VoyageAI**    | High-performance embeddings          | [voyageai.com](https://www.voyageai.com/)                                              |
| **MCP**         | Model Context Protocol specification | [modelcontextprotocol.io/specification](https://modelcontextprotocol.io/specification) |
| **XLM-RoBERTa** | Multilingual transformer model       | [huggingface.co/xlm-roberta-small](https://huggingface.co/xlm-roberta-small)           |
