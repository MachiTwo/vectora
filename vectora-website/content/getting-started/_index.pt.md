---
title: "Começando com Vectora"
description: "Guia de instalação, configuração local e primeira integração com Vectora"
slug: "getting-started"
tags:
  - guide
  - installation
  - setup
  - quickstart
  - fastapi
  - python
  - local-first
date: 2026-05-03
weight: 2
---

{{< lang-toggle >}}

{{< section-toggle >}}

Vectora é um **Hub de Conhecimento Local-First** construído em Python 3.10+. Você pode executá-lo localmente em sua máquina com dependências mínimas (FastAPI, LanceDB, PostgreSQL e Redis embutidos).

## O Que Você Vai Instalar

- **Backend FastAPI**: APIs REST + MCP + JSON-RPC em Python
- **Vector Database (LanceDB)**: Busca semântica local, sem servidor externo
- **Cognitive Runtime (VCR)**: Inferência XLM-RoBERTa < 10ms no CPU
- **CLI + TUI**: Interface de linha de comando com textual (opcional)
- **System Tray**: Integração com bandeja do Windows (opcional)

Tudo roda **localmente** — nenhum dados é enviado para a nuvem.

## Pré-requisitos

Você precisa de:

- **Python 3.10+** (obrigatório)
- **uv** (gerenciador de pacotes rápido, recomendado)
- **Docker** (opcional, para containerização)
- **Git** (para clonar o repositório)

## Três Caminhos de Instalação

### 1. Instalação Local (Rápido, Recomendado)

Instale Vectora na sua máquina local com `uv`. Leva menos de 2 minutos.

**[-> Ver Guia de Instalação Local](./installation.md)**

### 2. Docker (Containerizado)

Rode Vectora em um container Docker com PostgreSQL, Redis e LanceDB pré-configurados.

**[-> Ver Guia de Deployment com Docker](./local-deployment.md)**

### 3. Primeira Integração

Após instalar, integre Vectora com seu editor de código via REST API, MCP ou JSON-RPC.

**[-> Ver Guia de Primeira Integração](./first-integration.md)**

## Próximos Passos

1. **Escolha um caminho de instalação** (recomendamos Local ou Docker)
2. **Configure suas credenciais** (VoyageAI para embeddings, opcionalmente LLM externo)
3. **Teste o servidor HTTP**: `http://localhost:8000/health`
4. **Explore a CLI**: `vectora --help`
5. **Integre com seu editor**: VS Code, JetBrains ou Zed

## Arquitetura Rápida

```text
Seu Código
  |
  +-> Vectora CLI / API (FastAPI)
      |
      +-> Deep Agents (Planejamento LLM)
      |
      +-> Context Engine (LanceDB busca)
      |
      +-> VCR (Validação XLM-RoBERTa)
      |
      +-> LLM Externo (opcional: Claude, GPT-4, etc)
```

## Recursos Principais

- **Local-First**: Toda a inferência ocorre na sua máquina
- **Privacy-Preserving**: Sem dados em servidores remotos
- **Fast**: VCR < 10ms p99, RAG < 500ms p99
- **Open Source**: MIT license, comunidade-driven

## Troubleshooting Rápido

Se encontrar problemas durante a instalação, consulte:

- **"Python 3.10 não encontrado"**: Instale Python de [python.org](https://www.python.org/downloads/)
- **"uv command not found"**: Instale uv via `pip install uv` ou `pipx install uv`
- **"Erro de permissão no Windows"**: Execute o terminal como administrador
- **Mais problemas**: Ver seção de [troubleshooting](../troubleshooting/)

## External Linking

| Conceito    | Recurso                           | Link                                                           |
| ----------- | --------------------------------- | -------------------------------------------------------------- |
| **Python**  | Python Official                   | [python.org/downloads](https://www.python.org/downloads/)      |
| **uv**      | Rust-based Python package manager | [astral.sh/blog/uv](https://astral.sh/blog/uv)                 |
| **FastAPI** | Modern Python web framework       | [fastapi.tiangolo.com](https://fastapi.tiangolo.com)           |
| **LanceDB** | Vector database local             | [lancedb.com/docs](https://lancedb.com/docs)                   |
| **Docker**  | Container platform                | [docker.com/get-started](https://docs.docker.com/get-started/) |
