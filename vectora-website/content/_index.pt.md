---
title: Vectora
slug: vectora
date: "2026-04-18T22:30:00-03:00"
type: docs
sidebar:
  open: true
breadcrumbs: true
tags:
  - adk
  - agentic-framework
  - agents
  - ai
  - architecture
  - ast-parsing
  - auth
  - byok
  - claude
  - compliance
  - concepts
  - config
  - context-engine
  - embeddings
  - errors
  - gemini
  - gemini-cli
  - go
  - governance
  - guardian
  - integration
  - mcp
  - mcp-protocol
  - metrics
  - mongodb
  - mongodb-atlas
  - persistence
  - protocol
  - rag
  - rbac
  - reference
  - reranker
  - security
  - sso
  - state
  - sub-agents
  - system
  - testing
  - tools
  - troubleshooting
  - trust-folder
  - tutorial
  - vector-search
  - vectora
  - voyage
  - yaml
---

{{< lang-toggle >}}

O **Vectora** é um **Hub de Conhecimento Local-First** que capacita agentes de IA a operarem com contexto governado, sem alucinações e com privacidade total. Construído com **FastAPI + LangChain + Deep Agents**, combina busca vetorial de alta performance (LanceDB + VoyageAI), análise cognitiva (VCR com PyTorch + XLM-RoBERTa) e orquestração de RAG para fornecer contexto preciso via REST/MCP/JSON-RPC.

> [!IMPORTANT] **Fórmula Central**: `Agente Especialista = LangChain + Deep Agents + [VCR Pré-Pensamento](/models/vectora-cognitive-runtime/) + Contexto Governado (LanceDB + PostgreSQL + Redis)`

## O Problema que o Vectora Resolve

A tabela abaixo descreve como o Vectora aborda as falhas comuns em agentes genéricos e seu impacto prático no desenvolvimento.

| Falha em Agentes Genéricos     | Impacto Prático                                                  | Como o Vectora Mitiga                                                                                                                                         |
| :----------------------------- | :--------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Contexto Raso**              | Busca por "autenticação" retorna 50 arquivos irrelevantes        | [Reranker 2.5](/concepts/reranker/) filtra por relevância semântica real, não apenas similaridade de cosseno bruta                                            |
| **Sem Validação Pré-Execução** | Chamadas de ferramentas perigosas rodam antes de serem auditadas | [Agentic Framework](/concepts/agentic-framework-runtime/) intercepta, valida via Struct Validation e aplica [Guardian](/security/guardian/) antes da execução |
| **Falta de Isolamento**        | Dados do projeto vazam entre sessões                             | [Isolamento de Namespace](/security/rbac/) via RBAC de nível de aplicação + filtragem obrigatória no backend                                                  |
| **Consumo Imprevisível**       | LLMs geram excesso de dados, desperdiçando tokens em boilerplate | [Context Engine](/concepts/context-engine/) decide o escopo, aplica compactação (head/tail) e injeta apenas o que é relevante                                 |
| **Segurança Frágil**           | Blocklists dependem de prompts (que podem sofrer jailbreak)      | [Hard-Coded Guardian](/security/guardian/) é compilado no binário Go, impossível de contornar via prompt                                                      |

## A Solução: Camada de Inteligência Local-First

O Vectora é exposto via **REST, MCP e JSON-RPC**. Ele opera como uma camada de pré-pensamento e governança, enriquecendo agentes com contexto preciso e artefatos de decisão estruturados.

```mermaid
graph LR
    A["Agente Principal<br/>(Claude Code, Cursor, etc)"] -->|REST/MCP/JSON-RPC| B["FastAPI<br/>(Backend Python)"]
    B --> C["VCR: Pré-Pensamento<br/>(PyTorch + XLM-RoBERTa)"]
    C --> D["Context Engine<br/>(Parser AST + Compactação)"]
    D --> E["LanceDB<br/>(Vector Search)"]
    D --> F["VoyageAI<br/>(Embeddings + Reranking)"]
    E --> G["PostgreSQL + Redis<br/>(Metadata + Cache)"]
    F --> G
    G --> H["LangChain + Deep Agents<br/>(Orchestration)"]
    H --> I["Contexto Governado<br/>+ Análise + Métricas"]
    I -->|REST/MCP/JSON-RPC| A
```

## Componentes Principais

O sistema é dividido em módulos especializados que garantem integridade, performance e segurança na recuperação de contexto.

