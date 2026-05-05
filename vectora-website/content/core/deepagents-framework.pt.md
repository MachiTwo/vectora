---
title: Deep Agents Framework
slug: deepagents-framework
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - deep-agents
  - framework
  - langchain
  - langgraph
  - vectora
---

{{< lang-toggle >}}

{{< section-toggle >}}

O **Deep Agents Framework** é o núcleo do Vectora. Fornece uma arquitetura modular, extensível e pronta para produção para construir agentes de IA autônomos com suporte integrado a ferramentas, memória persistente, subagentes, e integração com múltiplos modelos de linguagem.

Diferentemente de frameworks genéricos, Deep Agents foi projetado especificamente para **agentes do mundo real**: respeita permissões, gerencia checkpoints, suporta interrupções humanas, fornece transparência completa sobre execução, e pode ser implantado em ambientes restringidos (incluindo sistemas local-first como Vectora).

## Arquitetura Fundamental

### Modelo Mental: State Machine com LangGraph

Deep Agents é construído sobre **LangGraph**, uma abstração de máquina de estado que representa a execução do agente como um grafo acíclico dirigido (DAG). Cada nó no grafo representa uma etapa de processamento; cada transição representa uma decisão.

```text
┌─────────────────────────────────────────────────────────────┐
│                    Fluxo do Deep Agent                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Input                                                       │
│    ↓                                                          │
│  ┌──────────────────┐                                        │
│  │  System Prompt   │  (BASE + USER + SUFFIX, assembled)     │
│  └─────────┬────────┘                                        │
│            ↓                                                  │
│  ┌──────────────────────────────────┐                        │
│  │   LLM Call (Claude, GPT-4, etc)  │                        │
│  │   - Text output                  │                        │
│  │   - Tool calls (JSON)            │                        │
│  └──────────┬───────────────────────┘                        │
│             ↓                                                 │
│  ┌──────────────────────────────────┐                        │
│  │   Tool Node (Executor)           │                        │
│  │   - Execute ferramenta solicitada│                        │
│  │   - Capturar output/erro         │                        │
│  │   - Aplicar middleware           │                        │
│  └──────────┬───────────────────────┘                        │
│             ↓                                                 │
│  ┌──────────────────────────────────┐                        │
│  │   Middleware Stack               │                        │
│  │   - Permissions                  │                        │
│  │   - Skills resolution            │                        │
│  │   - Memory management            │                        │
│  │   - Summarization                │                        │
│  └──────────┬───────────────────────┘                        │
│             ↓                                                 │
│  ┌──────────────────────────────────┐                        │
│  │   State Update & Checkpointing   │                        │
│  │   - Armazenar estado em storage  │                        │
│  │   - Permitir retomada posterior  │                        │
│  └──────────┬───────────────────────┘                        │
│             ↓                                                 │
│  Retornar ao LLM ou Final Output                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Conceitos-Chave

### Agent State (Estado do Agente)

Toda execução do agente é representada como um estado imutável que flui através do grafo:

```python
# Estado simplificado (o real tem mais campos)
{
    "messages": [
        HumanMessage("Faz uma busca sobre IA"),
        AIMessage("Vou buscar isso...", tool_calls=[...]),
        ToolMessage(content="Encontrei 3 resultados..."),
        ...
    ],
    "metadata": {
        "thread_id": "thread_abc123",
        "timestamp": "2026-05-04T14:30:00Z",
        "tools_used": ["search", "summarize"],
    }
}
```

### Middleware Pipeline (Processamento em Cadeia)

Middleware são plugues que interceptam e modificam comportamento do agente:

```python
# Exemplo: SkillsMiddleware converte referências de skills em tool calls
Input: "Usar @my-skill para processar isso"
         ↓
[SkillsMiddleware]
         ↓
