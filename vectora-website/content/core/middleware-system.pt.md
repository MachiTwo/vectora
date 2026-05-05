---
title: Middleware System
slug: middleware-system
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - middleware
  - pipelines
  - memory
  - permissions
  - skills
  - vectora
---

{{< lang-toggle >}}

{{< section-toggle >}}

**Middleware** são componentes que interceptam e modificam o fluxo de execução do agente. Cada middleware recebe o estado do agente em cada iteração, pode inspecioná-lo, modificá-lo, ou interromper a execução. A pilha de middleware forma uma **cadeia de responsabilidade** onde cada middleware processa o estado antes do próximo.

Diferentemente de ferramentas (que o agente decide chamar), middleware são **sempre ativas** e transparentes. São usadas para: controlar permissões, gerenciar memória, resolver skills em tool calls, delegar para subagentes, resumir contexto, e mais.

## Arquitetura de Middleware

### Fluxo de Execução

```text
Input do usuário
    ↓
┌─────────────────────────────────────┐
│  Middleware 1: FilesystemMiddleware │
│  - Validar permissões de arquivo    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Middleware 2: PermissionsMiddleware │
│  - Validar se pode chamar tool X    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Middleware 3: SkillsMiddleware      │
│  - Expandir @skill em tool calls    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Middleware 4: MemoryMiddleware      │
│  - Resumir histórico se muito longo │
└─────────────────────────────────────┘
    ↓
LLM Call (com estado processado por todos os middlewares)
    ↓
Tool Execution
    ↓
[Mesmo pipeline acima]
    ↓
Output final
```

### Interface Middleware

Todos os middleware implementam:

```python
from langchain.agents.middleware.types import AgentMiddleware, ResponseT
from typing import Any

class CustomMiddleware(AgentMiddleware):
    def process_input(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """Processar estado ANTES do LLM."""
        # Inspecionar/modificar estado
        return state

    def process_output(
        self,
        state: dict[str, Any],
        response: ResponseT,
    ) -> tuple[dict[str, Any], ResponseT]:
        """Processar estado e output APÓS o LLM."""
        # Modificar response ou estado
        return state, response
```

## MemoryMiddleware (Gerenciar Contexto)

**Uso:** Controlar tamanho da janela de contexto resumindo histórico longo.

```python
from deepagents.middleware import MemoryMiddleware

middleware = MemoryMiddleware(
    buffer_tokens=3000,  # Manter até 3000 tokens no buffer
    summary_model=model,  # Usar mesmo modelo para resumos
    threshold_tokens=4000,  # Resumir quando contexto > 4000
)

agent = create_deep_agent(
    model=model,
    tools=[...],
    middleware=[middleware],
)

# Comportamento:
# Conversa 1 (800 tokens): Mantém íntegra
# Conversa 2 (1500 tokens): Mantém íntegra
# Conversa 3 (1600 tokens): TOTAL = 3900 → Resumir antigas
# → Agora: [SUMMARY de Conv 1+2] + Conv 3
```

### Implementação Simplificada

```python
class MemoryMiddleware(AgentMiddleware):
    def __init__(
        self,
        buffer_tokens: int,
        summary_model: BaseChatModel,
    ):
        self.buffer_tokens = buffer_tokens
        self.summary_model = summary_model

    def process_input(self, state: dict[str, Any]) -> dict[str, Any]:
        messages = state["messages"]

        # Calcular tokens totais
        total_tokens = sum(
            len(msg.content.split()) * 1.3  # Estimativa
            for msg in messages
        )

        # Se exceder limite, resumir
        if total_tokens > self.buffer_tokens:
            # Manter últimas N mensagens intactas
            keep_recent = messages[-5:]

            # Resumir as antigas
            old_messages = messages[:-5]
            summary = self._summarize_messages(old_messages)

            # Substituir antigas por resumo
            state["messages"] = [
                SystemMessage(content=f"Resumo anterior:\n{summary}"),
                *keep_recent,
            ]

        return state

    def _summarize_messages(self, messages: list) -> str:
        """Usar LLM para resumir histórico."""
        # Formatar histórico
        history_text = "\n".join(
            f"{m.type}: {m.content[:100]}..." for m in messages
        )

        # Chamar LLM
        response = self.summary_model.invoke([
            SystemMessage("Resuma esta conversa em 2-3 sentenças."),
            HumanMessage(history_text),
        ])

        return response.content
```

### Quando Usar

```text
Use MemoryMiddleware para:
✓ Conversas longas (100+ mensagens)
✓ Agentes que falam demais
✓ Controlar custos de tokens
✓ Manter contexto dentro de limites do modelo

Evitar quando:
✗ Conversa curta (<20 mensagens)
✗ Precisa lembrar detalhes específicos (resumo perde)
✗ Task crítica onde perda de contexto é problema
```

## FilesystemMiddleware (Controlar Acesso)

**Uso:** Aplicar permissões granulares ao acesso de arquivos.