| Módulo                                                                   | Responsabilidade                                                                         | Tecnologia                   |
| :----------------------------------------------------------------------- | :--------------------------------------------------------------------------------------- | :--------------------------- |
| **[VCR: Vectora Cognitive Runtime](/models/vectora-cognitive-runtime/)** | Pré-pensamento: análise de intenção, seleção de ferramentas, otimização de query (<10ms) | PyTorch + XLM-RoBERTa + LoRA |
| **[FastAPI Backend](/backend/_index.pt.md)**                             | Servidor REST/MCP/JSON-RPC, auth JWT, RBAC, gestão de estado                             | FastAPI + Pydantic + asyncio |
| **[LangChain + Deep Agents](/langchain/deep-agents/_index.pt.md)**       | Orchestração, planning engine, executor de ferramentas, memória                          | LangChain + Deep Agents      |
| **[Context Engine](/concepts/context-engine/)**                          | Parsing AST, compactação, busca semântica, reranking local                               | LanceDB + VoyageAI           |
| **[Vector Storage](/backend/lancedb.pt.md)**                             | Armazenamento vetorial nativo, índices otimizados, busca semântica rápida                | LanceDB (local-first)        |
| **[Metadata + Cache](/backend/postgresql.pt.md)**                        | Persistência de metadados, sessões, histórico, isolamento multi-tenant                   | PostgreSQL + Redis           |
| **[Protocols](/protocols/_index.pt.md)**                                 | REST API, MCP server, JSON-RPC 2.0, ACP para integrações de editor                       | HTTP, stdin/stdout, JSON-RPC |

## Stack Tecnológico

O Vectora é construído com tecnologias **comprovadas, de código aberto** e otimizadas para **operação local-first** com máxima privacidade.

| Camada                          | Tecnologia                       | Razão                                                                    | Docs                                      |
| :------------------------------ | :------------------------------- | :----------------------------------------------------------------------- | :---------------------------------------- |
| **Orquestração + Planejamento** | `LangChain + Deep Agents`        | Abstração limpa sobre LLMs, planning nativo, estado persistido           | [LangChain](/langchain/_index.pt.md)      |
| **Pré-Pensamento (VCR)**        | `PyTorch + XLM-RoBERTa-small`    | Inferência local (<10ms p99), LoRA fine-tuning, zero dependência de rede | [VCR](/models/vectora-cognitive-runtime/) |
| **API Backend**                 | `FastAPI (Python 3.10+)`         | Async nativo, validação Pydantic, REST/MCP/JSON-RPC em um servidor       | [FastAPI](/backend/_index.pt.md)          |
| **Embeddings**                  | `VoyageAI (Voyage 4)`            | Ciente de AST, captura similaridade semântica funcional                  | [Embeddings](/search/embeddings.pt.md)    |
| **Reranking Local**             | `XLM-RoBERTa via VCR`            | Cross-encoder otimizado no VCR (<10ms), zero chamadas externas           | [Reranking](/search/reranker.pt.md)       |
| **Vector Storage**              | `LanceDB`                        | Nativo, sem servidor, índices otimizados, busca rápida, backup fácil     | [LanceDB](/backend/lancedb.pt.md)         |
| **Dados Estruturados**          | `PostgreSQL (pg8000 embedded)`   | Metadados, sessões, histórico, RBAC, totalmente local                    | [PostgreSQL](/backend/postgresql.pt.md)   |
| **Cache + Sessões**             | `Redis (embedded)`               | Cache de alta velocidade, gerenciamento de sessões, filas de background  | [Redis](/backend/redis.pt.md)             |
| **Frontend**                    | `React 19 + TypeScript + Vite`   | Type-safe, performance, real-time updates via WebSocket/SSE              | [Frontend](/frontend/_index.pt.md)        |
| **CLI + TUI**                   | `Python + textual + system tray` | Acessível, intuitivo, integrável com sistemas operacionais               | [CLI](/cli/_index.pt.md)                  |

> [!IMPORTANT] **Local-First, Privacy-Preserving**:
> O Vectora é designed para **rodarpor completo no seu ambiente** — PostgreSQL, Redis, LanceDB, VCR são todos embedidos ou rodam localmente.
> **Seus dados ficam seus.** Sem envio para a nuvem (exceto chamadas opcionais a VoyageAI para embeddings).

## Segurança, Governança e BYOK

A segurança no Vectora é implementada **na camada de aplicação**, não delegada ao banco de dados, garantindo controle total sobre o acesso aos dados.

