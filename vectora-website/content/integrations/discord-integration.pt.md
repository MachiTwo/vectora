---
title: Discord Integration
slug: discord-integration
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - discord
  - bot
  - community
  - integration
  - vectora
---

{{< lang-toggle >}}

A **Vectora Discord Integration** permite que comunidades façam buscas de documentação, obtenham respostas e compartilhem conhecimento diretamente no Discord.

## Setup do Discord Bot

### 1. Criar Aplicação no Discord

1. Vá para [Discord Developer Portal](https://discord.com/developers/applications)
2. Clique em "New Application"
3. Nomeie como "Vectora"
4. Vá para "Bot" > "Add Bot"

### 2. Configurar Permissões

```text
Configurar Permissões do Bot:
  ✓ Send Messages
  ✓ Send Messages in Threads
  ✓ Read Messages/View Channels
  ✓ Read Message History
  ✓ Use Slash Commands
  ✓ Embed Links
```

### 3. Ativar Intents

```text
Privileged Gateway Intents:
  ✓ Message Content Intent
  ✓ Server Members Intent
```

### 4. Copiar Token

```text
Bot Token: MTA1NzM1NjM5OTk5NDk2NTEyNA.G...
```

Salve com segurança!

### 5. Instalar em Servidor

Use a URL de autorização:

```text
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands
```

## Usando Vectora no Discord

### Comando Slash `/search`

```text
/search query: autenticação JWT
```

Vectora responde com resultados formatados.

### Menção do Bot

```text
@Vectora como faço token refresh?
```

O bot responde na thread.

### Reações Rápidas

```text
mensagem do usuário
[user reage com 🔍]

Vectora: Encontrei documentação sobre esse tópico!
```

## Configuração de Servidor

### Permissões por Canal

Configure canais onde Vectora pode operar:

```text
#general: desativado
#dev-discussion: ativado
#devops: ativado
#off-topic: desativado
```

Na Dashboard Vectora:

```text
Discord > Your Server > Channels
  ✓ #dev-discussion (search enabled)
  ✓ #devops (search enabled)
  ✗ #general (search disabled)
```

### Roles de Acesso

Configure quem pode usar:

```text
@member: Pode buscar
@moderator: Pode buscar + configurar
@admin: Acesso total
```

## Recursos do Bot

### Busca com Formatação

```text
/search autenticação

Vectora:
📄 **auth.py** (linha 45)
Score: 0.94 | Bucket: codebase

\`\`\`python
def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    ...
\`\`\`

[View Full] [Open in VSCode] [Add to Favorites]
```

### Resultados em Threads

Vectora sempre responde em threads para manter o canal limpo:

```text
User: @Vectora token validation
Vectora: [reponde na thread]
  └─ Result 1
  └─ Result 2
  └─ Result 3
```

### React-to-Search

```text
message: "Como fazer login?"
[user reage com 🔍]

Vectora: Encontrei 5 documentos sobre login
  - auth-guide.md
  - jwt-tutorial.md
  - ...
```

## Comandos Disponíveis

### `/search <query>`

Buscar documentação.

### `/index <bucket>`

Indexar bucket em seu servidor (permissão admin).

### `/buckets`

Listar buckets disponíveis.

### `/help`

Ver ajuda e comandos.

### `/stats`

Ver estatísticas de uso do servidor.

### `/config`

Configurar bot (permissão admin).

## Customização

### Emoji Customizados

```json
{
  "discord": {
    "emojis": {
      "search": "🔍",
      "result": "📄",
      "error": "❌",
      "success": "✅"
    }
  }
}
```

### Mensagens Customizadas

```json
{
  "discord": {
    "messages": {
      "searching": "🔍 Buscando documentação...",
      "no_results": "Nenhum resultado encontrado",
      "error": "Erro ao buscar. Tente novamente."
    }
  }
}
```

### Limites por Servidor

```json
{
  "discord": {
    "rate_limit": {
      "requests_per_hour": 100,
      "requests_per_user_hour": 20
    }
  }
}
```

## Exemplos de Uso

### Cenário 1: Ajuda em Tempo Real

```text
dev1: Como faço autenticação com JWT?
dev2: @Vectora JWT authentication
Vectora:
  Found 3 results:
  1. docs/auth/jwt-guide.md
  2. examples/jwt-login.py
  3. tests/auth.test.js
```

### Cenário 2: Suporte Comunitário

```text
new_user: Qual é o padrão de projeto?
moderator: @Vectora architecture patterns
Vectora:
  Padrões encontrados:
  - MVC: Em 5 módulos
  - Repository: Em 8 módulos
  - Service: Em 12 módulos
  [Ver Exemplos] [Documentação Completa]
```

### Cenário 3: Code Review

```text
reviewer: Como vocês implementam caching?
reviewer: @Vectora caching implementation
Vectora:
  Encontrei padrões similares:
  - lib/cache.py (LRU Cache)
  - lib/redis-cache.py (Redis)
  Score: 0.89
```

## Monitoring

### Statistics Command

```text
/stats

📊 Vectora Statistics
━━━━━━━━━━━━━━━━━
Hoje: 23 buscas
Esta semana: 156 buscas
Este mês: 612 buscas

Top Queries:
  1. authentication (45 buscas)
  2. api design (32 buscas)
  3. error handling (28 buscas)

Top Users:
  1. @dev1 (34 buscas)
  2. @dev2 (28 buscas)
  3. @dev3 (19 buscas)
```

### Activity Log

```text
Dashboard > Discord > Activity Log

2026-05-04 14:32 | user:alice | query:"JWT auth"
2026-05-04 14:33 | user:bob   | query:"token refresh"
2026-05-04 14:34 | user:charlie | query:"caching"
```

## Troubleshooting

### Bot não responde

1. Verificar se está online: `Status > Application Status`
2. Verificar permissões do bot no canal
3. Verificar token em Dashboard

```bash
# Testar bot
curl -H "Authorization: Bot YOUR_TOKEN" \
  https://discord.com/api/v10/users/@me
```

### Resultados lentos

1. Reduzir topK em configurações
2. Usar filtros mais específicos
3. Verificar latência do servidor

### Erros de autorização

1. Reinstalar o bot com URL correta
2. Verificar permissões em "Bot" > "Permissions"
3. Verificar Intents estão ativados

## Boas Práticas

### Canais Organizados

```text
📚 Documentation
  ├─ #docs-search (busca livre)
  ├─ #faq (perguntas frequentes)
  └─ #announcements

💻 Development
  ├─ #dev-general
  ├─ #code-review
  └─ #help
```

### Comandos Úteis para Mods

```text
/config list            # Ver configurações
/config set channel     # Ativar/desativar canal
/config set bucket      # Escolher buckets
/stats reset            # Resetar estatísticas
```

## Security

### Token Seguro

- Armazene token em `.env`
- Nunca faça commit do token
- Regenere se comprometido

```bash
# .env
DISCORD_BOT_TOKEN=YOUR_TOKEN_HERE
```

### Permissões Mínimas

Dê apenas as permissões necessárias:

```text
✓ Send Messages
✓ Read Messages
✓ Use Slash Commands
✗ Administrator (não necessário)
```

### Privacy

- Não armazenam mensagens do Discord
- Buscas são logadas (não conteúdo)
- Dados deletados em 30 dias

## External Linking

| Conceito               | Recurso           | Link                                                                                                                                   |
| ---------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Discord.py**         | Python library    | [discordpy.readthedocs.io](https://discordpy.readthedocs.io/)                                                                          |
| **Discord Developer**  | Official portal   | [discord.com/developers](https://discord.com/developers)                                                                               |
| **Discord API**        | API documentation | [discord.com/developers/docs/intro](https://discord.com/developers/docs/intro)                                                         |
| **Slash Commands**     | Command guide     | [discord.com/developers/docs/interactions/application-commands](https://discord.com/developers/docs/interactions/application-commands) |
| **Bot Best Practices** | Community guide   | [discordapp.com/developers/docs/topics/permissions](https://discordapp.com/developers/docs/topics/permissions)                         |
