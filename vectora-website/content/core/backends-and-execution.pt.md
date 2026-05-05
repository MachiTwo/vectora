---
title: Backends e Ambientes de Execução
slug: backends-and-execution
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - backends
  - filesystem
  - sandbox
  - execution
  - vectora
---

{{< lang-toggle >}}

{{< section-toggle >}}

**Backends** definem como Deep Agents executam operações no mundo real: ler/escrever arquivos, executar comandos shell, interagir com storage. Escolher o backend certo é crítico para segurança, performance, e controle do agente em ambientes de produção.

Vectora fornece múltiplos backends para diferentes cenários. Um agente pode usar um backend único (simples) ou combinar múltiplos via CompositeBackend (flexível). A escolha depende de: segurança necessária, performance, ambiente de execução, e permissões.

## Hierarquia de Backends

```text
┌──────────────────────────────┐
│   Backend Protocol (Interface)│
│   - read(), write()          │
│   - execute()                │
│   - ls(), glob()             │
│   - grep()                   │
└──────────────────────────────┘
              ↑
   ┌──────────┼──────────┬──────────┐
   │          │          │          │
FilesystemLocal      State        Store
Backend         Backend          Backend
│          │          │          │
│          │          │          └─ Storage (sem execução)
│          │          └─ State apenas (testes)
│          └─ Shell local (sem sandbox)
└─ Arquivo local (sem shell)

CompositeBackend: Combina múltiplos para máxima flexibilidade
```

## Backend: FilesystemBackend

**Uso:** Trabalhar com arquivos e diretórios no filesystem local.

**Segurança:** Baixa (sem isolamento de processo). Usa permissões do SO.

```python
from deepagents.backends import FilesystemBackend

# Criar backend
backend = FilesystemBackend(
    root="/home/user/projects",  # Root dir (chroot-like)
    allowed_extensions=[".py", ".md", ".json", ".txt"],
)

# Usar com agente
agent = create_deep_agent(
    model=model,
    tools=[read_file, write_file, list_files],
    backend=backend,
)

# Comportamento:
# - read_file("/home/user/projects/app.py") → funciona
# - read_file("/etc/passwd") → ERRO (fora de root)
# - read_file("/home/user/projects/secret.bin") → ERRO (extensão não permitida)
# - write_file(...) → cria/modifica arquivo
```

### Implementação Detalhada

```python
class FilesystemBackend(SandboxBackendProtocol):
    def __init__(self, root: str, allowed_extensions: list[str] = None):
        self.root = Path(root).resolve()
        self.allowed_extensions = allowed_extensions or []

    def read(self, path: str) -> str:
        """Ler arquivo (relativo a root)."""
        full_path = (self.root / path).resolve()

        # Validações
        if not str(full_path).startswith(str(self.root)):
            raise PermissionError(f"Path {path} está fora de {self.root}")

        if self.allowed_extensions:
            ext = full_path.suffix
            if ext not in self.allowed_extensions:
                raise ValueError(f"Extensão {ext} não permitida")

        return full_path.read_text(encoding='utf-8')

    def write(self, path: str, content: str) -> None:
        """Escrever arquivo."""
        full_path = (self.root / path).resolve()

        if not str(full_path).startswith(str(self.root)):
            raise PermissionError(f"Path {path} está fora de {self.root}")

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')

    def list_directory(self, path: str = ".") -> list[str]:
        """Listar diretório."""
        full_path = (self.root / path).resolve()
        return [str(p.relative_to(self.root)) for p in full_path.iterdir()]
```

### Casos de Uso

| Caso                | Config                                            |
| ------------------- | ------------------------------------------------- |
| **Dev local**       | `root="/home/dev/project"` sem restrictions       |
| **Blogar escritor** | `root="/home/writer/articles"`, allow [.md, .jpg] |
| **Code reviewer**   | `root="/workspace"`, read-only (via middleware)   |
| **Data processor**  | `root="/data"`, allow [.csv, .json]               |

## Backend: LocalShellBackend

**Uso:** Executar comandos shell locais (grep, find, head, etc).

**Segurança:** Média (com allowlist de comandos).

```python
from deepagents.backends import LocalShellBackend

backend = LocalShellBackend(
    allowed_commands=[
        "grep",
        "find",
        "head",
        "tail",
        "wc",
        "ls",
        "cat",
        "sed",
        "awk",
    ],
    timeout_seconds=30,
)

agent = create_deep_agent(
    model=model,
    tools=[execute_command],
    backend=backend,
)

# Comportamento:
# - execute_command("grep 'error' app.log") → ✓ funciona
# - execute_command("find . -name '*.py'") → ✓ funciona
# - execute_command("rm -rf /") → ✗ comando não em allowlist
# - execute_command("python exploit.py") → ✗ 'python' não permitido
```

### Security: Allowlist Pattern