| Camada                  | Implementação                                                                             | Documento                               |
| :---------------------- | :---------------------------------------------------------------------------------------- | :-------------------------------------- |
| **Hard-Coded Guardian** | Blocklist imutável (`.env`, `.key`, `.pem`, binários) executada antes de qualquer chamada | [Guardian](/security/guardian/)         |
| **Trust Folder**        | Validação de caminho com `fs.realpath` + escopo por namespace/projeto                     | [Trust Folder](/security/trust-folder/) |
| **RBAC de Aplicação**   | Papéis (`reader`, `contributor`, `admin`, `auditor`) validados em tempo de execução       | [RBAC](/security/rbac/)                 |
| **BYOK ou Gerenciado**  | Chaves do usuário (Free) ou créditos incluídos (Plus)                                     | [Plano Free](/plans/free/)              |
| **Gerenciado (Plus)**   | Cota gerenciada incluída nos planos Pro e Team                                            | [Plano Pro](/plans/pro/)                |

## Planos e Política de Retenção

O Vectora opera com um modelo de **Soberania Digital em Primeiro Lugar**, oferecendo **BYOK (Bring Your Own Key)** para controle total ou **Gerenciado (Plus)** para conveniência.

| Plano          | Preço       | Armazenamento            | Cota de API              | Retenção                                             | Docs                               |
| :------------- | :---------- | :----------------------- | :----------------------- | :--------------------------------------------------- | :--------------------------------- |
| **Free**       | $0/mês      | 512MB total              | Apenas BYOK              | 30 dias de inatividade = exclusão do índice vetorial | [Free](/plans/free/)               |
| **Pro**        | $29/mês     | 5GB total                | Ilimitado (Plus) ou BYOK | 90 dias pós-cancelamento                             | [Pro](/plans/pro/)                 |
| **Team**       | Customizado | Customizado              | Ilimitado (Plus) ou BYOK | Política de Conformidade                             | [Team](/plans/team/)               |
| **Enterprise** | Customizado | Ilimitado (VPC/Dedicado) | Por contrato             | Política customizada                                 | [Visão Geral](/plans/_index.pt.md) |

> [!NOTE] **Regras de Retenção**: Contas gratuitas inativas por 30 dias têm seu índice vetorial excluído automaticamente. Os metadados são preservados por +90 dias para exportação via `vectora export`. Downgrades notificam sobre a redução de limites e concedem 7 dias para backup. Detalhes em [Política de Retenção](/plans/retention/).

## Fluxo de Operação (MCP-First)

O processo de funcionamento do Vectora segue um fluxo rigoroso de validação e enriquecimento de contexto.

1. **Detecção**: O [Agente Principal](/integrations/claude-code/) identifica a necessidade de contexto profundo e dispara `context_search` via MCP.
2. **Interceptação**: O [Agentic Framework](/concepts/agentic-framework-runtime/) captura a chamada, valida o namespace e aplica o [Guardian](/security/guardian/).
3. **Decisão Tática (Vectora Cognitive Runtime)**: O [Vectora Cognitive Runtime](/models/vectora-decision-engine/) intercepta a intenção e decide a política de roteamento em <8ms (local).
4. **Recuperação**: O [Context Engine](/concepts/context-engine/) escolhe o escopo (filesystem, vetor ou híbrido) e aplica parsing AST.
5. **Embed + Rerank**: A consulta é processada via `voyage-4` e os resultados brutos são refinados pelo `voyage-rerank-2.5`.
6. **Busca e Compactação**: O [MongoDB Atlas](/backend/mongodb-atlas/) retorna os top-N com compactação (head/tail + ponteiros) para evitar a degradação do contexto.
7. **Observação (Vectora Cognitive Runtime)**: O Vectora Cognitive Runtime valida a resposta final contra o contexto original para garantir zero alucinações.
8. **Resposta Estruturada**: Contexto validado + métricas são retornados ao agente principal, que gera a resposta final ao usuário.

## Por onde começar?

Explore os guias abaixo para entender como integrar e operar o Vectora no seu dia a dia.

