---
title: Integrações
slug: integrations
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - integrations
  - sdk
  - api
  - plugins
  - vectora
---

{{< lang-toggle >}}

{{< section-toggle >}}

Vectora oferece múltiplos pontos de integração para conectar com ferramentas e plataformas externas. Desde SDKs nas principais linguagens até extensões IDE, integrações de serviços e protocolos de agentes.

## Arquitetura de Integrações

```text
Aplicação Cliente
      │
      ├─→ SDK (Python, JS, Go)
      │   └─→ HTTP Client + Auth
      │
      ├─→ IDE Extension (VSCode, JetBrains)
      │   └─→ Editor Integration
      │
      ├─→ MCP Server
      │   └─→ Claude/LLM Protocol
      │
      └─→ REST API
          └─→ Direct HTTP
```

## Categorias de Integração

### SDKs Oficiais

- **Python SDK** (`vectora-py`): Cliente full-featured com retry logic, streaming, type hints
- **JavaScript SDK** (`vectora-js`): Suporte para Node.js e browsers, async/await
- **Go SDK** (`vectora-go`): Cliente de baixa latência para microserviços

### Extensões IDE

- **VSCode Extension**: Paleta de comandos integrada, hover documentation, busca em-contexto
- **JetBrains Plugin**: Busca em-contexto, refactoring assists, sugestões de padrão

### Protocípios de Agentes

- **Model Context Protocol (MCP)**: Conexão nativa com Claude Desktop e agentes LLM
- **OpenAI Assistants**: Integração com OpenAI Assistants API e GPTs
- **Anthropic Protocol**: Suporte nativo para Claude e modelos Anthropic

### Serviços Externos

- **Slack**: Buscas de documentação, respostas automáticas em canais
- **GitHub**: Sincronização de repositórios, comentários em PRs com evidência
- **Discord**: Bot para busca e discussões em comunidades
- **Notion**: Integração bidirecional de documentação

## Autenticação em Integrações

Todas as integrações usam os mesmos mecanismos de autenticação centralizados:

```python
# Todos os clientes suportam
from vectora import VectoraClient

client = VectoraClient(
    api_key="vec_...",
    base_url="https://api.vectora.dev",
    timeout=30,
)
```

## Rate Limiting e Quotas

Todas as integrações respeitam os limites:

- **Standard**: 1,000 req/min, 100 MB/mês
- **Professional**: 10,000 req/min, 1 GB/mês
- **Enterprise**: Customizado

## Fluxo de Implementação

1. **Escolher integração**: SDK, IDE, MCP ou API Direct
2. **Autenticação**: Obter `API_KEY` no dashboard
3. **Configuração**: Instalar dependências, configurar credentials
4. **Uso**: Implementar conforme documentação específica
5. **Monitoring**: Acompanhar via observabilidade e dashboards

## External Linking

| Conceito                    | Recurso            | Link                                                                               |
| --------------------------- | ------------------ | ---------------------------------------------------------------------------------- |
| **Model Context Protocol**  | Claude integration | [modelcontextprotocol.io](https://modelcontextprotocol.io/)                        |
| **OpenAI Assistants**       | API documentation  | [platform.openai.com/docs/assistants](https://platform.openai.com/docs/assistants) |
| **Anthropic API**           | Official docs      | [docs.anthropic.com](https://docs.anthropic.com/)                                  |
| **REST API Best Practices** | API Design         | [restfulapi.net](https://restfulapi.net/)                                          |
| **OAuth 2.0**               | Authorization      | [oauth.net](https://oauth.net/)                                                    |
