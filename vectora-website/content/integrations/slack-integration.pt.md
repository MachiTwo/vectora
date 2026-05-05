---
title: Slack Integration
slug: slack-integration
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - slack
  - bot
  - integration
  - messaging
  - vectora
---

{{< lang-toggle >}}

A **Vectora Slack Integration** permite buscar documentação, fazer perguntas sobre código e obter respostas diretamente no Slack sem deixar a conversa.

## Setup no Slack

### 1. Criar Slack App

1. Acesse [api.slack.com/apps](https://api.slack.com/apps)
2. Clique em "Create New App"
3. Escolha "From an app manifest"
4. Cole o manifest abaixo

```yaml
display_information:
  name: Vectora Bot
  description: AI-powered documentation search for Slack
  background_color: "#2f2f2f"

features:
  bot_user:
    display_name: Vectora
    always_online: true

oauth_config:
  scopes:
    bot:
      - chat:write
      - commands
      - app_mentions:read
      - channels:read
      - users:read
      - search:read

settings:
  event_subscriptions:
    bot_events:
      - app_mention
      - message.channels

  interactivity:
    is_enabled: true
    request_url: https://your-server.com/slack/interactions
```

### 2. Instalar Vectora

1. Vá para "OAuth & Permissions"
2. Clique em "Install to Workspace"
3. Autorize as permissões
4. Copie o token `xoxb-...`

### 3. Configurar Webhook

1. Vá para "Event Subscriptions"
2. Enable events
3. Configure Request URL: `https://your-server.com/slack/events`
4. Subscribe to:
   - `app_mention`
   - `message.channels`

### 4. Configurar no Vectora

Abra o dashboard Vectora:

1. Vá para "Integrations > Slack"
2. Cole o token `xoxb-...`
3. Selecione buckets disponíveis
4. Salve

## Usando no Slack

### Menção Direta

```text
@vectora como faço autenticação com JWT?
```

Vectora responde na thread com documentação relevante.

### Busca com Comando Slash

```text
/vectora-search autenticação JWT
```

### Busca em Contexto

Ao discutir sobre código em um canal, mencione:

```text
Na verdade, @vectora, como funciona token refresh?
```

Vectora entende o contexto e busca documentação relevante.

## Configuração Avançada

### Permissões de Canais

Configure quais canais podem usar Vectora:

```text
Dashboard > Settings > Slack

Canais permitidos:
  ✓ #engineering
  ✓ #devops
  ✗ #marketing
```

### Filtros de Bucket

Por canal, configure buckets disponíveis:

```text
#engineering:
  - codebase (busca em repositório)
  - architecture (diagramas e padrões)
  - api-docs (documentação da API)

#devops:
  - deployment-guide
  - infrastructure
  - runbooks
```

### Respostas Customizadas

Customize o template de resposta:

```text
Settings > Response Template

Template:
  Found in {{bucket}}:
  📄 {{filename}} (line {{line}})
  Score: {{score}}%

  {{content}}
```

### Threading

Configure se respostas vão em thread:

```json
{
  "slack": {
    "reply_in_thread": true,
    "show_original_message": true
  }
}
```

## Rate Limiting no Slack

Vectora respeita limites Slack:

- **Free plan**: 10 buscas/dia por usuário
- **Pro plan**: 100 buscas/dia por usuário
- **Enterprise**: Customizado

Configure em `Settings > Rate Limits`.

## Exemplos de Uso

### Debugging em Tempo Real

```text
dev: @vectora por que token está expirado?
vectora: Achei em api-docs/auth.md linha 45:
  "Tokens JWT expiram após 24 horas por padrão.
   Use refresh_token para renovar..."
```

### Onboarding de Novo Dev

```text
new_dev: @vectora como fazer setup local?
vectora: [retorna guia setup completo]
```

### Code Review Assist

```text
reviewer: Esse pattern parece estranho
reviewer: @vectora existe padrão recomendado?
vectora: [retorna exemplos de pattern do codebase]
```

## Monitoring

### Analytics

Dashboard > Analytics:

- Buscas por dia/semana
- Canais mais ativos
- Queries mais frequentes
- Taxa de utilidade

### Audit Log

Todas as buscas são logadas:

```text
2026-05-04 14:32 | user:alice | query:"JWT auth" | bucket:"docs" | score:0.92
2026-05-04 14:33 | user:bob   | query:"token refresh" | bucket:"api" | score:0.87
```

Acesse em `Settings > Audit Log`.

## Troubleshooting

### Vectora não responde

1. Verificar token: `Dashboard > Integrations > Slack > Test`
2. Verificar permissões: `OAuth & Permissions > Scopes`
3. Verificar canal: Vectora foi adicionado ao canal?

```text
/invite @vectora
```

### Respostas lentas

1. Reduzir `topK` em settings
2. Usar filtros mais específicos
3. Verificar carga do servidor

### Erros de autenticação

```text
Settings > Slack > Reauthorize

Isso vai renovar o token e os scopes.
```

## Boas Práticas

### Organizar Buckets

```text
Codebase:
  ├─ backend/ (Python, Go)
  ├─ frontend/ (JavaScript, React)
  └─ infrastructure/ (Docker, k8s)

Documentation:
  ├─ api-reference
  ├─ guides
  └─ troubleshooting
```

### Naming Convention

```text
✓ /vectora-search JWT validation
✓ @vectora how do I refresh tokens?
✗ @vectora auth
```

Buscas mais específicas retornam melhores resultados.

## Security

### Token Management

- Regenerar token regularmente
- Nunca compartilhar token em mensagens
- Usar secrets management para self-hosted

### Data Privacy

- Logs de busca não contêm conteúdo privado
- Dados são criptografados em trânsito
- Retenção configurável (padrão: 30 dias)

## External Linking

| Conceito              | Recurso             | Link                                                                           |
| --------------------- | ------------------- | ------------------------------------------------------------------------------ |
| **Slack API**         | Official docs       | [api.slack.com](https://api.slack.com/)                                        |
| **Vectora Slack Bot** | GitHub repository   | [github.com/vectora-io/slack-bot](https://github.com/vectora-io/slack-bot)     |
| **Slack Manifests**   | Configuration guide | [api.slack.com/reference/manifests](https://api.slack.com/reference/manifests) |
| **Slack Bolt**        | Framework           | [slack.dev/bolt](https://slack.dev/bolt)                                       |
| **OAuth 2.0**         | Authorization       | [oauth.net](https://oauth.net/)                                                |
