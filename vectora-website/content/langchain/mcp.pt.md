---
title: "Model Context Protocol (MCP)"
slug: "langchain/mcp"
description: "Protocolo aberto para ferramentas e contexto em LLMs"
date: 2026-05-03
type: docs
sidebar:
  open: true
breadcrumbs: true
tags: ["langchain", "mcp", "protocol", "tools", "context", "integration"]
---

{{< lang-toggle >}}

MCP (Model Context Protocol) é um **protocolo aberto** que padroniza como aplicações fornecem ferramentas e contexto para LLMs.

## O Que é MCP?

Um padrão universal para:
- **Tools** - Funções que LLMs podem chamar
- **Resources** - Dados expostos (arquivos, registros, respostas de APIs)
- **Prompts** - Templates reutilizáveis que se convertem em mensagens

**Sem MCP:** Cada integração é única
```
LangChain ←→ Tool A
LangChain ←→ Tool B
LangChain ←→ Tool C
```

**Com MCP:** Protocolo universal
```
LangChain ←→ MCP Client ←→ [MCP Server 1] → Tools/Resources
                             [MCP Server 2] → Tools/Resources
                             [MCP Server 3] → Tools/Resources
```

## Transportes de Comunicação

### Stdio (Local)

Comunica com **subprocessos locais** - ideal para ferramentas simples:

```python
import json
import sys

# MCP Server simples (stdin/stdout)
while True:
    line = sys.stdin.readline()
    request = json.loads(line)
    
    if request["method"] == "tools/list":
        response = {
            "tools": [
                {
                    "name": "search",
                    "description": "Search documents",
                    "inputSchema": {...}
                }
            ]
        }
    elif request["method"] == "tools/call":
        result = execute_tool(request["params"])
        response = {"result": result}
    
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()
```

**Quando usar:**
- Ferramentas locais
- Baixa latência importante
- Segurança (sem rede)

### HTTP (Remoto)

Usa **requisições HTTP** para servidores remotos:

```python
from langchain_mcp import MCPClient

client = MCPClient(
    server_url="https://mcp-server.example.com",
    auth_token="your_token"
)

# Listar ferramentas disponíveis
tools = await client.list_tools()

# Chamar ferramenta
result = await client.call_tool(
    name="search",
    arguments={"query": "AI trends"}
)
```

**Quando usar:**
- Servidores remotos
- Múltiplas aplicações
- Escalabilidade importante

## Recursos Principais

### 1. Tools

Funções executáveis com schema definido:

```python
{
    "name": "search",
    "description": "Search documents for relevant information",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "limit": {
                "type": "integer",
                "default": 5
            }
        },
        "required": ["query"]
    }
}
```

### 2. Resources

Dados expostos para contexto:

```python
{
    "uri": "file:///documents/vectora-docs",
    "name": "Vectora Documentation",
    "mimeType": "text/markdown",
    "description": "Complete Vectora system documentation"
}
```

### 3. Prompts

Templates que se convertem em mensagens:

```python
{
    "name": "code_review",
    "description": "Template for code review",
    "arguments": [
        {
            "name": "code",
            "description": "Code to review"
        }
    ]
}
```

## Integração com LangChain

### Setup Básico

```python
from langchain_mcp import MCPClient, create_mcp_tools
from langchain.agents import create_react_agent

# Conectar a servidores MCP
client = MCPClient({
    "stdio_server": {
        "command": "python",
        "args": ["./mcp_server.py"]
    },
    "remote_server": {
        "url": "https://example.com/mcp"
    }
})

# Converter para LangChain tools
mcp_tools = await create_mcp_tools(client)

# Usar em agente
agent = create_react_agent(
    model=llm,
    tools=mcp_tools,
    prompt=prompt
)
```

### Exemplo Prático

```python
# MCP Server (Python)
class MyMCPServer:
    async def tools_list(self):
        return [{
            "name": "search_vectora",
            "description": "Search Vectora knowledge base",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                }
            }
        }]
    
    async def tools_call(self, name, args):
        if name == "search_vectora":
            return search_vectora_kb(args["query"])

# LangChain Agent
agent = create_agent(
    model="claude-3-opus",
    mcp_servers=[MyMCPServer()],
    tools_from="mcp"
)

result = await agent.invoke("Find documentation about VCR")
```

## Funcionalidades Avançadas

### Interceptadores

Modificar requisições/respostas:

```python
class LoggingInterceptor:
    async def before_request(self, request):
        logger.info(f"Calling: {request['method']}")
        return request
    
    async def after_response(self, response):
        logger.info(f"Result: {response['result']}")
        return response

client.add_interceptor(LoggingInterceptor())
```

### Suporte Multimodal

Ferramentas podem retornar conteúdo estruturado:

```python
response = {
    "content": [
        {
            "type": "text",
            "text": "Here's the document:"
        },
        {
            "type": "image",
            "data": base64_image
        },
        {
            "type": "document",
            "uri": "file:///path/to/doc"
        }
    ]
}
```

## Padrão: Vectora como MCP Server

```python
# Vectora expõe seu índice como MCP Server
class VectoraMCPServer:
    async def tools_list(self):
        return [
            {
                "name": "search",
                "description": "Search Vectora knowledge base"
            },
            {
                "name": "retrieve_context",
                "description": "Get context for code understanding"
            }
        ]
    
    async def resources_list(self):
        return [
            {
                "uri": "vectora://buckets/public",
                "name": "Public Knowledge"
            },
            {
                "uri": "vectora://buckets/private",
                "name": "Private Knowledge"
            }
        ]

# Agentes Claude Code usam Vectora via MCP
agent = create_agent(
    model="claude-3-opus",
    mcp_servers=[VectoraMCPServer()]
)
```

## External Linking

| Conceito | Recurso | Link |
|----------|---------|------|
| MCP Official | Model Context Protocol | [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/) |
| MCP Spec | Protocol Specification | [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction) |
| LangChain MCP | Integration Guide | [https://docs.langchain.com/oss/python/langchain/mcp](https://docs.langchain.com/oss/python/langchain/mcp) |
| MCP Servers | Community Servers | [https://modelcontextprotocol.io/servers](https://modelcontextprotocol.io/servers) |
| Creating Servers | Server Development | [https://modelcontextprotocol.io/server-guides](https://modelcontextprotocol.io/server-guides) |
