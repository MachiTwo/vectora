---
title: CLI e Interface TUI
slug: cli-and-tui
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - cli
  - tui
  - interface
  - textual
  - vectora
---

{{< lang-toggle >}}

{{< section-toggle >}}

O **Vectora CLI** é uma interface baseada em terminal (TUI - Textual User Interface) que oferece uma alternativa rich e interativa ao uso programático direto de Deep Agents. Construído com **Textual**, uma framework Python para TUIs modernas, o CLI fornece uma experiência completa de chat, gerenciamento de agentes, e execução de ferramentas com visualização em tempo real.

Diferentemente de CLIs tradicionais baseadas em comando-resposta, o Vectora CLI oferece uma **experiência conversacional rich**: você conversa com o agente em janelas de chat formatadas, vê execuções de ferramentas inline, recebe notificações assíncronas, e pode gerenciar múltiplas threads (conversas) simultaneamente.

## Arquitetura da CLI

### Pilha Tecnológica

```text
┌────────────────────────────────────┐
│   Camada de Aplicação              │
│   - Chat Loop                      │
│   - Event Handling                 │
│   - State Management               │
└────────────────────────────────────┘
                ↓
┌────────────────────────────────────┐
│   Textual (TUI Framework)          │
│   - Widgets (Chat, Input, Output)  │
│   - Event Loop                     │
│   - Rendering                      │
└────────────────────────────────────┘
                ↓
┌────────────────────────────────────┐
│   Deep Agents Framework            │
│   - Agent Execution                │
│   - Tool Management                │
│   - State Persistence              │
└────────────────────────────────────┘
                ↓
┌────────────────────────────────────┐
│   LangGraph + LangChain            │
│   - Graph Execution                │
│   - Checkpointing                  │
│   - Tool Dispatch                  │
└────────────────────────────────────┘
```

### Componentes Principais

| Componente         | Localização                       | Responsabilidade                                           |
| ------------------ | --------------------------------- | ---------------------------------------------------------- |
| **App**            | `app.py`                          | Container TUI, gerencia telas, binding de teclas           |
| **Chat Input**     | `widgets/chat_input.py`           | Widget de entrada com autocompletar e histórico            |
| **Message Store**  | `widgets/message_store.py`        | Armazena e indexa mensagens em memória                     |
| **Messages**       | `widgets/messages.py`             | Renderização formatada de mensagens (usuario, agent, erro) |
| **Agent Manager**  | `agent.py`                        | Criação e gerenciamento de agentes                         |
| **Server Manager** | `server_manager.py`               | Gerencia processos do LangGraph server                     |
| **MCP Tools**      | `mcp_tools.py`, `mcp_commands.py` | Integração Model Context Protocol                          |
| **Local Context**  | `local_context.py`                | Middleware para fornecer contexto local ao agente          |
| **Config**         | `config.py`                       | Carregamento de configurações, paths, credenciais          |

## Instalação e Setup Inicial

### Instalação

```bash
# Via pip
pip install deepagents-cli

# Via uv (recomendado)
uv tool install deepagents-cli

# Do repositório (desenvolvimento)
cd vectora/libs/cli
uv sync
```

### Primeiro Uso

```bash
# Inicia o CLI com agente padrão
deepagents

# Especificar agente
deepagents --agent code-reviewer

# Especificar modelo
deepagents --model gpt-4

# Retomar conversa anterior (thread)
deepagents --resume thread_abc123

# Modo não-interativo (scripts)
deepagents --input "Busca sobre autenticação" --output json
```

### Configuração Inicial

Na primeira execução, o CLI solicita:

1. **API Key** (Anthropic, OpenAI, etc)
2. **Diretório de trabalho** (onde agente pode ler/escrever)
3. **Preferências** (tema, idioma, etc)

Config é armazenada em `~/.deepagents/config.toml`:

```toml
[auth]
anthropic_api_key = "sk-ant-..."
openai_api_key = "sk-..."

[workspace]
default_work_dir = "/home/user/projects"
artifacts_dir = "/home/user/projects/.deepagents"

[agents]
default_agent = "default"
recent = "code-reviewer"

[ui]
theme = "nord"  # nord, dracula, monokai
ascii_mode = false
font_size = 12

[logging]
level = "info"  # debug, info, warn, error
```

## Usando o CLI: Guia Completo

### Fluxo Básico de Chat

```text
┌─────────────────────────────────────────────────────────┐
│                     Vectora Chat                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  > Você: Analisa esse código Python para performance  │
│                                                         │
│  ⏳ Agente: Analisando...                              │
│  [▓▓▓▓▓░░░░] 50%                                       │
│                                                         │
│  📄 Agente carregou: app.py (234 linhas)              │
│  🔧 Executando: grep -n "for.*in.*for" app.py         │
│  ✓ Encontrei 3 nested loops                           │
│                                                         │
│  Agente: Encontrei problemas:                         │
│  1. Linha 45: O(n²) loop desnecessário                │
│     Solução: use dict comprehension                   │
│                                                         │
│  2. Linha 78: Recomputação em loop                    │
│     Solução: cache com @lru_cache                     │
│                                                         │
│  > Você: _                                             │
│         (chat input aqui)                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Comandos de Teclado

| Atalho      | Ação                                    |
| ----------- | --------------------------------------- |
| `Ctrl+C`    | Interromper execução / sair             |
| `Ctrl+L`    | Limpar tela                             |
| `Ctrl+H`    | Ver histórico de mensagens              |
| `Ctrl+T`    | Gerenciar threads (conversas)           |
| `Ctrl+S`    | Salvar conversa como arquivo            |
| `Ctrl+N`    | Nova conversa                           |
| `Ctrl+A`    | Selecionar agente                       |
| `Ctrl+M`    | Trocar modelo                           |
| `Page Up`   | Scroll para cima no histórico           |
| `Page Down` | Scroll para baixo no histórico          |
| `Tab`       | Autocompletar (skills, comandos, paths) |
| `↑` / `↓`   | Navegar histórico de input              |

### Gerenciando Agentes

#### Listar agentes disponíveis

```bash
deepagents --list-agents
```

Saída:

```text
Agentes disponíveis:
  default           (padrão, pronto para qualquer tarefa)
  code-reviewer     (especializado em revisão de código)
  documenter        (gera documentação automática)
  debugger          (debug de problemas)
  analyst           (análise de dados)

Use: deepagents --agent <name>
```

#### Criar novo agente

```bash
deepagents --new-agent marketing-writer
```

Cria arquivo `~/.deepagents/marketing-writer/agents.toml`:

```toml
[agent]
name = "marketing-writer"
system_prompt = """Você é especialista em copywriting para marketing.
- Escreva com tom envolvente
- Use storytelling
- Inclua call-to-action claro
"""

[tools]
# Skills que este agente pode usar
sources = ["skills/writing", "skills/research"]

[model]
# Configuração específica
provider = "anthropic"
model_name = "claude-opus-4-7"
temperature = 0.7
max_tokens = 2000
```

#### Usar agente customizado

```bash
deepagents --agent marketing-writer

> Você: Escreve um email de marketing para um novo SaaS
```

### Gerenciando Threads (Conversas)

Cada "thread" é uma conversa independente com ID único:

```bash
# Listar threads
deepagents --list-threads

# Ver: thread_1 (12 mensagens, criado há 2h)
#      thread_2 (5 mensagens, criado há 1 dia)
#      thread_3 (34 mensagens, criado há 5 dias)

# Retomar thread específica
deepagents --resume thread_3

# Criar thread com nome customizado
deepagents --new-thread "research-project-x"

# Exportar thread para arquivo
deepagents --export-thread thread_1 --format json --output conversation.json

# Deletar thread
deepagents --delete-thread thread_2
```

### Visualizando Execução de Ferramentas

Quando o agente usa ferramentas, você vê em tempo real:

```text
Você: Lê o arquivo config.py

🔧 Agente usando: read_file
  Arquivo: /home/user/projects/config.py

  [▓▓▓░░░░░░] 30% (lendo...)

