---
title: Tools e Sistema de Ferramentas
slug: tools-and-execution
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - tools
  - functions
  - execution
  - langchain
  - vectora
---

{{< lang-toggle >}}

{{< section-toggle >}}

O **Tools System** é o mecanismo pelo qual Deep Agents (e Vectora) acessam o mundo externo: ler/escrever arquivos, executar comandos shell, fazer requisições HTTP, consultar bancos de dados, chamar APIs, etc. Tools são simplesmente **funções Python anotadas** que o agente pode chamar.

Diferentemente de usar funções diretamente, o sistema de tools fornece **segurança, transparência e rastreabilidade**: cada tool call é logado, pode ser aprovado por humanos, e pode ser interrompido se necessário. Além disso, ferramentas são compostas com middleware que aplica permissões, limites de rate, timeouts, e mais.

## Conceitos Fundamentais

### O que é uma Tool?

Uma tool é:

1. **Uma função Python** com tipos e docstring
2. **Anotada com `@tool`** para torná-la detectável
3. **Registrada no agente** para que ele saiba que existe
4. **Invocável pelo LLM** quando o agente julgar útil

```python
from langchain_core.tools import tool

@tool
def search_google(query: str) -> str:
    """Buscar no Google.

    Args:
        query: Termo a buscar (ex: 'python asyncio')

    Returns:
        Lista de resultados (URLs e snippets)
    """
    # Implementação real aqui
    return f"Encontrei 10 resultados para '{query}'"
```

### Como o Agente Vê Tools

O agente não executa a função diretamente. Em vez disso:

1. **LLM gera estrutura JSON** com nome, args, type
2. **Tool executor deserializa** e chama a função real
3. **Middleware intercede** para aplicar permissões, timeouts, etc
4. **Output é capturado** e retornado ao LLM como nova mensagem

```text
Agente pensa: "Preciso buscar sobre autenticação"
      ↓
LLM gera: {
  "type": "tool_call",
  "name": "search_google",
  "args": {"query": "JWT authentication 2026"}
}
      ↓
Tool Executor recebe JSON
      ↓
[Middleware Pipeline]
  - Check: user pode chamar search_google? ✓
  - Check: output ainda cabe em contexto? ✓
  - Check: timeout não foi atingido? ✓
      ↓
Execute: search_google(query="JWT authentication 2026")
      ↓
Capturar output: "Encontrei 5 artigos..."
      ↓
Retornar ao LLM: ToolMessage(content="Encontrei 5 artigos...")
```

## Criando Tools

### Padrão Básico

```python
from langchain_core.tools import tool

@tool
def my_tool(param1: str, param2: int = 5) -> str:
    """Breve descrição de uma linha.

    Descrição mais longa explicando em detalhes o que a tool faz,
    quando usar, restrições, etc.

    Args:
        param1: Descrição do primeiro parâmetro
        param2: Descrição do segundo parâmetro (default=5)

    Returns:
        Descrição do que é retornado

    Raises:
        ValueError: Quando algo inválido é passado
    """
    # Implementação
    return f"Processado: {param1} com {param2}"
```

**Regras importantes:**

- **Type hints obrigatórios** - LLM precisa saber tipos dos argumentos
- **Docstring obrigatória** - LLM usa para entender quando chamar
- **Args section** - Detalhar cada parâmetro
- **Returns section** - Descrever output
- **Raises section** - Documentar exceções

### Exemplos Práticos

#### 1. Ler arquivo

```python
@tool
def read_file(path: str) -> str:
    """Ler conteúdo de arquivo de texto.

    Suporta: .txt, .md, .py, .json, .yaml, etc.
    Nota: Binários retornam erro.

    Args:
        path: Caminho completo ao arquivo (ex: /home/user/doc.md)

    Returns:
        Conteúdo completo do arquivo como string

    Raises:
        FileNotFoundError: Arquivo não existe
        IsADirectoryError: Path é um diretório, não arquivo
        PermissionError: Sem permissão de leitura
    """
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```

#### 2. Fazer requisição HTTP

```python
@tool
def fetch_webpage(url: str, timeout: int = 10) -> str:
    """Fazer GET request e retornar HTML/conteúdo.

    Args:
        url: URL completa (ex: https://example.com/page)
        timeout: Timeout em segundos (default=10)

    Returns:
        Conteúdo HTML da página (primeiros 10KB)

    Raises:
        requests.Timeout: Request demorou mais que timeout
        requests.ConnectionError: Não conseguiu conectar
        ValueError: URL inválida
    """
    import requests

    headers = {"User-Agent": "Vectora-Agent/1.0"}
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text[:10000]
```

#### 3. Executar comando shell

