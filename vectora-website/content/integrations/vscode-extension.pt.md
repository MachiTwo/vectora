---
title: VSCode Extension
slug: vscode-extension
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - vscode
  - ide
  - extension
  - development
  - vectora
---

{{< lang-toggle >}}

A **Vectora VSCode Extension** integra busca e indexação de documentação diretamente no editor, com busca contextual, hover documentation e refactoring assists.

## Instalação

### Via VSCode Marketplace

1. Abra VSCode
2. Pressione `Ctrl+Shift+X` (Windows/Linux) ou `Cmd+Shift+X` (macOS)
3. Busque por "Vectora"
4. Clique em "Install"

### Via CLI

```bash
code --install-extension vectora-io.vectora
```

### Via VSIX

```bash
# Download do arquivo VSIX
wget https://marketplace.visualstudio.com/items?itemName=vectora-io.vectora

# Instalar
code --install-extension vectora-0.1.0.vsix
```

## Setup Inicial

### 1. Autenticação

Abra a Command Palette (`Ctrl+Shift+P`) e execute:

```text
Vectora: Authenticate
```

Cole sua API key quando solicitado.

### 2. Selecionar Bucket

```text
Vectora: Select Bucket
```

Escolha o bucket padrão para buscas.

### 3. Configuração (Opcional)

Abra `Preferences > Settings > Vectora`:

```json
{
  "vectora.apiKey": "vec_...",
  "vectora.defaultBucket": "docs",
  "vectora.topK": 5,
  "vectora.autoIndex": true,
  "vectora.indexInterval": 60000
}
```

## Recursos

### Busca Contextual

Pressione `Ctrl+Shift+F` para abrir a paleta de busca Vectora.

```text
Query: autenticação JWT

Resultados:
  auth.py:45 - function verify_token()
  auth.py:78 - function refresh_token()
  security.py:12 - const JWT_SECRET = "..."
```

### Hover Documentation

Passe o mouse sobre qualquer função ou classe para ver documentação relevante:

```python
def verify_token(token: str):  # Passe o mouse aqui
    """Verificar JWT token"""
```

A extensão busca exemplos e documentação nos seus buckets.

### Quick Fix / Code Actions

Quando encontra código sem documentação ou padrões inconsistentes:

```python
def new_function(x):
    # Alerta: sem docstring
    # Quick Fix: Buscar exemplos similares
```

### Go to Definition

`Ctrl+Click` em um símbolo para abrir sua implementação:

```python
from auth import verify_token  # Ctrl+Click para ir à definição
```

### Palette de Comandos

`Ctrl+Shift+P` para ver todos os comandos:

```text
Vectora: Search
Vectora: Index Current File
Vectora: Index Workspace
Vectora: View Bucket Contents
Vectora: Create New Bucket
Vectora: Refresh Index
Vectora: Clear Cache
Vectora: Show Statistics
Vectora: Open Settings
```

## Indexação

### Indexação Automática

Com `autoIndex: true`, a extensão indexa automaticamente:

- Arquivos salvos
- Novos arquivos criados
- Mudanças detectadas

### Indexação Manual

```text
Vectora: Index Current File
```

ou

```text
Vectora: Index Workspace
```

### Configurar Arquivos Ignorados

Crie `.vectoraignore` na raiz do projeto:

```text
node_modules/
.git/
dist/
build/
*.tmp
```

## Buscas Avançadas

### Filtros

Na paleta de busca, use filtros:

```text
Query: autenticação
Filter: type:python
Filter: file:auth.py
```

### Histórico

Pressione `Ctrl+H` para ver histórico de buscas recentes.

### Salvando Buscas

Clique na estrela para salvar busca recorrente:

```text
Queries Salvadas:
  ⭐ JWT validation
  ⭐ Password hashing
  ⭐ Token refresh
```

## Integração com Git

### Blame Integration

Clique em um número de linha para ver quem modificou:

```text
Vectora: Show Git Blame
```

A extensão busca documentação relevante à mudança.

### Refactoring Assists

Ao renomear ou refatorar código:

```python
def old_name():  # Renomear para new_name
    # Vectora busca todos os usos e documentação
```

## Performance

### Cache Management

```text
Vectora: Clear Cache
```

Limpa o cache local de buscas.

### Batch Indexing

Para grandes projetos, configure indexação em lotes:

```json
{
  "vectora.batchSize": 100,
  "vectora.indexInterval": 5000
}
```

## Troubleshooting

### Extensão não aparece

1. Reinicie VSCode: `Ctrl+Shift+P` > "Developer: Reload Window"
2. Verifique se está instalada: `Extensions > Installed`
3. Verifique os logs: `View > Output > Vectora`

### Autenticação falha

```bash
# Testar API key
curl -H "Authorization: Bearer vec_..." https://api.vectora.dev/health
```

### Busca lenta

1. Reduza `topK` em settings
2. Use filtros mais específicos
3. Verifique a conectividade de rede

### Indexação travou

```text
Vectora: Clear Cache
Vectora: Refresh Index
```

## Exemplos de Fluxo

### Desenvolver Com Documentação

```text
1. Abrir arquivo (auth.py)
2. Pressionar Ctrl+Shift+F
3. Buscar "JWT validation"
4. Hover em implementações sugeridas
5. Ctrl+Click para ir à definição
6. Implementar baseado em padrões
```

### Refatorar Com Confiança

```text
1. Selecionar função a refatorar
2. Vectora: Show Similar Functions
3. Revisar padrões usados
4. Refatorar mantendo consistência
5. Extensão indexa mudanças automaticamente
```

## Configurações Avançadas

### Custom Endpoint

```json
{
  "vectora.baseUrl": "https://custom.vectora.dev",
  "vectora.timeout": 30000
}
```

### Proxy

```json
{
  "vectora.proxy": "http://proxy.company.com:8080",
  "vectora.proxyStrictSSL": false
}
```

### Logging

```json
{
  "vectora.logLevel": "debug"
}
```

Ver logs em `View > Output > Vectora`.

## External Linking

| Conceito                     | Recurso            | Link                                                                                                  |
| ---------------------------- | ------------------ | ----------------------------------------------------------------------------------------------------- |
| **VSCode Extension API**     | Official docs      | [code.visualstudio.com/api](https://code.visualstudio.com/api)                                        |
| **Vectora VSCode Ext**       | GitHub repository  | [github.com/vectora-io/vectora-vscode](https://github.com/vectora-io/vectora-vscode)                  |
| **VSCode Marketplace**       | Extension registry | [marketplace.visualstudio.com](https://marketplace.visualstudio.com/)                                 |
| **Language Server Protocol** | Specification      | [microsoft.github.io/language-server-protocol](https://microsoft.github.io/language-server-protocol/) |
| **VSCode Documentation**     | Quick start        | [code.visualstudio.com/docs](https://code.visualstudio.com/docs)                                      |