Output: "Chamar a ferramenta 'my_skill' com esses parâmetros"
```

A pilha de middleware é aplicada em **ordem específica** para respeitar dependências:

1. **Filesystem** - Resolve permissões de arquivo antes de ferramentas acessarem disco
2. **Permissions** - Valida se o usuário pode executar uma ferramenta específica
3. **Skills** - Expande referências de skills em tool calls
4. **Memory** - Gerencia contexto persistente entre execuções
5. **Summarization** - Resume histórico longo para controlar tamanho de contexto
6. **Subagents** - Delega tarefas para subagentes especializados

### Backends (Armazenamento e Execução)

Backends definem COMO o agente executa ferramentas e armazena estado:

| Backend               | Uso                         | Quando usar                                   |
| --------------------- | --------------------------- | --------------------------------------------- |
| **FilesystemBackend** | Lê/escreve arquivos locais  | Desenvolvimento local, agentes de codificação |
| **LocalShellBackend** | Executa comandos shell      | Automação de linha de comando, CI/CD          |
| **SandboxBackend**    | Ambientes isolados (Docker) | Segurança, executar código não confiável      |
| **StateBackend**      | Apenas state, sem execução  | Testes, processamento cloud                   |
| **CompositeBackend**  | Combina múltiplos           | Filesystem + Shell + Custom                   |

### Checkpointing (Persistência de Estado)

Agentes podem salvar estado em cada etapa, permitindo retomada:

```python
# Exemplo: Salvar estado para retomada posterior
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()  # Em memória (dev) ou disk (prod)
agent = create_deep_agent(
    tools=[...],
    checkpointer=checkpointer,
)

# Execução 1: Pausa após 2 tool calls
config = {"configurable": {"thread_id": "user_123"}}
state = agent.invoke({"messages": [...]}, config)

# Execução 2: Retoma de onde parou
state = agent.invoke({"messages": [...]}, config)
```

## Criando um Deep Agent

### Setup Básico

```python
from deepagents import create_deep_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

# 1. Definir ferramentas
@tool
def search_documentation(query: str) -> str:
    """Buscar documentação por query."""
    return f"Encontrei 5 documentos sobre '{query}'"

@tool
def read_file(path: str) -> str:
    """Ler conteúdo de arquivo."""
    with open(path) as f:
        return f.read()

# 2. Criar modelo
model = ChatAnthropic(model_name="claude-opus-4-7")

# 3. Criar agente
agent = create_deep_agent(
    model=model,
    tools=[search_documentation, read_file],
    system_prompt="Você é um assistente especializado em buscar e analisar documentação.",
    checkpointer=MemorySaver(),
)

# 4. Executar
state = agent.invoke(
    {"messages": [{"role": "user", "content": "Busca sobre autenticação JWT"}]},
    config={"configurable": {"thread_id": "user_456"}}
)

print(state["messages"][-1].content)  # Última resposta do agente
```

### Opções Avançadas

```python
from deepagents import create_deep_agent
from deepagents.middleware import (
    MemoryMiddleware,
    SkillsMiddleware,
    FilesystemMiddleware,
    FilesystemPermission,
)
from deepagents.backends import CompositeBackend, FilesystemBackend, LocalShellBackend
from langgraph.checkpoint.postgres import PostgresSaver  # Produção

agent = create_deep_agent(
    model=model,
    tools=[...],

    # Backends: Como executar ferramentas
    backend=CompositeBackend([
        FilesystemBackend(root="/home/user/work"),
        LocalShellBackend(allowed_commands=["grep", "find", "head"]),
    ]),

    # Middleware: Processamento customizado
    middleware=[
        FilesystemMiddleware(
            permissions=[
                FilesystemPermission(
                    path_pattern="/home/user/work/**",
                    access="rw",  # read-write
                )
            ]
        ),
        MemoryMiddleware(buffer_tokens=2000),  # Janela de memória
        SkillsMiddleware(
            sources=["/path/to/skills/"],  # Carregar skills de diretórios
        ),
    ],

    # Checkpointing: Onde armazenar estado
    checkpointer=PostgresSaver.from_conn_string(
        "postgresql://user:pass@localhost/vectora_db"
    ),

    # Model switching: Trocar modelos dinamicamente
    model_factory=lambda context: {
        "claude-opus": ChatAnthropic(model_name="claude-opus-4-7"),
        "gpt-4": ChatOpenAI(model_name="gpt-4-turbo"),
    }.get(context.get("selected_model"), model),

    # Resposta estruturada: Forçar formato JSON
    response_format=ResponseFormat.json_schema({"type": "object"}),

    # Limits
    max_iterations=50,
    max_tokens=8000,
)
```

## System Prompt Assembly (Composição de Prompt)

Deep Agents compõe o system prompt em **4 partes**, garantindo que instruções do usuário tenham sempre precedência:

```text
┌─────────────────────────────────────────┐
│  USER                                   │  ← Instruções do usuário (máxima prioridade)
├─────────────────────────────────────────┤
│  BASE (ou CUSTOM se modelo especifica)  │  ← Default guidelines do Deep Agent
├─────────────────────────────────────────┤
│  SUFFIX                                 │  ← Tuning do modelo específico
└─────────────────────────────────────────┘

