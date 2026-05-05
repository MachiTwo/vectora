---
title: ACP
slug: acp
date: "2026-04-18T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - acp
  - agents
  - ai
  - auth
  - concepts
  - go
  - json
  - jwt
  - mcp
  - multi-agent
  - protocol
  - state
  - sub-agents
  - system
  - vectora
---

{{< lang-toggle >}}

**ACP** (Agent Communication Protocol) é um protocolo de comunicação entre Vectora e agents customizados ou outros sistemas. Está em **Beta** para early adopters.

## O que é ACP?

ACP permite que:

- **Vectora seja sub-agent** de um sistema maior (ex: IA orquestradora multi-agent)
- **Múltiplos agents trabalhem juntos** compartilhando contexto
- **Arquiteturas distribuídas** com Vectora em múltiplas instâncias

Diferente de MCP (IDE ↔ Vectora), ACP é para **agent ↔ agent**.

## Casos de Uso

| Caso                   | Descrição                                       |
| ---------------------- | ----------------------------------------------- |
| **Multi-agent system** | Vectora + Code Agent + Test Agent coordenados   |
| **Distributed search** | Vectora em múltiplos namespaces/datacenters     |
| **Custom workflows**   | Agent orquestradora chama Vectora dinamicamente |
| **Hybrid systems**     | Vectora + GenAI + Traditional APIs juntos       |

## Status

**Beta** - Especificação em evolução. Aceita early adopters e feedback.

- Protocolista: RPC baseado em JSON (similar a MCP)
- Auth: JWT com refresh tokens
- Transporte: HTTP/2 ou WebSocket para streaming

## Começar

ACP ainda não tem documentação pública completa. Para early access:

1. Abra uma [GitHub Discussion](https://github.com/Kaffyn/Vectora/discussions)
2. Mencione "ACP interest"
3. Descreva seu caso de uso
4. Receberá acesso ao spec beta + suporte

## Comparação: MCP vs ACP

| Aspecto         | MCP                   | ACP                        |
| --------------- | --------------------- | -------------------------- |
| **Caso de uso** | IDE local             | Inter-agent distribuído    |
| **Transporte**  | STDIO (IPC)           | HTTP/2 ou WebSocket        |
| **Latência**    | <10ms                 | 50-100ms                   |
| **State**       | Persistente (session) | Compartilhado entre agents |
| **Status**      | Stable                | Beta                       |

---

> Interessado em ACP? [Abra uma Discussion](https://github.com/Kaffyn/Vectora/discussions)

## External Linking

| Conceito             | Recurso                              | Link                                                                                            |
| -------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------- |
| **MCP**              | Model Context Protocol Specification | [modelcontextprotocol.io/specification](https://modelcontextprotocol.io/specification)          |
| **Anthropic Claude** | Claude Documentation                 | [docs.anthropic.com](https://docs.anthropic.com/)                                               |
| **JWT RFC 7519**     | JSON Web Token Standard              | [datatracker.ietf.org/doc/html/rfc7519](https://datatracker.ietf.org/doc/html/rfc7519)          |
| **LangChain Agents** | LangChain agent docs                 | [python.langchain.com/docs/concepts/agents](https://python.langchain.com/docs/concepts/agents/) |
