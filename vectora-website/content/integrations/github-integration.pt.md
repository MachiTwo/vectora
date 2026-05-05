---
title: GitHub Integration
slug: github-integration
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - github
  - integration
  - repository
  - codereview
  - vectora
---

{{< lang-toggle >}}

A **Vectora GitHub Integration** sincroniza repositórios, fornece evidência em code reviews e comenta em PRs com documentação relevante.

## Setup do GitHub App

### 1. Criar GitHub App

1. Vá para `Settings > Developer settings > GitHub Apps`
2. Clique em "New GitHub App"
3. Preencha as informações:

```text
App name: Vectora
Homepage URL: https://vectora.dev
Webhook URL: https://api.vectora.dev/webhooks/github
```

### 2. Configurar Permissões

```text
Repository Permissions:
  ✓ Contents: Read & write
  ✓ Pull requests: Read & write
  ✓ Issues: Read & write
  ✓ Code scanning alerts: Read & write

User Permissions:
  ✓ Email addresses: Read-only
```

### 3. Configurar Eventos

```text
Subscribe to events:
  ✓ Push
  ✓ Pull request
  ✓ Pull request review
  ✓ Issues
  ✓ Issue comment
```

### 4. Instalar no Vectora

1. Copie a chave privada do GitHub App
2. Acesse `Dashboard > Integrations > GitHub`
3. Cole a chave
4. Selecione repositórios a sincronizar

## Sincronização de Repositórios

### Setup Inicial

```bash
# Via CLI
vectora-cli github sync myrepo

# Via Dashboard
Dashboard > GitHub > Select Repository > Sync
```

### Buscas no Repositório

A extensão VSCode agora busca em código do repositório:

```python
from utils import verify_token  # Passe o mouse para ver documentação
```

Vectora busca:

- Implementação em `utils.py`
- Documentação em `docs/`
- Exemplos em `tests/`

### Monitoramento de Push

Quando faz push, Vectora:

1. Indexa novos arquivos
2. Detecta mudanças de padrão
3. Alerta se novo código desvia do padrão existente

## Code Review Automation

### Comments em PRs

Vectora comenta em PRs fornecendo contexto:

```text
# PR #123: Add JWT refresh endpoint

Vectora: Found similar implementation in lib/auth.py (line 45)

  The refresh endpoint should:
  - Validate old token
  - Generate new token with same claims
  - Return both access_token and refresh_token

  See: docs/authentication.md#refresh-flow
```

### Review Suggestions

Configure quando Vectora deve comentar:

```json
{
  "github": {
    "auto_review": true,
    "comment_on_pattern_deviation": true,
    "min_confidence": 0.8,
    "check_for": ["security_patterns", "performance_patterns", "naming_conventions"]
  }
}
```

### Code Analysis

Vectora detecta:

- **Security**: SQL injection, XSS, weak auth
- **Performance**: N+1 queries, blocking calls
- **Patterns**: Inconsistência com codebase

## Webhook Events

### Push Event

```python
# Triggered quando código é feito push
# Vectora:
# - Indexa novos arquivos
# - Detecta breaking changes
# - Valida padrões
```

### Pull Request Event

```python
# Triggered quando PR é aberto
# Vectora:
# - Busca código relacionado
# - Comenta com evidência
# - Sugere melhorias
```

### Issue Event

```python
# Triggered quando issue é criada
# Vectora:
# - Busca issues similares
# - Sugere código relevante
# - Vincula documentação
```

## Configuração Avançada

### Filtros de Repositório

Por repositório, escolha buckets:

```text
Repository: backend
  - codebase (código-fonte)
  - architecture (design docs)
  - api-specs

Repository: frontend
  - codebase
  - component-library
  - design-system
```

### Threshold de Confiança

```json
{
  "github": {
    "min_confidence_to_comment": 0.85,
    "min_confidence_to_block": 0.95
  }
}
```