Ordem final: USER + BASE + SUFFIX (joined with \n\n)
```

### Exemplo Prático

```python
# Especificar system prompt customizado
agent = create_deep_agent(
    model=model,
    tools=[...],
    system_prompt="""Você é um revisor de código Python especializado em performance.
- Sempre procure por O(n²) loops
- Sugira caching quando houver recomputação
- Explique seu raciocínio com exemplos de código
""",  # ← USER segment
)

# Prompt final enviado ao modelo:
"""Você é um revisor de código Python especializado em performance.
- Sempre procure por O(n²) loops
- Sugira caching quando houver recomputação
- Explique seu raciocínio com exemplos de código

You are a deep agent, an AI assistant that helps users accomplish tasks using tools...
[BASE_AGENT_PROMPT inteiro]

[SUFFIX específico do modelo se aplicável]
"""
```

## Modelo e Provider Profiles

Deep Agents suporta **múltiplos modelos** via perfis, permitindo trocar modelos sem refatorar código:

### Harness Profiles (Modelos Específicos)

```python
from deepagents.profiles import HarnessProfile, HarnessProfileConfig

# Define comportamento específico para Claude Opus
opus_profile = HarnessProfile(
    id="claude-opus",
    model_name="claude-opus-4-7",
    base_system_prompt="Você é especialista em análise complexa...",
    system_prompt_suffix="Sempre forneça análises profundas.",
    config=HarnessProfileConfig(
        max_tokens=8000,
        temperature=0.2,  # Mais determinístico para análises
    )
)

# Registrar perfil
from deepagents import register_harness_profile
register_harness_profile(opus_profile)

# Usar: O agente usa perfil automaticamente
agent = create_deep_agent(
    model=ChatAnthropic(model_name="claude-opus-4-7"),  # Tipo dispara perfil
    tools=[...],
)
```

### Provider Profiles (Troca Dinâmica)

```python
# Permitir usuário escolher modelo em runtime
models_available = {
    "claude-opus": ChatAnthropic(model_name="claude-opus-4-7"),
    "gpt-4": ChatOpenAI(model_name="gpt-4-turbo"),
    "gemini": ChatVertexAI(model_name="gemini-2.0"),
}

def get_model_for_context(context):
    """Retorna modelo baseado em contexto (sessão, usuário, etc)."""
    selected = context.get("model_id", "claude-opus")
    return models_available.get(selected)

agent = create_deep_agent(
    model=models_available["claude-opus"],  # Default
    tools=[...],
    model_factory=get_model_for_context,
)
```

## Padrões Comuns

### Pattern 1: Agent com Contexto Persistente (Memory)

```python
from deepagents.middleware import MemoryMiddleware

agent = create_deep_agent(
    model=model,
    tools=[...],
    middleware=[
        MemoryMiddleware(
            buffer_tokens=3000,  # Manter até 3000 tokens de histórico
            summary_model=model,  # Usar mesmo modelo para resumos
        ),
    ],
)

# Em conversa longa, MemoryMiddleware automaticamente resumirá
# histórico antigo enquanto mantém últimas interações íntegras
```

### Pattern 2: Agent Restrito a Diretórios Específicos

```python
from deepagents.backends import FilesystemBackend
from deepagents.middleware import FilesystemMiddleware, FilesystemPermission