```python
from deepagents.middleware import FilesystemMiddleware, FilesystemPermission

middleware = FilesystemMiddleware(
    permissions=[
        # Padrão 1: Diretório de leitura
        FilesystemPermission(
            path_pattern="/home/user/documents/**",
            access="r",  # read-only
        ),
        # Padrão 2: Diretório de leitura/escrita
        FilesystemPermission(
            path_pattern="/home/user/output/**",
            access="rw",  # read-write
        ),
        # Padrão 3: Proibir arquivo específico
        FilesystemPermission(
            path_pattern="/home/user/.ssh/id_rsa",
            access="",  # proibido
        ),
    ]
)

agent = create_deep_agent(
    model=model,
    tools=[read_file, write_file],
    middleware=[middleware],
)

# Comportamento:
# read_file("/home/user/documents/guide.md") → ✓
# write_file("/home/user/documents/guide.md") → ✗ read-only
# write_file("/home/user/output/result.txt") → ✓
# read_file("/home/user/.ssh/id_rsa") → ✗ proibido
```

### Path Pattern Matching

```python
# Exatos
FilesystemPermission("/home/user/secret.txt", "")

# Wildcards
FilesystemPermission("/home/user/documents/*.md", "r")
FilesystemPermission("/home/user/projects/**/data", "rw")

# Ranges (números)
FilesystemPermission("/data/2024/**/*.csv", "r")
FilesystemPermission("/archive/[2020-2023]/**", "")
```

## SkillsMiddleware (Reusable Components)

**Uso:** Permitir agente usar "skills" (conjuntos pré-definidos de ferramentas).

Um skill é um pacote com:

- Descrição
- Ferramentas que fornece
- Setup/teardown
- Dependências

```python
from deepagents.middleware import SkillsMiddleware

middleware = SkillsMiddleware(
    sources=[
        "/home/user/.deepagents/skills",
        "project/custom-skills",
    ]
)

agent = create_deep_agent(
    model=model,
    tools=[],  # Skills carregam ferramentas
    middleware=[middleware],
)

# Agora agente pode usar: @skill-name
```

### Estrutura de Skill

```text
my-skill/
├── SKILL.md          # Metadados
├── __init__.py       # Código
└── tools.py          # Ferramentas fornecidas
```

**SKILL.md:**

```markdown
---
name: "web-scraper"
description: "Scrape e analisa websites"
version: "1.0.0"
tools:
  - fetch_webpage
  - extract_text
  - find_links
dependencies: []
---

Skill para scraping de websites com análise de conteúdo.
```

**tools.py:**

```python
from langchain_core.tools import tool

@tool
def fetch_webpage(url: str) -> str:
    """Buscar webpage."""
    import requests
    return requests.get(url).text

@tool
def extract_text(html: str) -> str:
    """Extrair texto do HTML."""
    from html.parser import HTMLParser
    # ... implementação
    return text
```

### Usando Skills

```text
> Você: Use @web-scraper para analisar exemplo.com

[SkillsMiddleware resolve @web-scraper]
↓
Carrega tools: fetch_webpage, extract_text, find_links
↓
Agente agora tem acesso a essas ferramentas
↓
Agente: Vou usar fetch_webpage para buscar exemplo.com
```

## SubAgentMiddleware (Delegar Tarefas)

**Uso:** Delegar sub-tarefas para agentes especializados.

Um subagente é um agente menor otimizado para tarefa específica.

```python
from deepagents import create_deep_agent, SubAgent, SubAgentMiddleware
from deepagents.middleware import SubAgentMiddleware

# Definir subagentes
code_reviewer = SubAgent(
    name="code-reviewer",
    system_prompt="Você revisa código Python...",
    tools=[read_file, analyze_ast],
)

documentor = SubAgent(
    name="documentor",
    system_prompt="Você gera documentação...",
    tools=[read_file, format_markdown],
)

# Agente principal
middleware = SubAgentMiddleware(
    subagents=[code_reviewer, documentor],
)

agent = create_deep_agent(
    model=model,
    tools=[main_tool1, main_tool2],
    middleware=[middleware],
)

# Uso:
# > Você: Revisa app.py e gera documentação

# Agente: Vou usar code_reviewer para revisar
#         e documentor para gerar docs
#
# [Delega para code_reviewer: app.py]
# [Delega para documentor: gerar docs]
```

### Definindo SubAgents

```python
from deepagents import SubAgent, SubAgentMiddleware

code_reviewer = SubAgent(
    name="code-reviewer",
    description="Especialista em revisão de código Python",
    system_prompt="""Você é especialista em análise de código Python.
- Foco em: performance, segurança, maintainability
- Sugira melhorias específicas com exemplos
- Cite patterns padrão da comunidade Python
""",
    tools=[read_file, grep, syntax_check],
    max_iterations=20,
)

# Registrar com middleware
middleware = SubAgentMiddleware(subagents=[code_reviewer])

agent = create_deep_agent(
    model=model,
    middleware=[middleware],
)
```

## Middleware Customizado

### Exemplo 1: Logging Middleware