✓ Sucesso! 234 bytes lidos

📝 Conteúdo:
  1 | # Configuration module
  2 | import os
  3 |
  4 | DEBUG = os.getenv("DEBUG", False)
  5 | DATABASE_URL = os.getenv("DB_URL")
  ...

Agente: Vi a configuração. DEBUG está desativado, DB_URL...
```

### Modo Output Estruturado

Para integrar com scripts/APIs:

```bash
# Output em JSON
deepagents --input "Análise de performance" --output json > result.json

# Output em Markdown
deepagents --input "Gera relatório" --output markdown > report.md

# Output raw (sem formatação)
deepagents --input "Simples busca" --output text
```

Output JSON:

```json
{
  "status": "success",
  "messages": [
    {
      "role": "user",
      "content": "Análise de performance"
    },
    {
      "role": "assistant",
      "content": "Encontrei...",
      "tool_calls": [{ "name": "read_file", "args": { "path": "app.py" } }]
    }
  ],
  "metadata": {
    "thread_id": "thread_1",
    "timestamp": "2026-05-04T14:30:00Z",
    "tools_used": ["read_file", "search"],
    "tokens": { "input": 1200, "output": 450 }
  }
}
```

## Configuração de Agentes (agents.toml)

Cada agente tem arquivo `agents.toml` que controla seu comportamento:

```toml
[agent]
name = "advanced-analyzer"
description = "Agente especializado em análise profunda"

# System prompt define "personalidade" do agente
system_prompt = """Você é analista especializado.
- Sempre questione premissas
- Forneça múltiplas perspectivas
- Cite fontes e evidências
"""

[model]
provider = "anthropic"              # anthropic, openai, etc
model_name = "claude-opus-4-7"
temperature = 0.5                   # 0=determinístico, 1=criativo
max_tokens = 4000
top_p = 0.9
top_k = 40

[tools]
# Ferramentas disponíveis para este agente
enabled = ["read_file", "search", "analyze"]
disabled = ["delete_file", "execute_script"]

# Skills (componentes reutilizáveis)
sources = [
    "skills/analysis",
    "skills/research",
    "~/.deepagents/shared-skills",
]

[backend]
# Como executar ferramentas
type = "composite"
filesystem_root = "/home/user/work"
allowed_shell_commands = ["grep", "find", "head", "tail"]

[middleware]
# Middleware customizado para este agente
memory_buffer_tokens = 3000
enable_filesystem_sandbox = true
enable_human_approval = true  # Pedir aprovação antes de certos tools

[limits]
max_iterations = 50             # Máximo de rodadas LLM + tool
timeout_per_tool = 30           # Segundos
max_memory_messages = 100        # Histórico máximo

[monitoring]
enable_logging = true
log_level = "info"
langsmith_project = "vectora-dev"
```

## MCP Integration (Model Context Protocol)

MCP permite que o agente acesse ferramentas/dados de serviços externos (GitHub, Slack, etc):

### Configurar MCP Server

```toml
# Em agents.toml

[mcp]
# Servidores MCP que este agente pode acessar
servers = [
    "github",      # MCP para GitHub
    "slack",       # MCP para Slack
    "notion",      # MCP para Notion
]

# Autenticação
[mcp.github]
provider = "github"
token = "ghp_..."
org = "vectora-io"

[mcp.slack]
provider = "slack"
token = "xoxb-..."
default_channel = "#general"
```

### Usando MCP Tools

Quando MCP está configurado, você pode usar:

```text
> Você: Cria um issue no GitHub com título "Fix slow search"

🔧 Agente usando: github/create_issue
  Repositório: vectora-io/vectora
  Título: Fix slow search
  Body: Pesquisa demora > 5s

✓ Issue criado: #1234
  URL: https://github.com/vectora-io/vectora/issues/1234

Agente: Criei o issue #1234. Quer que eu...
```

## Performance e Otimização

### Token Awareness

CLI monitora tokens e avisa quando se aproximando de limites:

```text
⚠️  Aviso: 70% do contexto usado (5.6k/8k tokens)
   Limite de iterações: 15/50
   Memória de conversa será resumida na próxima mensagem