| Categoria             | Documento                                                                                                                   | Descrição                                                                             |
| :-------------------- | :-------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------ |
| **Início Rápido**     | [Primeiros Passos](/getting-started/)                                                                                       | `winget install kaffyn.vectora`, setup da Systray, integração MCP                     |
| **Conceitos**         | [Sub-Agentes](/concepts/sub-agents/)                                                                                        | Por que Sub-Agente e não ferramentas MCP passivas? Governança ativa                   |
| **Agentic Framework** | [Agentic Framework](/concepts/agentic-framework-runtime/)                                                                   | Execução de ferramentas, Engenharia de Contexto, Gestão de Estado                     |
| **Contexto & RAG**    | [Context Engine](/concepts/context-engine/)                                                                                 | Parsing AST, compactação, raciocínio multi-etapa, ranking híbrido                     |
| **Reranking**         | [Reranker](/concepts/reranker/) · [Reranker Local](/concepts/reranker-local/)                                               | VectorDB + cross-encoder para dados mutáveis, trade-offs de custo                     |
| **Modelos**           | [Gemini 3](/models/gemini/) · [Voyage 4](/models/voyage/)                                                                   | Stack curada, fallback BYOK, esquema de config, custos por query                      |
| **Backend**           | [MongoDB Atlas](/backend/mongodb-atlas/)                                                                                    | Busca Vetorial, coleções, persistência de estado, isolamento multi-tenant             |
| **Segurança**         | [Guardian](/security/guardian/) · [RBAC](/security/rbac/)                                                                   | Blocklist hard-coded, Trust Folder, sanitização, papéis por namespace                 |
| **Planos**            | [Visão Geral](/plans/overview/)                                                                                             | Free/Pro/Team, cota gerenciada, fallback automático, política de retenção             |
| **Integrações**       | [Claude Code](/integrations/claude-code/) · [Gemini CLI](/integrations/gemini-cli/) · [Paperclip](/integrations/paperclip/) | Configuração MCP, extensões de IDE, agentes customizados, orquestradores multi-agente |
| **Referência**        | [Ferramentas MCP](/reference/mcp-tools/) · [Config YAML](/reference/config-yaml/)                                           | Schema de ferramentas, config.yaml validado nativamente, códigos de erro              |
| **Contribuição**      | [Diretrizes](/contributing/guidelines/)                                                                                     | Golang estrito, testes de performance, PRs, roadmap público                           |

---

> **Frase para lembrar**:
> _"O Vectora não responde ao usuário. Ele entrega contexto governado ao seu agente. Backend gerenciado, API sob sua chave, segurança na aplicação, seus dados sempre seus."_

## Guia de Navegação

Acesse as seções principais da documentação para aprofundar seu conhecimento.

- [**Primeiros Passos**](./getting-started/) — Instalação, setup BYOK e integração MCP.
- [**Conceitos Centrais**](./concepts/) — Entenda Sub-Agentes, Context Engine e Reranking.
- [**Segurança e Governança**](./security/) — Detalhes sobre Guardian, Trust Folder e RBAC.
- [**Autenticação**](./auth/) — Fluxos SSO, Identidade Unificada e Chaves de API.
- [**Modelos e Provedores**](./models/) — Stack curada com Gemini 3 e Voyage AI.
- [**Backend**](./backend/) — MongoDB Atlas.
- [**Integrações**](./integrations/) — Como usar com Claude Code, Gemini CLI e Cursor.
- [**Planos e Preços**](./plans/) — Comparação de funcionalidades e política de retenção.
- [**Referência Técnica**](./reference/) — Schema de ferramentas MCP e Config YAML.
- [**Contribuição**](./contributing/) — Diretrizes, padrões de código e roadmap.
- [**FAQ**](./faq/) — Resolução de problemas e perguntas frequentes.
- [**Protocolos**](./protocols/) — Especificações do Protocolo MCP no Vectora.

## External Linking

| Concept               | Resource                             | Link                                                                                                       |
| --------------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| **MongoDB Atlas**     | Atlas Vector Search Documentation    | [www.mongodb.com/docs/atlas/atlas-vector-search/](https://www.mongodb.com/docs/atlas/atlas-vector-search/) |
| **MCP**               | Model Context Protocol Specification | [modelcontextprotocol.io/specification](https://modelcontextprotocol.io/specification)                     |
| **MCP Go SDK**        | Go SDK for MCP (mark3labs)           | [github.com/mark3labs/mcp-go](https://github.com/mark3labs/mcp-go)                                         |
| **Voyage AI**         | High-performance embeddings for RAG  | [www.voyageai.com/](https://www.voyageai.com/)                                                             |
| **Voyage Embeddings** | Voyage Embeddings Documentation      | [docs.voyageai.com/docs/embeddings](https://docs.voyageai.com/docs/embeddings)                             |
| **Voyage Reranker**   | Voyage Reranker API                  | [docs.voyageai.com/docs/reranker](https://docs.voyageai.com/docs/reranker)                                 |

---

**Vectora v0.1.0** · [GitHub](https://github.com/Kaffyn/Vectora) · [Licença (MIT)](https://github.com/Kaffyn/Vectora/blob/master/LICENSE) · [Contribuidores](https://github.com/Kaffyn/Vectora/graphs/contributors)

_Parte do ecossistema de Agentes de IA Vectora. Construído com [ADK](https://adk.dev/), [Claude](https://claude.ai/) e [Go](https://golang.org/)._

© 2026 Vectora Contributors. Todos os direitos reservados.

---

_Parte do ecossistema Vectora_ · [Open Source (MIT)](https://github.com/Kaffyn/Vectora) · [Contribuidores](https://github.com/Kaffyn/Vectora/graphs/contributors)
