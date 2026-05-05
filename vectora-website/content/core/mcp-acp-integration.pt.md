---
title: MCP e ACP Integration
slug: mcp-acp-integration
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - mcp
  - acp
  - protocol
  - integration
  - vectora
---

{{< lang-toggle >}}

{{< section-toggle >}}

**MCP (Model Context Protocol)** e **ACP (Agent Client Protocol)** são dois protocolos complementares que permitem que Deep Agents (e Vectora) se integrem com ecossistemas maiores:

- **MCP:** Permite que agentes acessem ferramentas e dados de serviços externos (GitHub, Slack, Notion, etc.) através de um protocolo padronizado.
- **ACP:** Permite que agentes rodem como "clientes" dentro de editores de texto (Zed, VSCode com suporte futuro) que implementam o protocolo.

Ambos são protocolos baseados em **stdio** (entrada/saída padrão), tornando-os agnósticos a linguagem e rede.

## Model Context Protocol (MCP)

### O que é MCP?

MCP é um **protocolo JSON-RPC** que define como um cliente (o agente) comunica com um servidor (provedor de ferramentas/dados). Qualquer servidor que implemente MCP pode fornecer ferramentas para o agente.

```text
┌──────────────────────┐
│   Deep Agent Client  │
│   (Vectora, Claude)  │
└──────────┬───────────┘
           │
     MCP (JSON-RPC)
     via stdio
           │
    ┌──────┴──────────┐
    │                 │
┌───▼───────┐    ┌───▼──────────┐
│MCP GitHub │    │MCP Slack     │
│Server     │    │Server        │
└───────────┘    └──────────────┘
    │                  │
  GitHub API      Slack API
```

### Especificação MCP

MCP define:

1. **Resources:** Dados que o servidor expõe (arquivos, issues, mensagens)
2. **Tools:** Funções que o servidor oferece (criar issue, enviar mensagem)
3. **Prompts:** Templates que guiam o agente

### Instalando MCP Servers

```bash
# MCP servers são executáveis ou scripts
# Instalá-los significa torná-los disponíveis no PATH ou em local known

# Via npm (para servidores Node.js)
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-slack

# Via pip (para servidores Python)
pip install mcp-github-server
pip install mcp-slack-server

# Manual: download binário
# Colocar em ~/.mcp/servers/

# Verificar instalação
which mcp-github-server
# /usr/local/bin/mcp-github-server
```

### Configurando MCP no Agente

MCP servers são configurados no arquivo `agents.toml`:

```toml
[mcp]
# Lista de servidores MCP que este agente pode acessar
servers = ["github", "slack", "notion"]

# Configuração por servidor
[mcp.github]
# Type: identifica qual server é este
type = "github"

# Command: como iniciar o server
command = "mcp-github-server"

# Args: argumentos para passar ao command
args = []

# Env: variáveis de ambiente (autenticação, etc)
env = {
    GITHUB_TOKEN = "ghp_...",
    GITHUB_ORG = "vectora-io",
}

[mcp.slack]
type = "slack"
command = "mcp-slack-server"
env = {
    SLACK_BOT_TOKEN = "xoxb-...",
    SLACK_SIGNING_SECRET = "...",
}

[mcp.notion]
type = "notion"
command = "mcp-notion-server"
env = {
    NOTION_API_KEY = "ntn_...",
}
```

### Servidores MCP Disponíveis