```

### Caching e Histórico

```bash
# Ver cache status
deepagents --show-cache

# Limpar cache
deepagents --clear-cache

# Desabilitar cache (debug)
deepagents --no-cache
```

### Modo Offline

Para ambientes sem internet:

```bash
# Modo offline usa apenas modelos locais/cached
deepagents --offline --model local-llama

# Nota: Ferramentas que precisam de rede falharão gracefully
```

## Debugging e Troubleshooting

### Ativar Debug Logging

```bash
deepagents --debug
```

Saída verbose:

```text
[DEBUG] Loading config from ~/.deepagents/config.toml
[DEBUG] Agent 'default' initialized with 8 tools
[DEBUG] LangGraph server started on 127.0.0.1:2024
[DEBUG] Middleware stack: [FilesystemMiddleware, MemoryMiddleware, SkillsMiddleware]
[DEBUG] Checkpointer: MemorySaver
[DEBUG] User input: "Busca sobre IA"
[DEBUG] System prompt assembled (1200 tokens)
[DEBUG] LLM call (Claude Opus): 1200 input tokens
[DEBUG] LLM response with tool call: read_file
[DEBUG] Tool node executing: read_file /home/user/doc.md
[DEBUG] Tool output: 234 bytes
[DEBUG] State checkpoint saved
```

### Ver Histórico Completo

```bash
# Ver todas as mensagens da thread atual (com timestamps)
deepagents --show-history

# Ver com detalhes (tool calls, tokens, latência)
deepagents --show-history --verbose

# Exportar histórico
deepagents --export-history thread_1 --format json
```

### Teste de Conectividade

```bash
# Testar conexão com API
deepagents --test-connection

# Saída:
# ✓ Anthropic API: OK (latência 150ms)
# ✓ OpenAI API: OK (latência 220ms)
# ✗ Custom endpoint: FAILED (timeout)
```

## Shortcuts e Avançado

### Skills Integration

Skills são componentes reutilizáveis que agentes podem usar:

```bash
# Ver skills disponíveis
deepagents --list-skills

# Output:
# Skill: @search-docs
#   Descrição: Busca em documentação
#   Ferramentas: [search, read]
#   Agentes: 3
#
# Skill: @code-analysis
#   Descrição: Analisa código
#   Ferramentas: [grep, syntax-check]
#   Agentes: 5

# Usar skill em agente
> Você: @code-analysis app.py
```

### Batch Processing

Para processar múltiplas solicitações:

```bash
# Arquivo input.jsonl
{"input": "Analisa app.py", "thread": "batch_1"}
{"input": "Documenta api.py", "thread": "batch_1"}
{"input": "Testa utils.py", "thread": "batch_2"}

# Processar em batch
deepagents --batch input.jsonl --output batch_results.jsonl

# Monitorar progresso
deepagents --batch input.jsonl --verbose --show-progress
```

### Integração com Outros Clientes

CLI pode ser usado como backend para ferramentas externas:

```python
# Python script
import subprocess
import json

result = subprocess.run(
    ["deepagents", "--input", "Busca sobre IA", "--output", "json"],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)
print(f"Resposta: {data['messages'][-1]['content']}")
```

## External Linking

| Conceito                   | Recurso              | Link                                                                      |
| -------------------------- | -------------------- | ------------------------------------------------------------------------- |
| **Textual Framework**      | TUI Python           | [textualize.io](https://textualize.io/)                                   |
| **Deep Agents CLI**        | Docs oficiais        | [langchain.com/deepagents-cli](https://langchain.com/deepagents-cli/)     |
| **Rich Library**           | Formatting terminal  | [rich.readthedocs.io](https://rich.readthedocs.io/)                       |
| **Model Context Protocol** | MCP Spec             | [modelcontextprotocol.io](https://modelcontextprotocol.io/)               |
| **LangGraph Server**       | Background execution | [langchain.com/langgraph-server](https://langchain.com/langgraph-server/) |