```python
# RESTRICTIVO (mais seguro, menos útil)
secure_backend = LocalShellBackend(
    allowed_commands=[
        "grep",
        "find",
        "wc",
        "head",
    ],
)

# PERMISSIVO (menos seguro, mais útil)
dev_backend = LocalShellBackend(
    allowed_commands=[
        # Read-only
        "cat", "head", "tail", "wc", "grep", "find", "ls",
        # Analysis
        "file", "stat", "du",
        # Git (read-only)
        "git log", "git show", "git diff",
        # Build
        "npm run build",
        "pytest tests/",
    ],
)

# CUSTOM: dinâmico
def get_allowed_commands(context):
    user = context.get("user_id")
    if user in ["admin", "devops"]:
        # Admins podem rodar mais comandos
        return ["*"]  # Todos os comandos
    else:
        # Users normais tem restrictions
        return ["grep", "find", "ls"]

backend = LocalShellBackend(
    allowed_commands_func=get_allowed_commands,
)
```

### Implementação Simplificada

```python
class LocalShellBackend:
    def __init__(self, allowed_commands: list[str], timeout_seconds: int = 30):
        self.allowed_commands = allowed_commands
        self.timeout = timeout_seconds

    def execute(self, command: str) -> ExecuteResponse:
        """Executar comando shell."""
        # Validar comando em allowlist
        cmd_name = command.split()[0]
        if cmd_name not in self.allowed_commands:
            raise PermissionError(f"Comando '{cmd_name}' não permitido")

        # Executar com timeout
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            return ExecuteResponse(
                output=result.stdout,
                exit_code=result.returncode,
                truncated=len(result.stdout) > 5000,
            )
        except subprocess.TimeoutExpired:
            return ExecuteResponse(
                output=f"Comando excedeu timeout de {self.timeout}s",
                exit_code=124,
            )
```

## Backend: SandboxBackend

**Uso:** Execução isolada e segura em Docker/containers.

**Segurança:** Alta (processo isolado, filesystem vazio inicialmente).

```python
from deepagents.backends import SandboxBackend

# Criar ambiente isolado em Docker
backend = SandboxBackend(
    image="python:3.11",  # Imagem Docker para executar
    mount_paths={
        "/work": "/home/user/project",  # Mount projeto de leitura
    },
    environment={
        "PYTHONUNBUFFERED": "1",
        "API_KEY": "...",
    },
    timeout_seconds=60,
)

agent = create_deep_agent(
    model=model,
    tools=[execute_in_sandbox],
    backend=backend,
)

# Uso:
# execute_in_sandbox("python train.py --epochs 10")
# → Roda em container isolado, sem acesso à máquina host
```

### Quando Usar SandboxBackend

```text
✓ Usar SandboxBackend para:
  - Executar código não confiável
  - Rodar scripts que podem crashar
  - Isolamento total de filesystem
  - Control de recursos (CPU, memória)
  - Agentes deployados para múltiplos usuários

✗ Não usar para:
  - Desenvolvimento local (overhead)
  - Acesso a hardware específico
  - Performance crítica
  - Comunicação com processos locais
```

## Backend: StateBackend

**Uso:** Apenas persistência de estado (para testes, sem execução).

**Segurança:** Máxima (nenhuma operação real executada).

```python
from deepagents.backends import StateBackend

backend = StateBackend()

agent = create_deep_agent(
    model=model,
    tools=[...],
    backend=backend,
)

# Comportamento:
# - Agente não pode ler/escrever arquivos reais
# - Agente não pode executar comandos reais
# - Apenas armazena/carrega estado
# - Útil para: testes, simulação, análise de prompts
```

### Caso de Uso: Testing

```python
def test_agent_decides_correctly():
    """Testar que agente toma decisões corretas."""
    from langgraph.checkpoint.memory import MemorySaver

    backend = StateBackend()
    agent = create_deep_agent(
        model=model,
        tools=[read_file, write_file],
        backend=backend,
    )

    state = agent.invoke({
        "messages": [{"role": "user", "content": "Análisa performance.py"}]
    })

    # Verificar: agente tentou chamar read_file?
    tool_calls = [m.tool_calls for m in state["messages"]]
    assert any(tc.name == "read_file" for tc in tool_calls), \
        "Agente deveria ler arquivo"
```

## Backend: StoreBackend

**Uso:** Persistência de dados estruturados (similar a StateBackend).

**Segurança:** Alta (apenas armazenamento, sem execução).

```python
from deepagents.backends import StoreBackend
from langgraph.store.base import BaseStore

class CustomStore(BaseStore):
    """Implementação customizada de store."""
    def put(self, namespace: list[str], key: str, value: Any) -> None:
        # Armazenar valor
        pass

    def get(self, namespace: list[str], key: str) -> Any:
        # Recuperar valor
        pass

backend = StoreBackend(store=CustomStore())

agent = create_deep_agent(
    model=model,
    tools=[...],
    backend=backend,
)
```

## Backend: CompositeBackend (Combinar)

**Uso:** Usar múltiplos backends simultaneamente para máxima flexibilidade.

```python
from deepagents.backends import CompositeBackend, FilesystemBackend, LocalShellBackend

backend = CompositeBackend([
    FilesystemBackend(root="/home/user/work"),
    LocalShellBackend(allowed_commands=["grep", "find", "git"]),
])

agent = create_deep_agent(
    model=model,
    tools=[read_file, write_file, execute_command],
    backend=backend,
)

# Cada backend trata seu tipo de operação:
# - FilesystemBackend: read_file, write_file, list_files
# - LocalShellBackend: execute_command
```

