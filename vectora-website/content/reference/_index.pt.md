---
title: "Referência: APIs, CLI e Configuração"
slug: reference
date: "2026-05-04T10:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - api
  - cli
  - config
  - fastapi
  - jwt
  - mcp
  - rbac
  - reference
  - rest
  - vectora
draft: false
---

{{< lang-toggle >}}

{{< section-toggle >}}

Referência rápida dos endpoints REST, ferramentas MCP, comandos CLI e chaves de configuração do Vectora.

## REST API

Todos os endpoints requerem `Authorization: Bearer <access_token>` exceto `/auth/login` e `/health`.

### Autenticação

| Método | Endpoint        | Permissão   | Descrição               |
| ------ | --------------- | ----------- | ----------------------- |
| `POST` | `/auth/login`   | Pública     | Login com email + senha |
| `POST` | `/auth/refresh` | Pública     | Renovar access token    |
| `POST` | `/auth/logout`  | Autenticado | Revogar token atual     |

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@empresa.com", "password": "senha"}'

# Resposta
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Busca e Contexto

| Método | Endpoint                    | Permissão        | Latência SLA  |
| ------ | --------------------------- | ---------------- | ------------- |
| `POST` | `/api/v1/search`            | `search:execute` | < 500ms p95   |
| `POST` | `/api/v1/agent/run`         | `agent:execute`  | < 30s         |
| `GET`  | `/api/v1/agent/stream/{id}` | `agent:execute`  | SSE streaming |

```bash
# Busca semântica
curl -X POST http://localhost:8000/api/v1/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "validar JWT", "namespace": "src/auth", "top_k": 10}'
```

### Indexação

| Método   | Endpoint                    | Permissão      | Descrição         |
| -------- | --------------------------- | -------------- | ----------------- |
| `POST`   | `/api/v1/index`             | `index:write`  | Indexar codebase  |
| `DELETE` | `/api/v1/index/{namespace}` | `index:delete` | Remover namespace |
| `GET`    | `/api/v1/index/status`      | `index:read`   | Status do índice  |

### Admin

| Método   | Endpoint                 | Permissão     | Descrição       |
| -------- | ------------------------ | ------------- | --------------- |
| `GET`    | `/admin/users`           | `admin:read`  | Listar usuários |
| `POST`   | `/admin/users`           | `admin:write` | Criar usuário   |
| `PUT`    | `/admin/users/{id}/role` | `admin:write` | Alterar role    |
| `DELETE` | `/admin/users/{id}`      | `admin:write` | Remover usuário |

### Saúde e Métricas

| Método | Endpoint   | Permissão    | Descrição                    |
| ------ | ---------- | ------------ | ---------------------------- |
| `GET`  | `/health`  | Pública      | Health check básico          |
| `GET`  | `/ready`   | Pública      | Readiness check (DB + Redis) |
| `GET`  | `/metrics` | `admin:read` | Métricas Prometheus          |

## MCP Tools (12 ferramentas)

| Tool               | Input                         | Output                      | SLA     |
| ------------------ | ----------------------------- | --------------------------- | ------- |
| `search_context`   | `query`, `top_k`, `namespace` | chunks, precision           | < 300ms |
| `analyze_file`     | `file_path`                   | structure, imports, exports | < 200ms |
| `find_references`  | `symbol_name`                 | call sites, types           | < 250ms |
| `file_summary`     | `file_path`                   | summary, key functions      | < 150ms |
| `list_workspace`   | `filter` (opt)                | files, structure            | < 100ms |
| `get_dependencies` | `file_path`                   | direct, indirect deps       | < 200ms |
| `analyze_changes`  | `file_paths[]`                | impact analysis             | < 400ms |
| `validate_imports` | `file_paths[]`                | validation results          | < 300ms |
| `search_by_type`   | `type_name`                   | usages of type              | < 250ms |
| `get_config`       | `key` (opt)                   | config value                | < 50ms  |
| `index_status`     | none                          | status, size, chunks        | < 100ms |
| `execute_query`    | `query_type`, `params`        | generic query               | < 500ms |

### Configurar MCP no Claude Code

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

## CLI — Comandos

### Instalação e Configuração

