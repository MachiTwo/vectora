---
title: MCP
slug: mcp
date: "2026-04-18T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - ai
  - architecture
  - auth
  - claude
  - concepts
  - context-engine
  - embeddings
  - fastapi
  - jwt
  - mcp
  - mcp-protocol
  - protocol
  - rag
  - reranker
  - security
  - tools
  - vector-search
  - vectora
  - voyage
---

{{< lang-toggle >}}

O Vectora expõe ferramentas via MCP (Model Context Protocol) para integração com editores de IA (Claude Code, JetBrains, Zed). MCP é um dos três protocolos suportados — junto com REST API e JSON-RPC 2.0. Este documento descreve como o Vectora implementa MCP e como IDEs se integram.

## O que é MCP?

**MCP** é um protocolo aberto que permite que LLMs (Large Language Models) chamar "ferramentas" de um computador. Diferente de APIs REST genéricas, MCP é otimizado para:

- **Tool Discovery**: IDE descobre quais ferramentas estão disponíveis
- **Structured I/O**: Schemas JSON para garantir validação
- **Error Handling**: Respostas estruturadas com retry automático
- **Capability Negotiation**: Client/server acordam em features

```text
┌─────────────┐
│ IDE │ (Claude Code, Cursor, etc)
│ (MCP Client)
└──────┬──────┘
       │ {"jsonrpc": "2.0", "method": "resources/list"}
       ▼
┌──────────────────────────┐
│ Vectora MCP Server │
│ (mcp service running) │
│ │
│ • Tool: search_context │
│ • Tool: analyze_file │
│ • Tool: find_references │
└──────────────────────────┘
       ▲
       │ {"result": [...], "tools": [...]}
       │
```

## Por Que Vectora Usa MCP?

| Alternativa               | Problema                                         | Como MCP Resolve                        |
| ------------------------- | ------------------------------------------------ | --------------------------------------- |
| **REST API**              | SDK em cada IDE, configuração complexa           | MCP é nativo em Claude Code/Cursor      |
| **CLI Tool**              | Sem context compartilhado entre IDE e ferramenta | MCP mantém state entre chamadas         |
| **Subprocess**            | Lento, sem structured output                     | MCP é eficiente + JSON nativo           |
| **LSP (Language Server)** | Projetado para autocompletar, não IA             | MCP é genérico para qualquer ferramenta |

**Resultado**: Uma IDE (Claude Code) ↔ Múltiplos MCPs (Vectora, pytest, git, file-system).

## Arquitetura Vectora MCP

Vectora implementa MCP com uma stack clara: cliente MCP no IDE se conecta ao servidor Vectora via STDIO, que orquestra Agentic Framework, Context Engine e Tool Executor.

## Components

```text
IDE (Claude Code)
    │
    └─→ MCP Client (built-in)
         │
         ├─→ STDIO Transport (pipe)
         │
         └─→ Vectora MCP Server
              │
              ├─→ Agentic Framework (validação)
              │ ├─→ Guardian (segurança)
              │ └─→ Preconditions (verificação)
              │
              ├─→ Context Engine (busca)
              │ ├─→ Embeddings (VoyageAI voyage-4)
              │ ├─→ Search (LanceDB HNSW)
              │ └─→ Reranking (XLM-RoBERTa local)
              │
              └─→ Tool Executor
                   ├─→ search_context
                   ├─→ analyze_file
                   ├─→ find_references
                   └─→ ... (12 tools total)
```

## Transport

Vectora MCP usa **STDIO** (stdin/stdout pipes):

```bash
"mcp": {
  "vectora": {
    "command": "vectora",
    "args": ["mcp", "--stdio"]
  }
}

# Vectora inicia com:
# STDIN ← mensagens JSON do IDE
# STDOUT → respostas JSON de Vectora
```

## Protocol Flow

O fluxo MCP em Vectora passa por três fases: inicialização onde IDE e servidor negoceiam capacidades, descoberta de ferramentas disponíveis, e execução de tools com tratamento de erros.

## 1. Inicialização

```json
// IDE envia
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "claude-code",
      "version": "1.0.0"
    }
  }
}

// Vectora responde
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {} // Ferramentas disponíveis
    },
    "serverInfo": {
      "name": "vectora",
      "version": "0.8.0"
    }
  }
}
```

## 2. Tool Discovery

```json
// IDE pede lista de tools
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}

// Vectora lista (exemplo simplificado)
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "search_context",
        "description": "Busca semântica em codebase",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": {"type": "string"},
            "top_k": {"type": "integer", "default": 10}
          }
        }
      },
      // ... mais tools
    ]
  }
}
```

## 3. Tool Execution

```json
// IDE chama tool
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "search_context",
    "arguments": {
      "query": "Como validar tokens JWT?",
      "top_k": 5
    }
  }
}

// Vectora executa (passa por Agentic Framework + Guardian)
// Retorna resultado
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Encontrei 5 chunks relevantes..."
      },
      {
        "type": "text",
        "text": "[JSON com chunks, metadata, precisão]"
      }
    ]
  }
}
```

## Vectora MCP Tools (12 Total)

| Tool               | Input              | Output                      | Latência SLA |
| ------------------ | ------------------ | --------------------------- | ------------ |
| `search_context`   | query, top_k       | chunks, precision           | <300ms       |
| `analyze_file`     | file_path          | structure, imports, exports | <200ms       |
| `find_references`  | symbol_name        | call sites, types           | <250ms       |
| `file_summary`     | file_path          | summary, key functions      | <150ms       |
| `list_workspace`   | filter (opt)       | files, structure            | <100ms       |
| `get_dependencies` | file_path          | direct, indirect deps       | <200ms       |
| `analyze_changes`  | file_paths[]       | impact analysis             | <400ms       |
| `validate_imports` | file_paths[]       | validation results          | <300ms       |
| `search_by_type`   | type_name          | usages of type              | <250ms       |
| `get_config`       | key (opt)          | config value                | <50ms        |
| `index_status`     | none               | status, size, chunks        | <100ms       |
| `execute_query`    | query_type, params | generic query               | <500ms       |