```python
@tool
def run_command(command: str, timeout: int = 30) -> str:
    """Executar comando shell e retornar output.

    Apenas comandos em allowlist podem ser executados.
    Allowlist padrão: grep, find, head, tail, wc, ls, cat

    Args:
        command: Comando a executar (ex: 'grep "error" app.log')
        timeout: Timeout em segundos (default=30)

    Returns:
        Stdout do comando (primeiros 5KB)

    Raises:
        subprocess.TimeoutExpired: Comando excedeu timeout
        subprocess.CalledProcessError: Comando retornou exit code != 0
        PermissionError: Comando não está em allowlist
    """
    import subprocess

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, command, result.stdout, result.stderr
        )

    return result.stdout[:5000]
```

#### 4. Consultar banco de dados

```python
@tool
def query_database(sql: str, limit: int = 100) -> str:
    """Executar query SQL e retornar resultados.

    Apenas SELECTs são permitidos (read-only).

    Args:
        sql: Query SQL (ex: 'SELECT * FROM users WHERE status = "active"')
        limit: Máximo de linhas a retornar (default=100)

    Returns:
        Resultados em formato JSON Lines (1 objeto por linha)

    Raises:
        ValueError: Query contém INSERT/UPDATE/DELETE
        psycopg2.Error: Erro na execução da query
    """
    import psycopg2
    import json

    # Validar: apenas SELECT
    if not sql.strip().upper().startswith('SELECT'):
        raise ValueError("Apenas SELECTs são permitidos")

    conn = psycopg2.connect("dbname=vectora user=app")
    cursor = conn.cursor()
    cursor.execute(f"{sql} LIMIT {limit}")

    # Retornar como JSON Lines
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    result = []
    for row in rows:
        result.append(json.dumps(dict(zip(columns, row))))

    conn.close()
    return "\n".join(result)
```

#### 5. Tool assíncrona

```python
from langchain_core.tools import tool
import asyncio

@tool
async def async_api_call(endpoint: str, data: dict) -> str:
    """Chamar API externa (com async).

    Args:
        endpoint: URL do endpoint (ex: https://api.example.com/data)
        data: Dados JSON para enviar

    Returns:
        Response JSON como string
    """
    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=data) as resp:
            return await resp.text()

# Agente automaticamente detecta e trata async
agent = create_deep_agent(
    model=model,
    tools=[async_api_call],
)
```

## Registrando Tools no Agente

### Método 1: Passar lista ao criar agente

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model=model,
    tools=[
        read_file,
        write_file,
        search_google,
        run_command,
    ],
)
```

### Método 2: Descoberta automática (Skill Sources)

```python
from deepagents.middleware import SkillsMiddleware

# Todas as tools em /path/to/skills/ são carregadas automaticamente
agent = create_deep_agent(
    model=model,
    tools=[],  # Vazio - skills carregarão tools
    middleware=[
        SkillsMiddleware(
            sources=[
                "/home/user/.deepagents/skills",
                "project/custom-skills",
            ]
        ),
    ],
)
```

### Método 3: Registro dinâmico

```python
# Adicionar tool após criar agente
@tool
def new_tool(x: int) -> int:
    return x * 2

# Recriar agente com nova tool
agent.tools.append(new_tool)
```

## Middleware de Tools (Permissões, Timeouts, Rate Limiting)

### Filtragem por Permissão

```python
from deepagents.middleware import _ToolExclusionMiddleware

# Alguns users não podem usar certas tools
excluded_tools_per_user = {
    "user_1": ["delete_file", "execute_script"],
    "user_2": ["run_command"],
    "admin": [],  # Admin pode usar tudo
}

def get_excluded_tools(context):
    user = context.get("user_id")
    return excluded_tools_per_user.get(user, [])

agent = create_deep_agent(
    model=model,
    tools=[...],
    middleware=[
        _ToolExclusionMiddleware(
            get_excluded_tools=get_excluded_tools,
        ),
    ],
)

# Resultado: Se user_1 tenta chamar delete_file, middleware intercepta e recusa
```

### Timeout por Tool

```python
# Deep Agents suporta timeout em tools específicas
@tool
def slow_operation(data: str) -> str:
    """Operação que pode demorar."""
    # Será interrompida após 30 segundos
    return process_slow(data)

# No agente:
agent = create_deep_agent(
    model=model,
    tools=[slow_operation],
)

# Deep Agents automaticamente limita execução a max_iterations
# e aplica timeout geral. Para timeout por tool individual,
# use try/except com signal ou asyncio.wait_for()
```

### Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_minute: int):
    """Decorator para rate limit."""
    min_interval = 60 / calls_per_minute
    last_call = [0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

            result = func(*args, **kwargs)
            last_call[0] = time.time()
            return result
        return wrapper
    return decorator

@tool
@rate_limit(calls_per_minute=10)
def api_call(endpoint: str) -> str:
    """API com max 10 calls por minuto."""
    return requests.get(endpoint).text
```