```bash
uv tool install vectora
vectora config set voyage_api_key sk-voyage-xxx
vectora config set namespace meu-projeto
vectora config list
```

### Busca

```bash
vectora search "validar JWT"
vectora search "validar JWT" --namespace src/auth --top-k 5
vectora search "validar JWT" --verbose       # exibe scores e latências
```

### Indexar Codebase

```bash
vectora index .                             # indexar diretório atual
vectora index ./src --namespace src         # namespace específico
vectora index status                        # ver chunks e namespaces
vectora index drop --namespace meu-projeto  # remover namespace
vectora index rebuild                       # recriar índice HNSW
```

### Agente

```bash
vectora agent run "Explique o fluxo de autenticação"
vectora agent stream "Refatore auth.py"     # output SSE em tempo real
```

### Servidor

```bash
vectora serve                               # inicia FastAPI (porta 8000)
vectora serve --port 9000 --workers 4
vectora mcp --stdio                         # inicia MCP server
```

### Auth e Admin

```bash
vectora auth login --email dev@empresa.com
vectora auth token --show
vectora admin create-user --email admin@empresa.com --role superadmin
vectora admin list-users
vectora admin set-role --email dev@empresa.com --role operator
```

### Diagnóstico

```bash
vectora health                              # status de todos os componentes
vectora vcr status                          # modelo XLM-RoBERTa + latência
vectora vcr download                        # baixar modelo VCR
```

## Chaves de Configuração

| Chave                | Padrão                                       | Descrição                                       |
| -------------------- | -------------------------------------------- | ----------------------------------------------- |
| `voyage_api_key`     | —                                            | Chave VoyageAI (obrigatória)                    |
| `namespace`          | `default`                                    | Namespace padrão para indexação                 |
| `chunk_size`         | `512`                                        | Tokens por chunk de indexação                   |
| `chunk_overlap`      | `64`                                         | Sobreposição entre chunks                       |
| `top_k`              | `10`                                         | Resultados retornados por busca                 |
| `vcr_device`         | `cpu`                                        | Dispositivo VCR (`cpu` ou `cuda`)               |
| `embedding_provider` | `voyageai`                                   | Provedor de embeddings                          |
| `auto_refresh`       | `false`                                      | Renovação automática de tokens                  |
| `log_level`          | `info`                                       | Nível de log (`debug`, `info`, `warn`, `error`) |
| `redis_url`          | `redis://localhost:6379`                     | URL do Redis                                    |
| `postgres_url`       | `postgresql://vectora:...@localhost/vectora` | URL do PostgreSQL                               |

## RBAC — Roles e Permissões

| Permissão        | viewer | developer | operator | admin | superadmin |
| ---------------- | :----: | :-------: | :------: | :---: | :--------: |
| `search:execute` |        |     x     |    x     |   x   |     x      |
| `search:read`    |   x    |     x     |    x     |   x   |     x      |
| `agent:execute`  |        |     x     |    x     |   x   |     x      |
| `index:read`     |   x    |     x     |    x     |   x   |     x      |
| `index:write`    |        |           |    x     |   x   |     x      |
| `index:delete`   |        |           |    x     |   x   |     x      |
| `admin:read`     |        |           |          |   x   |     x      |
| `admin:write`    |        |           |          |   x   |     x      |
| `config:read`    |        |           |    x     |   x   |     x      |
| `config:write`   |        |           |          |   x   |     x      |

## External Linking

| Conceito              | Recurso                   | Link                                                                                   |
| --------------------- | ------------------------- | -------------------------------------------------------------------------------------- |
| **FastAPI**           | Python web framework docs | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)                                  |
| **MCP Specification** | Model Context Protocol    | [modelcontextprotocol.io/specification](https://modelcontextprotocol.io/specification) |
| **JWT RFC 7519**      | JSON Web Token standard   | [datatracker.ietf.org/doc/html/rfc7519](https://datatracker.ietf.org/doc/html/rfc7519) |
| **VoyageAI**          | Embeddings API reference  | [docs.voyageai.com/docs/embeddings](https://docs.voyageai.com/docs/embeddings)         |
| **LanceDB**           | Vector database docs      | [lancedb.com/docs](https://lancedb.com/docs)                                           |