Ver [MCP Tools Reference](../reference/mcp-tools.md) para detalhes completos.

## Configuração no IDE

Cada IDE tem um processo diferente para configurar MCP servers. Abaixo estão os exemplos para as plataformas mais usadas.

## Claude Code (Recomendado)

```json
// ~/.claude/claude_desktop_config.json
{
  "mcpServers": {
    "vectora": {
      "command": "vectora",
      "args": ["mcp", "--stdio"]
    }
  }
}
```

## Cursor

```json
// .cursor/settings.json
{
  "mcp": {
    "vectora": {
      "command": "vectora",
      "args": ["mcp", "--stdio"],
      "env": {
        "VECTORA_NAMESPACE": "meu-projeto"
      }
    }
  }
}
```

## Zed

```json
// .zed/settings.json
{
  "language_servers": {
    "vectora": {
      "binary": {
        "path": "vectora"
      },
      "initialization_options": {
        "namespace": "meu-projeto"
      }
    }
  }
}
```

## Tratamento de Erros

MCP define erros estruturados:

```json
// Tool falha com erro
{
  "jsonrpc": "2.0",
  "id": 3,
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "error_code": "NAMESPACE_NOT_FOUND",
      "detail": "Namespace 'invalid' não existe"
    }
  }
}
```

Códigos de erro Vectora:

- `NAMESPACE_NOT_FOUND` (404)
- `AUTHENTICATION_FAILED` (401)
- `RATE_LIMIT_EXCEEDED` (429)
- `INVALID_SCHEMA` (400)
- `TIMEOUT` (504)
- `INTERNAL_ERROR` (500)

## Performance & Otimizações

Vectora implementa várias técnicas para manter latência baixa e escalabilidade alta: streaming para respostas grandes, caching de resultados frequentes, e batch processing.

## Streaming (Para respostas grandes)

MCP suporta streaming de tool results:

```json
// Chunked response
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      { "type": "text", "text": "Chunk 1...", "partial": true },
      { "type": "text", "text": "Chunk 2...", "partial": true },
      { "type": "text", "text": "Chunk 3...", "partial": false } // fim
    ]
  }
}
```

## Caching

Vectora cacheia resultados de busca:

```text
Client: search_context("Como validar tokens?")
  ↓ (primeira vez)
Server: Processa + Retorna + **Cacheia com TTL 5min**
  ↓ (segunda vez, mesma query em 5min)
Server: Retorna do cache (0ms vs 230ms)
```

## Batch Calls

IDE pode fazer múltiplas chamadas em paralelo:

```json
[
  {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "search_context", "arguments": {...}}},
  {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "analyze_file", "arguments": {...}}},
  {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "find_references", "arguments": {...}}}
]
```

## Debug & Logging

Para entender o que está acontecendo entre IDE e Vectora, use o MCP Inspector ou active logging estruturado. Ambos ajudam a diagnosticar problemas de integração.

## MCP Inspector

```bash
# Ver mensagens MCP em tempo real
# (IDE + Vectora)
vectora mcp --debug

# Saída:
# [MCP] Client → Server: {"jsonrpc": "2.0", "method": "initialize", ...}
# [MCP] Server → Client: {"jsonrpc": "2.0", "result": {...}, ...}
# [MCP] Tool call: search_context | Query: "..." | Time: 234ms
```

## Estrutura de Logs

```yaml
# logs/mcp.log (JSON)
{
  "timestamp": "2026-04-19T10:30:45Z",
  "level": "INFO",
  "event": "tool_executed",
  "tool_name": "search_context",
  "tool_duration_ms": 234,
  "error_code": null,
  "precision": 0.87,
  "chunks_returned": 5,
}
```

## Comparação: MCP vs Alternativas

| Aspecto         | MCP                      | REST API              | LSP           |
| --------------- | ------------------------ | --------------------- | ------------- |
| **Setup**       | Automático em IDE        | Config manual         | Config manual |
| **Discovery**   | Dinâmico (tools/list)    | Documentação estática | Estático      |
| **State**       | Persistente (session)    | Stateless             | Stateless     |
| **Latência**    | <10ms IPC                | >100ms network        | <50ms IPC     |
| **Suporte IDE** | Claude Code, Cursor, Zed | Todas                 | Algumas       |

**Conclusão**: MCP é ideal para ferramentas que precisam de contexto persistente + discovery.

## External Linking

| Conceito              | Recurso                              | Link                                                                                   |
| --------------------- | ------------------------------------ | -------------------------------------------------------------------------------------- |
| **MCP**               | Model Context Protocol Specification | [modelcontextprotocol.io/specification](https://modelcontextprotocol.io/specification) |
| **Anthropic Claude**  | Claude Documentation                 | [docs.anthropic.com](https://docs.anthropic.com/)                                      |
| **LanceDB**           | Vector database local                | [lancedb.com/docs](https://lancedb.com/docs)                                           |
| **VoyageAI**          | High-performance embeddings for RAG  | [voyageai.com](https://www.voyageai.com/)                                              |
| **Voyage Embeddings** | Voyage Embeddings Documentation      | [docs.voyageai.com/docs/embeddings](https://docs.voyageai.com/docs/embeddings)         |
