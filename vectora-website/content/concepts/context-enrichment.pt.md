---
title: Context Enrichment
slug: context-enrichment
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - ast
  - code-analysis
  - context
  - dependencies
  - enrichment
  - vectora
---

{{< lang-toggle >}}

**Context Enrichment** é o processo de expandir o contexto recuperado com informações estruturais adicionais: dependências, relacionamentos entre módulos, tipos, e metadados semânticos. Sem enriquecimento, o agente tem apenas snippets isolados.

## Exemplo: Sem vs Com Enriquecimento

### Sem Enriquecimento

```python
# Query: "Como funciona autenticação?"
# Resultado: 1 chunk isolado

{
    "file": "auth.py",
    "content": "def verify_token(token: str) -> dict: ...",
    "embedding": [...],
}
```

Problema: Falta contexto de **donde token vem**, **qual algoritmo é usado**, **dependências**.

### Com Enriquecimento

```python
{
    "file": "auth.py",
    "content": "def verify_token(token: str) -> dict: ...",
    "embedding": [...],

    # Enriquecimento adicionado:
    "imports": ["jwt", "cryptography", "datetime"],
    "dependencies": [
        {"module": "config", "type": "peer", "file": "config.py"},
        {"module": "database", "type": "peer", "file": "db.py"},
    ],
    "related_functions": [
        {"name": "decode_jwt", "file": "auth.py", "distance": "1-hop"},
        {"name": "validate_exp", "file": "auth.py", "distance": "1-hop"},
    ],
    "type_hints": {
        "token": "str",
        "return": "dict[str, Any]"
    },
    "exceptions": ["UnauthorizedError", "ExpiredSignatureError"],
}
```

Agora o agente tem contexto **estrutural completo**.

## Estratégias de Enriquecimento

### 1. Análise AST (Abstract Syntax Tree)

Extrair estrutura sintática do código:

```python
import ast

code = """
def verify_token(token: str) -> dict:
    # implementação
    pass
"""

tree = ast.parse(code)

class ASTAnalyzer(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        print(f"Função: {node.name}")
        print(f"Args: {[arg.arg for arg in node.args.args]}")
        print(f"Return type: {ast.unparse(node.returns)}")

        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Return):
                print(f"Return value: {ast.unparse(child.value)}")

analyzer = ASTAnalyzer()
analyzer.visit(tree)
```

### 2. Resolução de Dependências

Encontrar imports e módulos relacionados:

```python
def resolve_dependencies(file_path: str, class_or_func_name: str) -> list[dict]:
    """Resolver dependências usando LSP (Language Server Protocol) ou AST"""

    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    dependencies = []

    # 1. Extrair imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                dependencies.append({
                    "type": "import",
                    "module": alias.name,
                    "alias": alias.asname,
                })
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                dependencies.append({
                    "type": "from_import",
                    "module": node.module,
                    "name": alias.name,
                })

    # 2. Encontrar uso de variáveis/funções
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == class_or_func_name:
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call):
                        func_name = ast.unparse(subnode.func)
                        dependencies.append({
                            "type": "function_call",
                            "name": func_name,
                        })

    return dependencies
```

### 3. Grafo de Dependências

Construir grafo completo de relacionamentos:

```python
import networkx as nx

def build_dependency_graph(codebase_path: str) -> nx.DiGraph:
    """Construir grafo de dependências entre módulos"""

    graph = nx.DiGraph()

    for file in find_python_files(codebase_path):
        with open(file, 'r') as f:
            tree = ast.parse(f.read())

        # Adicionar nó para arquivo
        graph.add_node(file)

        # Extrair imports e adicionar arestas
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported_file = resolve_import_to_file(node.module, codebase_path)
                if imported_file:
                    graph.add_edge(file, imported_file)

    return graph

# Usar para encontrar relacionamentos
graph = build_dependency_graph("./my-repo")

def get_related_files(file_path: str, distance: int = 2) -> list[str]:
    """Encontrar arquivos relacionados até N hops de distância"""
    related = []
    for node in nx.single_source_shortest_path_length(graph, file_path, cutoff=distance):
        if node != file_path:
            related.append((node, nx.shortest_path_length(graph, file_path, node)))
    return sorted(related, key=lambda x: x[1])
```

## Enriquecimento em Tempo de Query

No Vectora, enriquecimento acontece em **tempo de busca**:

```python
def search_with_enrichment(query: str, bucket_id: str) -> list[dict]:
    """Buscar + enriquecer contexto"""

    # 1. Busca semântica padrão
    results = lancedb_search(query, top_k=100)

    # 2. Reranking
    results = rerank(results, top_k=10)

    # 3. Enriquecimento
    enriched = []
    for chunk in results:
        # Resolver AST
        ast_info = analyze_ast(chunk["file"], chunk["content"])

        # Resolver dependências
        deps = resolve_dependencies_from_ast(ast_info)

        # Buscar arquivos relacionados
        related = get_related_files(chunk["file"], distance=1)

        # Adicionar ao chunk
        chunk["ast_info"] = ast_info
        chunk["dependencies"] = deps
        chunk["related_files"] = related

        enriched.append(chunk)

    return enriched
```

## Tipos de Enriquecimento

| Tipo             | Descrição                    | Custo | Quando Usar          |
| ---------------- | ---------------------------- | ----- | -------------------- |
| **Imports**      | Extrair módulos importados   | Baixo | Sempre               |
| **AST**          | Análise sintática completa   | Médio | Todas as queries     |
| **Dependências** | Grafo de relacionamentos     | Alto  | Agent Complete       |
| **Tipos**        | Annotations e type hints     | Baixo | Type-related queries |
| **Docstrings**   | Documentação extraída        | Baixo | Sempre               |
| **Tests**        | Links para testes relevantes | Médio | Code understanding   |

## Performance vs Qualidade

Trade-off entre enriquecimento e latência:

```text
Enriquecimento   Latência    Qualidade    Custo
────────────────────────────────────────────────
Mínimo           <100ms      ⭐⭐         Baixo
AST + Imports    ~200ms      ⭐⭐⭐       Médio
Deps + Graph     ~500ms      ⭐⭐⭐⭐     Médio-Alto
Full Graph       ~1s         ⭐⭐⭐⭐⭐   Alto
```

Para a maioria dos casos, **AST + Imports** oferece melhor tradeoff.

## Implementação Prática

No Vectora, enriquecimento é feito automaticamente durante indexação:

```bash
# Indexar com enriquecimento completo
vectora index add ./my-repo --bucket "my-repo" --enrich-mode full

# Ou minimalista
vectora index add ./my-repo --bucket "my-repo" --enrich-mode minimal
```

Configuração via config:

```bash
vectora config set enrich_mode full
vectora config set enrich_depth 2  # 2-hop max
```

## External Linking

| Conceito                     | Recurso                      | Link                                                                                                  |
| ---------------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------------- |
| **AST Module**               | Python abstract syntax trees | [docs.python.org/3/library/ast](https://docs.python.org/3/library/ast.html)                           |
| **Language Server Protocol** | Code intelligence standard   | [microsoft.github.io/language-server-protocol](https://microsoft.github.io/language-server-protocol/) |
| **Tree-sitter**              | Parser generator for code    | [tree-sitter.github.io](https://tree-sitter.github.io/)                                               |
| **NetworkX**                 | Python graph library         | [networkx.org](https://networkx.org/)                                                                 |
| **AST Parsing Guide**        | Deep dive into code analysis | [greentreesnakes.readthedocs.io](https://greentreesnakes.readthedocs.io/en/latest/)                   |