agent = create_deep_agent(
    model=model,
    tools=[file_read, file_write],
    backend=FilesystemBackend(root="/home/user/projects"),
    middleware=[
        FilesystemMiddleware(
            permissions=[
                # Leitura ilimitada em docs
                FilesystemPermission(path_pattern="/home/user/projects/docs/**", access="r"),
                # Escrita apenas em output/
                FilesystemPermission(path_pattern="/home/user/projects/output/**", access="rw"),
                # Proibir acesso a .env
                FilesystemPermission(path_pattern="/home/user/projects/.env", access=""),
            ]
        ),
    ],
)
```

### Pattern 3: Interrupção Humana (Human-in-the-Loop)

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

# Agente pede aprovação antes de executar ferramentas perigosas
def should_interrupt(state):
    """Retorna True se deve pedir aprovação humana."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls"):
        for call in last_message.tool_calls:
            if call.name in ["delete_file", "execute_script", "deploy"]:
                return True
    return False

agent = create_deep_agent(
    model=model,
    tools=[delete_file, execute_script, deploy],
    middleware=[
        HumanInTheLoopMiddleware(
            should_interrupt=should_interrupt,
        ),
    ],
)

# Execução:
# 1. Agente decide usar delete_file
# 2. Middleware detecta, pausa
# 3. Pede aprovação: "Deletar /importante.txt? [aprovar/recusar]"
# 4. Continua após resposta humana
```

## Performance e Otimização

### Token Counting e Límites

```python
from langchain_core.language_models import LLMSyntheticCacheProvider
from langgraph.cache.base import BaseCache

# Prompt caching reduz custos em agentes de longa duração
agent = create_deep_agent(
    model=ChatAnthropic(
        model_name="claude-opus-4-7",
        cache_creation_input_tokens=1000,  # Cachear bloco de 1000 tokens
    ),
    tools=[...],
)

# Token-aware memory: Resumir quando atingir limite
agent = create_deep_agent(
    model=model,
    tools=[...],
    middleware=[
        MemoryMiddleware(
            buffer_tokens=6000,  # Resumir história quando exceder
            summary_model=model,
        ),
    ],
)
```

### Timeout e Rate Limiting

```python
# Limitar iterações para evitar loops infinitos
agent = create_deep_agent(
    model=model,
    tools=[...],
    max_iterations=30,  # Máximo 30 rodadas de LLM + tool
)

# Timeout por ferramenta
@tool
def slow_api_call(url: str) -> str:
    """Chamar API (timeout 5 segundos)."""
    import requests
    return requests.get(url, timeout=5).text
```

## Debugging e Observabilidade

### Logging

```python
import logging

# Ativar debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("deepagents").setLevel(logging.DEBUG)

# Saída: Você verá cada middleware, tool call, estado, etc
```

### LangSmith Integration

```python
import os
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "..."
os.environ["LANGSMITH_PROJECT"] = "vectora-dev"

agent = create_deep_agent(...)

# Agora todas as execuções são rastreadas em langsmith.com
# Ver: full state traces, token counts, latency, errors
```

### State Inspection

```python
# Inspecionar estado completo após execução
state = agent.invoke(...)

# Campos úteis para debug:
print(f"Total messages: {len(state['messages'])}")
print(f"Tool calls executadas: {[m.tool_calls for m in state['messages']]}")
print(f"Última resposta: {state['messages'][-1].content}")
```

## External Linking

| Conceito             | Recurso                | Link                                                                          |
| -------------------- | ---------------------- | ----------------------------------------------------------------------------- |
| **LangGraph**        | Framework de estado    | [langchain.com/docs/langgraph](https://langchain.com/docs/langgraph/)         |
| **Deep Agents Docs** | Documentação oficial   | [langchain.com/deepagents](https://langchain.com/deepagents/)                 |
| **LangChain Tools**  | Criação de ferramentas | [langchain.com/docs/modules/tools](https://langchain.com/docs/modules/tools/) |
| **Claude API**       | Modelos Anthropic      | [claude.ai/claude-api](https://claude.ai/claude-api/)                         |
| **Prompt Caching**   | Cache de tokens        | [cloud.google.com/docs/caching](https://cloud.google.com/docs/caching/)       |