| Server         | Tipo              | Ferramentas                                        | Link                                                                                       |
| -------------- | ----------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **github**     | Oficial Anthropic | Lista repos, issues, PRs, create issue, comment PR | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **slack**      | Oficial Anthropic | Listar canais, enviar mensagem, buscar histórico   | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **notion**     | Comunidade        | Buscar páginas, criar página, atualizar            | [mcp-notion-server.com](https://mcp-notion-server.com)                                     |
| **postgres**   | Comunidade        | Executar queries, schema inspection                | [github.com/mcp-postgres](https://github.com/mcp-postgres)                                 |
| **filesystem** | Oficial           | Ler/escrever arquivos (alternativa ao backend)     | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |

### Usando MCP Tools no Agente

Uma vez MCP configurado, o agente acessa ferramentas automaticamente:

```text
> Você: Cria um issue no GitHub com título "Fix slow search"

🔍 Agente detecta: usar MCP GitHub
    ↓
[Inicializa MCP GitHub Server]
    ↓
Carrega ferramentas disponíveis:
  - list_repositories
  - create_issue
  - list_issues
  - comment_on_pr
  ...
    ↓
Agente decide usar: create_issue
    ↓
MCP Call:
  {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "create_issue",
      "arguments": {
        "repo": "vectora-io/vectora",
        "title": "Fix slow search",
        "body": "Search takes > 5 seconds. Need optimization.",
      }
    }
  }
    ↓
MCP Server GitHub responde:
  {
    "jsonrpc": "2.0",
    "result": {
      "issue_number": 1234,
      "url": "https://github.com/vectora-io/vectora/issues/1234",
    }
  }
    ↓
Agente: Criei issue #1234: https://github.com/vectora-io/vectora/issues/1234
```

### Implementando MCP Server Customizado

Para integrar seu próprio serviço:

```python
# my_mcp_server.py
import json
import sys
from typing import Any

class MyMCPServer:
    def __init__(self):
        self.tools = {
            "my_custom_tool": {
                "description": "Faz algo customizado",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"},
                    },
                }
            }
        }

    def handle_request(self, request: dict) -> dict:
        """Processar request JSON-RPC."""
        method = request.get("method")

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "result": {"tools": list(self.tools.values())}
            }

        elif method == "tools/call":
            name = request["params"]["name"]
            args = request["params"]["arguments"]

            if name == "my_custom_tool":
                result = self.my_custom_tool(args["param1"])
            else:
                result = {"error": f"Unknown tool: {name}"}

            return {
                "jsonrpc": "2.0",
                "result": result
            }

    def my_custom_tool(self, param1: str) -> str:
        """Implementação da ferramenta."""
        return f"Processado: {param1}"

    def run(self):
        """Loop principal que lê stdin e escreve stdout."""
        for line in sys.stdin:
            request = json.loads(line)
            response = self.handle_request(request)
            print(json.dumps(response))

if __name__ == "__main__":
    server = MyMCPServer()
    server.run()
```

Configurar no `agents.toml`:

```toml
[mcp.my_service]
type = "custom"
command = "python /path/to/my_mcp_server.py"
```

## Agent Client Protocol (ACP)

### O que é ACP?

**ACP** permite que Deep Agents rodem como "clientes inteligentes" dentro de editores de texto que suportam o protocolo. Diferentemente de MCP (client→server), ACP é **server→client** onde o editor é o servidor e o agente é o cliente.

Caso de uso: Agente rodar em Zed, VSCode, ou outro editor, acessando o projeto aberto e ajudando o desenvolvedor.

```text
┌──────────────────────────────────────┐
│         Zed Editor                   │
│  ┌──────────────────────────────────┐│
│  │   Project Files (accessible)     ││
│  │   - app.py                       ││
│  │   - config.json                  ││
│  └──────────────────────────────────┘│
│           ↑                           │
│        ACP Protocol                   │
│        (stdio)                        │
│           ↑                           │
│  ┌──────────────────────────────────┐│
│  │   Deep Agent Process             ││
│  │   - Acessa arquivos do projeto   ││
│  │   - Faz análise                  ││
│  │   - Retorna sugestões            ││
│  └──────────────────────────────────┘│
└──────────────────────────────────────┘
```

### Instalando ACP no Zed

1. **Ter Zed instalado**

   ```bash
   curl -f https://zed.dev/install.sh | sh
   ```

2. **Instalar servidor ACP Vectora**

   ```bash
   npm install -g vectora-acp-server
   # ou
   pip install vectora-acp
   ```

3. **Configurar Zed**

   Editar `~/.config/zed/settings.json`:

   ```json
   {
     "agent_servers": {
       "Vectora": {
         "type": "custom",
         "command": "vectora-acp-server"
       }
     }
   }
   ```

4. **Usar no Zed**
   - `Cmd+Shift+?` para abrir Agent Panel
   - Criar nova Vectora thread
   - Começar a conversar

### Implementando ACP Server

```python
# vectora_acp_server.py
from acp import run_agent
from deepagents import create_deep_agent
from deepagents_acp.server import AgentServerACP
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
import asyncio

async def main():
    # Criar agente especializado para editor
    model = ChatAnthropic(model_name="claude-opus-4-7")

    agent = create_deep_agent(
        model=model,
        tools=[
            read_file,
            write_file,
            search_files,
            run_command,
        ],
        system_prompt="""Você é assistente de desenvolvimento integrado no editor.
- Acesse apenas arquivos do projeto
- Forneça sugestões de código
- Detecte bugs via análise estática
- Sugira melhorias de performance
""",
        checkpointer=MemorySaver(),
    )

    # Wrapping para ACP
    server = AgentServerACP(agent)

    # Executar
    await run_agent(server)

if __name__ == "__main__":
    asyncio.run(main())
```

### Diferenças MCP vs ACP

| Aspecto          | MCP                             | ACP                               |
| ---------------- | ------------------------------- | --------------------------------- |
| **Direção**      | Client → Server                 | Server ← Client (Agent em Client) |
| **Use Case**     | Agente acessa serviços externos | Agente rodando dentro de editor   |
| **Protocolo**    | JSON-RPC                        | ACP (custom)                      |
| **Exemplos**     | GitHub, Slack, Notion           | Zed, VSCode (futuro)              |
| **Acesso**       | APIs externas                   | Projeto local do editor           |
| **Persistência** | Agente em servidor              | Agente em máquina local           |

## Combinando MCP + Agente

Caso comum: Agente com MCP GitHub + MCP Slack

```toml
[mcp]
servers = ["github", "slack"]

[mcp.github]
type = "github"
command = "mcp-github-server"
env = { GITHUB_TOKEN = "..." }

[mcp.slack]
type = "slack"
command = "mcp-slack-server"
env = { SLACK_BOT_TOKEN = "..." }
```

Fluxo:

```text
> Você: Cria issue no GitHub e notifica no Slack quando pronto

Agente analisa:
- Preciso criar issue → usar MCP GitHub
- Preciso notificar → usar MCP Slack

[Cria issue via MCP GitHub]
✓ Issue criado #1234

[Envia mensagem via MCP Slack]
✓ Notificado em #dev-team

Agente: Issue #1234 criado e notificado no Slack.
```

## Debugging MCP/ACP

### Ativar Logging MCP

```bash
# Executar agente com debug logging
RUST_LOG=debug vectora --debug

# ou via Python
import logging
logging.getLogger("mcp").setLevel(logging.DEBUG)
logging.getLogger("acp").setLevel(logging.DEBUG)
```

Saída:

```text
[DEBUG] MCP: Starting github server at /usr/local/bin/mcp-github-server
[DEBUG] MCP: GitHub server initialized
[DEBUG] MCP: Available tools: [list_repositories, create_issue, ...]
[DEBUG] MCP: Tool call: create_issue with args {'repo': 'vectora-io/vectora', ...}
[DEBUG] MCP: Response: {'issue_number': 1234, 'url': '...'}
```

### Testar MCP Server Localmente

```bash
# Testar se servidor responde
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | \
  mcp-github-server

# Saída esperada:
# {"jsonrpc":"2.0","result":{"tools":[...]}}
```

### Ver Tools Disponíveis

```bash
# Após configurar MCP no agente:
deepagents --list-mcp-tools

# Saída:
# GitHub Tools:
#   - list_repositories: List repos in org
#   - create_issue: Create new issue
#   - comment_on_pr: Comment on PR
#
# Slack Tools:
#   - list_channels: List channels
#   - send_message: Send message to channel
#   - get_channel_history: Get message history
```

## Performance e Rate Limiting

MCP calls têm overhead de startup (inicializar servidor). Para conversas longas:

```text
Primeira chamada MCP: 200-500ms (startup do server)
Chamadas seguintes: 50-100ms (server já pronto)
```

Otimizações:

```python
# Manter server vivo entre calls
agent = create_deep_agent(
    model=model,
    tools=[...],
    mcp_timeout=300,  # Manter server por 5 minutos
    mcp_auto_cleanup=True,  # Auto-kill se inativo
)

# Cache de resultados MCP
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_github_list_repos(org: str):
    """Cache de 1 minuto."""
    return mcp_github.list_repositories(org)
```

## Segurança MCP/ACP

### Validação de Respostas

```python
# MCP Server pode retornar qualquer coisa
# Sempre validar output antes de usar

def safe_mcp_call(tool_name: str, args: dict) -> Any:
    try:
        response = mcp_server.call(tool_name, args)

        # Validar estrutura
        if not isinstance(response, dict):
            raise ValueError("MCP response deve ser dict")

        # Validar conteúdo
        if "error" in response:
            raise ValueError(f"MCP error: {response['error']}")

        return response
    except Exception as e:
        logger.error(f"MCP call failed: {e}")
        raise
```

### Permissões MCP

MCP servidores devem respeitar permissões:

```python
# MCP server implementa controle de acesso
class SecureGitHubServer:
    def create_issue(self, repo: str, title: str, body: str) -> dict:
        # Validar permissão
        if not self.user_has_permission(repo, "write"):
            raise PermissionError(f"No write access to {repo}")

        # Executar
        return github.create_issue(repo, title, body)
```

## External Linking

| Conceito              | Recurso               | Link                                                                                       |
| --------------------- | --------------------- | ------------------------------------------------------------------------------------------ |
| **MCP Specification** | Official spec         | [modelcontextprotocol.io](https://modelcontextprotocol.io/)                                |
| **MCP Servers**       | Official servers      | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
| **ACP Spec**          | Agent Client Protocol | [agentclientprotocol.com](https://agentclientprotocol.com/)                                |
| **Zed Editor**        | Editor com ACP        | [zed.dev](https://zed.dev/)                                                                |
| **JSON-RPC 2.0**      | Protocol spec         | [jsonrpc.org/specification](https://www.jsonrpc.org/specification)                         |