### Composição Avançada

```python
from deepagents.backends import (
    CompositeBackend, FilesystemBackend, LocalShellBackend,
    StateBackend
)

# Staging backend: combine diferentes ambientes
def create_staging_backend():
    return CompositeBackend([
        # Acesso ao código (leitura)
        FilesystemBackend(
            root="/home/app/src",
            allowed_extensions=[".py", ".md"],
        ),
        # Acesso a dados (leitura/escrita)
        FilesystemBackend(
            root="/home/app/data",
            allowed_extensions=[".csv", ".json"],
        ),
        # Comandos seguros
        LocalShellBackend(
            allowed_commands=["grep", "find", "git log", "pytest"],
        ),
    ])

agent = create_deep_agent(
    model=model,
    tools=[...],
    backend=create_staging_backend(),
)
```

## Interação Backend com Middleware

Backends definem **O QUE** é possível fazer. Middleware definem **COMO** é feito (permissões, rate limiting, logging).

```text
Tool Call
    ↓
Middleware Valida (Permissions, Rate Limiting, Timeouts)
    ↓
Backend Executa
    ↓
Middleware Processa Output (Summarize, Cache, Log)
    ↓
Retorna ao Agente
```

### Exemplo: Filesystem Backend + Permission Middleware

```python
from deepagents.middleware import FilesystemMiddleware, FilesystemPermission
from deepagents.backends import FilesystemBackend

backend = FilesystemBackend(root="/home/user/work")

middleware = FilesystemMiddleware(
    permissions=[
        FilesystemPermission(
            path_pattern="/home/user/work/docs/**",
            access="r",  # read-only
        ),
        FilesystemPermission(
            path_pattern="/home/user/work/output/**",
            access="rw",  # read-write
        ),
    ]
)

agent = create_deep_agent(
    model=model,
    tools=[read_file, write_file],
    backend=backend,
    middleware=[middleware],
)

# Resultado:
# read_file("/home/user/work/docs/guide.md") → ✓
# write_file("/home/user/work/docs/guide.md") → ✗ (read-only)
# write_file("/home/user/work/output/result.txt") → ✓
# read_file("/etc/passwd") → ✗ (fora de root)
```

## Debugging Backends

### Logging

```python
import logging

logging.getLogger("deepagents.backends").setLevel(logging.DEBUG)

# Saída:
# [DEBUG] FilesystemBackend: read /home/user/work/app.py
# [DEBUG] FilesystemBackend: 2340 bytes read
# [DEBUG] LocalShellBackend: execute grep 'error' app.log
# [DEBUG] LocalShellBackend: output 45 lines, exit code 0
```

### Inspecionar Backend

```python
agent = create_deep_agent(...)

# Ver que backend está em uso
print(agent.backend)
# output: FilesystemBackend(root=/home/user/work)

# Se CompositeBackend
if hasattr(agent.backend, 'backends'):
    for sub_backend in agent.backend.backends:
        print(f"  - {sub_backend}")
```

## Performance Considerations

### Filesystem vs. Shell: Benchmark

```text
Operation: Read 1MB file 10 vezes

FilesystemBackend:
  - Tempo médio: 45ms
  - Sem overhead
  - Direto em memória

LocalShellBackend (via cat):
  - Tempo médio: 120ms
  - Overhead de subprocess
  - Output parsing
  - Limite de output (5KB default)

SandboxBackend (via Docker):
  - Tempo médio: 500ms+
  - Overhead de container startup
  - Network overhead se remoto
  - Mas máxima segurança
```

### Otimizações

```python
# 1. Cachear leituras frequentes
from functools import lru_cache

@lru_cache(maxsize=100)
def read_file_cached(path: str) -> str:
    backend = get_current_backend()
    return backend.read(path)

# 2. Batch operations
def read_multiple_files(paths: list[str]) -> dict:
    """Ler múltiplos arquivos (mais eficiente que um a um)."""
    backend = get_current_backend()
    return {path: backend.read(path) for path in paths}

# 3. Usar shell para operações complexas
# Em vez de: read_file -> parse -> filter -> analyze
# Use: execute("grep 'error' app.log | wc -l")
```

## External Linking

| Conceito                | Recurso             | Link                                                                               |
| ----------------------- | ------------------- | ---------------------------------------------------------------------------------- |
| **LangChain Backends**  | Especificação       | [langchain.com/docs/backends](https://langchain.com/docs/backends/)                |
| **Docker Security**     | Container isolation | [docker.com/security](https://www.docker.com/security/)                            |
| **POSIX Permissions**   | File permissions    | [pubs.opengroup.org](https://pubs.opengroup.org/)                                  |
| **Linux Capabilities**  | Process permissions | [man7.org/capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html) |
| **Subprocess Security** | Python subprocess   | [docs.python.org/subprocess](https://docs.python.org/3/library/subprocess.html)    |
