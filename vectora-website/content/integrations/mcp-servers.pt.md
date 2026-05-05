---
title: MCP Servers
slug: mcp-servers
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - mcp
  - model-context-protocol
  - claude
  - integration
  - vectora
---

{{< lang-toggle >}}

Vectora fornece um **MCP Server** que permite conectar Vectora diretamente com Claude Desktop, agentes Claude e outras aplicações que suportam o Model Context Protocol.

## O que é MCP?

O **Model Context Protocol (MCP)** é um protocolo padrão que permite LLMs acessar ferramentas e dados de forma segura e eficiente. Com o MCP Server do Vectora, Claude e outros LLMs podem:

- Buscar documentação em tempo real
- Indexar repositórios de código
- Gerenciar buckets
- Executar operações RAG sem latência

## Instalação do MCP Server

### Via Package Manager

```bash
# npm
npm install -g @vectora/mcp-server

# pip
pip install vectora-mcp-server

# go
go install github.com/vectora-io/vectora-mcp-server@latest
```

### Via Docker

```bash
docker run -e VECTORA_API_KEY=vec_... vectora-io/mcp-server:latest
```

## Configuração no Claude Desktop

### 1. Localizar arquivo de configuração

```text
Windows: %APPDATA%\Claude\claude_desktop_config.json
macOS: ~/Library/Application\ Support/Claude/claude_desktop_config.json
Linux: ~/.config/Claude/claude_desktop_config.json
```

### 2. Adicionar MCP Server

```json
{
  "mcpServers": {
    "vectora": {
      "command": "vectora-mcp-server",
      "env": {
        "VECTORA_API_KEY": "vec_your_key_here"
      }
    }
  }
}
```

### 3. Reiniciar Claude Desktop

Após salvar a configuração, reinicie o Claude Desktop e o MCP Server estará disponível.

## Usando Vectora no Claude

Uma vez configurado, você pode usar Vectora naturalmente em conversas:

```text
Usuário: "Buscar documentação sobre autenticação JWT"

Claude pode então:
- Fazer busca em seus buckets
- Recuperar código relevante
- Fornecer resposta contextualizada
```

## Ferramentas Disponíveis no MCP

### search

Buscar documentos em um bucket.

```python
search(
    query: str,
    bucket_id: str,
    top_k: int = 5,
    filters: Optional[Dict] = None,
) -> List[SearchResult]
```

### index

Indexar documentos em um bucket.

```python
index(
    bucket_id: str,
    documents: List[Document],
) -> IndexResult
```

### list_buckets

Listar todos os buckets do usuário.

```python
list_buckets() -> List[Bucket]
```

### get_bucket

Obter detalhes de um bucket específico.

```python
get_bucket(bucket_id: str) -> Bucket
```

### create_bucket

Criar novo bucket.

```python
create_bucket(
    name: str,
    is_public: bool = False,
    description: Optional[str] = None,
) -> Bucket
```

## Exemplos de Uso

### Busca Simples

```text
"Buscar em meu bucket de documentação por 'autenticação'"
```

Claude usa a ferramenta `search` automaticamente.

### Indexação de Repositório

```text
"Indexar os arquivos Python em ./src no bucket 'codebase'"
```

Claude usa a ferramenta `index` para adicionar documentos.

### Gerenciamento de Buckets

```text
"Listar meus buckets e criar um novo chamado 'project-alpha'"
```

Claude usa `list_buckets` e `create_bucket`.

## Configuração Avançada

### Custom Endpoint

```json
{
  "mcpServers": {
    "vectora": {
      "command": "vectora-mcp-server",
      "args": ["--base-url", "https://custom.vectora.dev"],
      "env": {
        "VECTORA_API_KEY": "vec_..."
      }
    }
  }
}
```

### Logging e Debug

```json
{
  "mcpServers": {
    "vectora": {
      "command": "vectora-mcp-server",
      "env": {
        "VECTORA_API_KEY": "vec_...",
        "LOG_LEVEL": "debug"
      }
    }
  }
}
```

## Segurança

### API Key Management

- Nunca commit API keys no Git
- Use variáveis de ambiente
- Rotacione chaves regularmente

```json
{
  "mcpServers": {
    "vectora": {
      "command": "vectora-mcp-server",
      "env": {
        "VECTORA_API_KEY": "${VECTORA_API_KEY}"
      }
    }
  }
}
```

### Rate Limiting

O MCP Server respeita todos os limites de rate limiting da API:

- Standard: 1,000 req/min
- Professional: 10,000 req/min
- Enterprise: Customizado

## Troubleshooting

### MCP Server não aparece no Claude

1. Verifique o caminho do arquivo de configuração
2. Valide o JSON: `jsonlint claude_desktop_config.json`
3. Reinicie completamente o Claude Desktop
4. Verifique os logs: `~/.local/state/claude/logs/`

### Autenticação falha

```bash
# Testar API key
curl -H "Authorization: Bearer vec_..." https://api.vectora.dev/health
```

### Timeout nas requisições

Ajuste o timeout no MCP Server:

```json
{
  "mcpServers": {
    "vectora": {
      "env": {
        "VECTORA_TIMEOUT_MS": "60000"
      }
    }
  }
}
```

## Monitoramento

### Logs do MCP Server

```bash
# Ver logs em tempo real
tail -f ~/.local/state/claude/logs/mcp-server.log

# Filtrar por erro
grep "ERROR" ~/.local/state/claude/logs/mcp-server.log
```

### Métricas

O MCP Server expõe métricas Prometheus:

```bash
# Acessar métricas (default port 9090)
curl http://localhost:9090/metrics
```

## External Linking

| Conceito                   | Recurso                | Link                                                                                           |
| -------------------------- | ---------------------- | ---------------------------------------------------------------------------------------------- |
| **Model Context Protocol** | Official specification | [modelcontextprotocol.io](https://modelcontextprotocol.io/)                                    |
| **Claude Desktop Guide**   | Official documentation | [support.anthropic.com/en/articles/8745496](https://support.anthropic.com/en/articles/8745496) |
| **Vectora MCP Server**     | GitHub repository      | [github.com/vectora-io/vectora-mcp](https://github.com/vectora-io/vectora-mcp)                 |
| **JSON Schema**            | Specification          | [json-schema.org](https://json-schema.org/)                                                    |
| **Protocol Design**        | Best practices         | [12factor.net](https://12factor.net/)                                                          |