```python
from langchain.agents.middleware.types import AgentMiddleware
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(AgentMiddleware):
    """Log todas as operações do agente."""

    def process_input(self, state: dict) -> dict:
        user_message = state["messages"][-1].content
        logger.info(f"User: {user_message[:100]}")
        return state

    def process_output(self, state: dict, response):
        if hasattr(response, "tool_calls"):
            for call in response.tool_calls:
                logger.info(f"Tool call: {call.name}")
        else:
            logger.info(f"Response: {response.content[:100]}")
        return state, response
```

### Exemplo 2: Rate Limiting Middleware

```python
import time
from collections import defaultdict

class RateLimitMiddleware(AgentMiddleware):
    """Limitar requisições por usuário."""

    def __init__(self, max_calls_per_minute: int = 10):
        self.max_calls = max_calls_per_minute
        self.calls_per_user = defaultdict(list)

    def process_input(self, state: dict) -> dict:
        user_id = state.get("metadata", {}).get("user_id", "unknown")
        now = time.time()

        # Limpar calls antigas
        self.calls_per_user[user_id] = [
            t for t in self.calls_per_user[user_id]
            if now - t < 60
        ]

        # Verificar limite
        if len(self.calls_per_user[user_id]) >= self.max_calls:
            raise RuntimeError(
                f"Rate limit exceeded for user {user_id}. "
                f"Max {self.max_calls} calls per minute."
            )

        # Registrar call
        self.calls_per_user[user_id].append(now)

        return state
```

### Exemplo 3: Content Filter Middleware

```python
class ContentFilterMiddleware(AgentMiddleware):
    """Filtrar conteúdo inapropriado."""

    def __init__(self, blocked_patterns: list[str]):
        self.blocked_patterns = blocked_patterns

    def process_output(self, state: dict, response):
        content = response.content if hasattr(response, "content") else str(response)

        for pattern in self.blocked_patterns:
            if pattern.lower() in content.lower():
                # Filtrar resposta
                response.content = "[Conteúdo filtrado]"
                break

        return state, response
```

## Composição de Middleware

### Pipeline Típico (Dev)

```python
agent = create_deep_agent(
    model=model,
    tools=[...],
    middleware=[
        FilesystemMiddleware(permissions=[...]),
        SkillsMiddleware(sources=[...]),
        MemoryMiddleware(buffer_tokens=3000),
    ],
)
```

### Pipeline Típico (Produção)

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

agent = create_deep_agent(
    model=model,
    tools=[...],
    middleware=[
        # Segurança em primeiro
        FilesystemMiddleware(permissions=[...]),

        # Monitoramento
        LoggingMiddleware(),
        RateLimitMiddleware(max_calls_per_minute=100),

        # Funcionalidades
        SkillsMiddleware(sources=[...]),
        SubAgentMiddleware(subagents=[...]),
        MemoryMiddleware(buffer_tokens=3000),

        # Aprovação final
        HumanInTheLoopMiddleware(
            should_interrupt=lambda state: state.get("needs_approval", False)
        ),
    ],
)
```

## Debugging Middleware

### Inspecionar Middleware Stack

```python
agent = create_deep_agent(...)

# Ver middleware em uso
for middleware in agent.middleware:
    print(f"Middleware: {middleware.__class__.__name__}")
    print(f"  Config: {middleware.__dict__}")
```

### Ativar Debug Logging

```python
import logging

logging.getLogger("deepagents.middleware").setLevel(logging.DEBUG)

# Saída:
# [DEBUG] FilesystemMiddleware: Checking permission for /home/user/file.txt
# [DEBUG] FilesystemMiddleware: Permission: r (read-only) - ALLOWED
# [DEBUG] MemoryMiddleware: Context size 3200 tokens (limit 3000)
# [DEBUG] MemoryMiddleware: Summarizing historical messages...
```

## Performance Impact

```text
Middleware Overhead (por LLM call):

FilesystemMiddleware: <5ms (regex matching)
MemoryMiddleware: 100-500ms (se resumindo com LLM)
SkillsMiddleware: 10-50ms (carregamento de skills)
SubAgentMiddleware: 0ms (decision em LLM)
CustomMiddleware: Depende implementação

Recomendação:
- Manter <3 middleware no hot path
- Mover operações pesadas para async quando possível
- Cache resultados de middleware quando aplicável
```

## External Linking

| Conceito                            | Recurso        | Link                                                                                                                                  |
| ----------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Chain of Responsibility Pattern** | Design pattern | [refactoring.guru/design-patterns/chain-of-responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility)          |
| **LangChain Middleware**            | Official docs  | [langchain.com/docs/modules/agents/middleware](https://langchain.com/docs/modules/agents/middleware/)                                 |
| **Permission Systems**              | Best practices | [cheatsheetseries.owasp.org/cheatsheets/Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) |
| **Token Counting**                  | LangChain      | [langchain.com/docs/guides/token-counting](https://langchain.com/docs/guides/token-counting/)                                         |
| **LangSmith Monitoring**            | Observability  | [smith.langchain.com](https://smith.langchain.com/)                                                                                   |