## Padrões Avançados

### Pattern 1: Tool com Fallback

```python
@tool
def search_primary(query: str) -> str:
    """Buscar em índice primário (rápido)."""
    try:
        return elasticsearch_client.search(query)
    except Exception as e:
        # Fallback para busca secundária
        return search_fallback(query)

def search_fallback(query: str) -> str:
    """Busca em índice secundário (mais lento mas confiável)."""
    return database.search_full_text(query)
```

### Pattern 2: Tool que Retorna Diferentes Formatos

```python
from enum import Enum

class Format(str, Enum):
    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"

@tool
def export_data(table: str, format: Format = Format.JSON) -> str:
    """Exportar dados em diferentes formatos.

    Args:
        table: Nome da tabela (users, products, etc)
        format: Formato output (json, csv, markdown)

    Returns:
        Dados formatados
    """
    data = db.fetch(table)

    if format == Format.JSON:
        return json.dumps(data)
    elif format == Format.CSV:
        return to_csv(data)
    elif format == Format.MARKDOWN:
        return to_markdown_table(data)
```

### Pattern 3: Tool Composta (Wrapper de Múltiplas Operações)

```python
@tool
def analyze_and_report(file_path: str, output_format: str = "md") -> str:
    """Analisar arquivo e gerar relatório completo.

    Internamente usa múltiplas tools (read, process, format).
    Útil para operações complexas que devem ser "atômicas".
    """
    # Step 1: Ler
    content = read_file(file_path)

    # Step 2: Processar
    analysis = {
        "lines": len(content.split('\n')),
        "words": len(content.split()),
        "patterns": find_patterns(content),
    }

    # Step 3: Formatar
    if output_format == "md":
        report = f"""# Análise de {file_path}
- Linhas: {analysis['lines']}
- Palavras: {analysis['words']}
- Padrões: {analysis['patterns']}
"""
    else:
        report = json.dumps(analysis)

    return report
```

### Pattern 4: Tool com Validação e Transformação

```python
from typing import Literal

@tool
def transform_data(
    input_data: str,
    transformation: Literal["uppercase", "lowercase", "reverse", "json-format"],
) -> str:
    """Transformar dados em várias formas.

    Args:
        input_data: Dados brutos a transformar
        transformation: Tipo de transformação a aplicar

    Returns:
        Dados transformados

    Raises:
        ValueError: Transformação inválida
    """
    if transformation == "uppercase":
        return input_data.upper()
    elif transformation == "lowercase":
        return input_data.lower()
    elif transformation == "reverse":
        return input_data[::-1]
    elif transformation == "json-format":
        try:
            parsed = json.loads(input_data)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido: {e}")
    else:
        raise ValueError(f"Transformação desconhecida: {transformation}")
```

## Debugging e Observabilidade

### Ver Tools Disponíveis

```python
# Inspecionar tools do agente
agent = create_deep_agent(...)

for tool in agent.tools:
    print(f"Tool: {tool.name}")
    print(f"  Descrição: {tool.description}")
    print(f"  Argumentos: {tool.args}")
```

### Logging de Tool Calls

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("deepagents.tools")

# Agora você verá:
# [DEBUG] Tool call: read_file, args: {'path': '/home/user/doc.md'}
# [DEBUG] Tool output: 234 bytes
# [DEBUG] Tool call: search_google, args: {'query': 'JWT auth'}
# [DEBUG] Tool error: Timeout exceeded after 30s
```

### Rastreamento com LangSmith

```python
import os
os.environ["LANGSMITH_API_KEY"] = "..."
os.environ["LANGSMITH_PROJECT"] = "vectora-dev"

agent = create_deep_agent(...)

# Todos os tool calls serão rastreados em langsmith.com
# Você verá: timing, inputs, outputs, erros
```

## External Linking

| Conceito            | Recurso              | Link                                                                          |
| ------------------- | -------------------- | ----------------------------------------------------------------------------- |
| **LangChain Tools** | Criação de tools     | [langchain.com/docs/modules/tools](https://langchain.com/docs/modules/tools/) |
| **Pydantic**        | Type validation      | [docs.pydantic.dev](https://docs.pydantic.dev/)                               |
| **JSON Schema**     | Tool specs           | [json-schema.org](https://json-schema.org/)                                   |
| **OpenAPI**         | Tool standardization | [openapis.org](https://www.openapis.org/)                                     |
| **LangSmith**       | Rastreamento         | [smith.langchain.com](https://smith.langchain.com/)                           |