Vectora só comenta se confidence >= 0.85.

### Ignorar Arquivos

```text
.githubvectoraignore

node_modules/
dist/
.env
*.test.js
```

### Branch Filtering

```json
{
  "github": {
    "branches": {
      "main": {
        "auto_review": true,
        "require_approval": true
      },
      "develop": {
        "auto_review": true
      },
      "feature/*": {
        "auto_review": false
      }
    }
  }
}
```

## GitHub Actions Integration

### Usando em Workflows

```yaml
name: Code Review with Vectora

on: [pull_request]

jobs:
  vectora-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Vectora Review
        uses: vectora-io/github-action@v1
        with:
          api-key: ${{ secrets.VECTORA_API_KEY }}
          buckets: "codebase,architecture"
          min-confidence: 0.8
```

## Examples

### Exemplo 1: Code Review Automático

```text
# PR #42: Add authentication middleware

Vectora: ✅ Follows existing patterns

Found similar implementation in:
  - middleware/rate-limiter.js (line 23)
  - middleware/cors.js (line 15)

Pattern detected: Error handling matches codebase standard
Score: 0.94

Suggestion: Add test for edge case (see tests/auth.test.js line 120)
```

### Exemplo 2: Security Alert

```text
# PR #45: Add user login endpoint

Vectora: ⚠️ Security concern detected

Your implementation uses:
  crypto.randomBytes(32).toString('hex')

But codebase standard (lib/auth.js line 78) uses:
  secrets.token_urlsafe(32)

The second is cryptographically stronger for web tokens.
See: docs/security/token-generation.md
```

### Exemplo 3: Performance Detection

```text
# PR #50: Add search endpoint

Vectora: ⚠️ Potential N+1 query detected

For each result in search, you're calling:
  db.query("SELECT user FROM users WHERE id=?")

See similar pattern solved in:
  - search.py line 234 (uses JOIN)
  - reports.py line 156 (uses bulk query)

This might cause performance issues with large result sets.
```

## Monitoring

### GitHub Dashboard

```text
Dashboard > GitHub:
  - Latest PR reviews
  - Code review history
  - Pattern deviations detected
  - Security alerts
```

### Metrics

```text
- PRs reviewed: 156
- Auto-comments: 89
- Pattern violations: 12
- Security alerts: 3
- Average review time: 2.3 min
```

## Troubleshooting

### GitHub App não aparece

1. Reinstalar o GitHub App na organização
2. Verificar permissões em `Settings > Applications`

### Comentários não aparecem

1. Verificar webhook: `Settings > Developer settings > Webhooks`
2. Verificar token do app é válido
3. Verificar branch filtering em settings

### Sincronização lenta

Reduzir quantidade de repositórios ou aumentar frequency:

```json
{
  "github": {
    "sync_frequency_minutes": 60,
    "max_repos": 5
  }
}
```

## Security

### Token Management

- GitHub App private key é criptografada
- Tokens são rotacionados automaticamente
- Nunca exponha tokens em logs

### Data Privacy

- Código não é armazenado, apenas indexado
- Comentários contêm apenas referências
- Logs não contêm conteúdo privado

## External Linking

| Conceito                  | Recurso             | Link                                                                                                   |
| ------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------ |
| **GitHub API**            | Official docs       | [docs.github.com/en/rest](https://docs.github.com/en/rest)                                             |
| **GitHub Apps**           | Configuration guide | [docs.github.com/en/developers/apps](https://docs.github.com/en/developers/apps)                       |
| **Vectora GitHub Action** | GitHub marketplace  | [github.com/marketplace/actions/vectora-review](https://github.com/marketplace/actions/vectora-review) |
| **Webhooks**              | Event reference     | [docs.github.com/webhooks](https://docs.github.com/webhooks)                                           |
| **GitHub Actions**        | Workflows           | [docs.github.com/en/actions](https://docs.github.com/en/actions)                                       |
