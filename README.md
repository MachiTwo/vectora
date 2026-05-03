# VECTORA — Executive Overview

Vectora é um **Agent Completo especializado**, instalável localmente, que funciona como hub de conhecimento para outras aplicações e agents.

## O que é Vectora?

Vectora é um aplicativo **local-first, single binary** construído em Python (FastAPI) + React que combina:

- **Pre-thinking layer (VCR):** Enriquecimento contextual profundo via XLM-RoBERTa-small fine-tuned
- **Agent completo (LangChain):** Raciocínio ativo, tools reais, capacidade de implementar código
- **Bancos de dados integrados:** PostgreSQL (pg8000-embedded), Redis, LanceDB (vetorial)
- **Embeddings:** VoyageAI para semantic search
- **Protocolos:** REST API, MCP (Model Context Protocol), JSON-RPC 2.0

Não é um "RAG wrapper genérico" — é um **agente especialista** que Claude Code, Gemini e outros agents delegam trabalhos específicos.

**Vectora** oferece capacidades reais de processamento inteligente:

- **VCR (Vectora Cognitive Runtime):** Pre-thinking layer que enriquece contexto via XLM-RoBERTa-small fine-tuned em padrões de contexto
- **Busca vetorial:** Busca semântica em documentos com LanceDB + VoyageAI embeddings
- **Reranking local:** Reordena resultados localmente sem API adicional
- **Busca web:** Integra SerpAPI quando contexto local é insuficiente
- **Agent com tools reais:** File system access, terminal execution, MCPs externos, Redis/PostgreSQL queries
- **Implementação de código:** Não é apenas "RAG" — faz refactoring, escrita, testes reais
- **LangChain orchestration:** Thinking ativo, chain-of-thought, retry strategies
- **Sistema de memória:** Redis (session) + PostgreSQL (persistent) + LanceDB (semantic)
- **Multi-agent compatible:** Claude Code, Gemini CLI, Paperclip, custom agents via MCP
- **Local-first:** Todos os dados em `~/.vectora/`, sem dependência de cloud

**NÃO é:**

- ❌ SaaS proprietary
- ❌ Chat interface genérica
- ❌ "RAG wrapper" que só busca
- ❌ Dependente de nuvem
- ❌ Apenas um orchestrador (tem cognição própria via VCR)

**É:**

- ✅ **Agent Completo:** Pensa (VCR), age (tools), implementa (código real)
- ✅ **Open-source**, rodando localmente (pip install / pipx install / docker)
- ✅ **Single app integrado:** CLI + daemon + frontend + todos bancos + VCR
- ✅ **Local-first:** Dados em `~/.vectora/`, sem API externa necessária
- ✅ **Multi-agent ready:** Claude Code, Gemini, Paperclip chamam via MCP/REST
- ✅ **Especialista em contexto:** VCR fine-tuned apenas em enriquecimento contextual
- ✅ **Production-ready:** Phase 1 tem synthetic data, Phase 2+ melhora com traces reais

---

## Mapa Mental Completo

Fluxo de uma chamada externa (Claude Code) até resposta final:

```
┌──────────────────────────────┐
│   Claude Code (Agent)        │
│ "Implemente isso para mim"   │
└────────────┬─────────────────┘
             │ MCP/JSON-RPC call
             │
   ┌─────────▼──────────────────────────────────────┐
   │   VECTORA (Local Single App)                    │
   │                                                │
   │  ┌──────────────────────────────────────────┐ │
   │  │ 1. VCR: PRE-THINKING LAYER               │ │
   │  │  ├─ XLM-RoBERTa-small + LoRA             │ │
   │  │  ├─ Busca Redis: session history         │ │
   │  │  ├─ Busca PostgreSQL: contexto relevante│ │
   │  │  ├─ Busca LanceDB: chunks vetoriais     │ │
   │  │  └─ Output: enriched_context + confidence
   │  └──────────────────────────────────────────┘ │
   │                                                │
   │  ┌──────────────────────────────────────────┐ │
   │  │ 2. LANGCHAIN AGENT (Thinking Ativo)     │ │
   │  │  ├─ System Prompt: contexto enriquecido │ │
   │  │  ├─ User Prompt: query do Claude Code   │ │
   │  │  ├─ LLM (Anthropic/OpenAI/Google)      │ │
   │  │  └─ Tools:                               │ │
   │  │     ├─ File Read/Write                   │ │
   │  │     ├─ Terminal Execute                  │ │
   │  │     ├─ Redis Query                       │ │
   │  │     ├─ PostgreSQL Query                  │ │
   │  │     ├─ LanceDB Search (rerank)           │ │
   │  │     ├─ MCP Externos                      │ │
   │  │     └─ Web Search (SerpAPI)              │ │
   │  │                                           │ │
   │  │  Executa:                                 │ │
   │  │  - Se pergunta → responde                │ │
   │  │  - Se implemente → implementa real       │ │
   │  │  - Se refactor → refatora                │ │
   │  │  - Se test → testa                       │ │
   │  │                                           │ │
   │  │  Streaming: responde progressivamente    │ │
   │  └──────────────────────────────────────────┘ │
   │                                                │
   │  ┌──────────────────────────────────────────┐ │
   │  │ 3. Persistent Storage                    │ │
   │  │  ├─ Redis (memory, session, cache)       │ │
   │  │  ├─ PostgreSQL (metadata, history)       │ │
   │  │  ├─ LanceDB (vector embeddings)          │ │
   │  │  └─ File System (code, configs)          │ │
   │  └──────────────────────────────────────────┘ │
   │                                                │
   │  ┌──────────────────────────────────────────┐ │
   │  │ 4. Protocol Handlers                     │ │
   │  │  ├─ REST API (/api/v1/*)                 │ │
   │  │  ├─ MCP Server (stdio)                   │ │
   │  │  ├─ JSON-RPC 2.0 (IPC)                   │ │
   │  │  └─ WebSocket (frontend streaming)       │ │
   │  └──────────────────────────────────────────┘ │
   └────────────┬──────────────────────────────────┘
                │ JSON-RPC streaming response
                │
   ┌────────────▼──────────────────┐
   │ Claude Code (Agrega)          │
   │ ├─ Recebe chunks Vectora      │
   │ ├─ Processa resposta          │
   │ ├─ Retorna ao usuário final   │
   └───────────────────────────────┘
```

**Stack Interno:**

- **Backend:** Python 3.10+ | FastAPI | LangChain
- **Frontend:** React 18 | Vite | TypeScript
- **CLI:** Python Click/Typer
- **VCR:** PyTorch | XLM-RoBERTa-small | PEFT LoRA
- **DBs:** PostgreSQL (pg8000-embedded) | Redis | LanceDB
- **Embeddings:** VoyageAI
- **DevOps:** Docker | GitHub Actions | pip/pipx

---

## Como Funciona: Fluxo Completo

Vectora é sempre um Agent Completo. O fluxo muda conforme é chamado:

### Cenário 1: Claude Code Chama Vectora (via MCP)

```
┌────────────────────────────────┐
│  Claude Code (Agent Principal) │
│  "Implemente esse hook"        │
└────────────┬───────────────────┘
             │ MCP call (stdio)
             │ {query, context_prepared}
             │
   ┌─────────▼────────────────────────────┐
   │   VECTORA (Agent Especialista)       │
   │                                      │
   │  1. VCR Pre-Thinking                 │
   │     └─ Enriquece contexto            │
   │        (Redis, PostgreSQL, LanceDB)  │
   │                                      │
   │  2. LangChain Agent                  │
   │     ├─ System: contexto enriquecido  │
   │     ├─ User: query do Claude Code    │
   │     ├─ Thinking ativo                │
   │     └─ Tools: file/terminal/db       │
   │                                      │
   │  3. Executa Implementação Real       │
   │     ├─ Lê arquivos existentes        │
   │     ├─ Escreve/modifica código       │
   │     ├─ Testa a implementação         │
   │     └─ Salva resultado               │
   │                                      │
   │  4. Streaming Response               │
   │     └─ Responde progressivamente     │
   └─────────┬────────────────────────────┘
             │ JSON-RPC streaming chunks
             │ {status, output, code, etc}
             │
   ┌─────────▼──────────────────┐
   │ Claude Code (Agrega)       │
   │ ├─ Recebe chunks Vectora   │
   │ ├─ Processa informações    │
   │ └─ Responde ao usuário     │
   └────────────────────────────┘
```

---

### Cenário 2: Usar Vectora Standalone (CLI)

Vectora também pode ser usado diretamente pelo usuário via CLI/TUI:

```bash
vectora                    # Inicia daemon local
# acesso em http://localhost:8000

vectora chat               # Abre chat interativo no terminal
> "Implemente um hook custom para React"
> (Vectora faz o mesmo fluxo interno, mas retorna ao usuário direto)

vectora stop               # Para daemon
```

Nesse caso, você interactua diretamente com um Agent Completo sem intermediários.

---

## Modelo de Permissoes Multi-Agent

O Vectora separa autenticacao de usuario e autenticacao de agent. A conta usa login com email e senha, mas tambem recebe uma API key principal para automacao e integracoes.

A partir da API key principal, o usuario pode derivar chaves especificas para cada agent. Um agent de CEO, TCO, backend, frontend, security ou QA pode ter sua propria chave, seu proprio contexto, sua propria memoria, Redis, embeddings, indices e bucket privado completo.

Os buckets privados nao sao compartilhados por padrao. Isso permite que cada agent mantenha historico, decisoes e contexto operacional sem misturar dados sensiveis com outros agents.

Mesmo com isolamento privado, todos os agents autorizados sempre podem acessar o bucket publico do usuario e o bucket publico da organizacao. Esses buckets servem como camada comum para documentacao, decisoes compartilhadas, referencias e conhecimento que deve circular entre agents.

O Vectora tambem e totalmente exportavel. Dados, memoria e contexto podem ser exportados e importados entre usuarios, organizacoes e agents autorizados. Quando a hierarquia exigir, o CEO pode receber acesso ao contexto do TCO, e o TCO pode receber acesso ao contexto dos engenheiros, sem transformar todos os buckets privados em dados publicos.

## Dashboard — Interface de Configuração (Sempre Ativa)

Dashboard NÃO é um "modo", é a **interface de gerenciamento** que funciona **em paralelo** com ambos os modos:

```
┌──────────────────────────────────────────────────────┐
│       Vectora Dashboard                               │
│    https://localhost:3000 (ou VPS)                   │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ Login (email + password)                    │    │
│  └─────────────────────────────────────────────┘    │
│                       │                             │
│  ┌────────────────────▼───────────────────────┐    │
│  │ Main Dashboard                             │    │
│  │                                            │    │
│  │   Stats & Analytics:                     │    │
│  │  ├─ Queries today: 42                      │    │
│  │  ├─ Avg latency: 234ms                     │    │
│  │  ├─ Cache hit rate: 73%                    │    │
│  │  ├─ Vectors indexed: 15K                   │    │
│  │  └─ Storage used: 2.3GB / 50GB             │    │
│  │                                            │    │
│  │   Quick Actions:                         │    │
│  │  ├─ [Index New Dataset]                    │    │
│  │  ├─ [Clear Cache]                          │    │
│  │  └─ [Export Memory]                        │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │ Settings & Configuration                   │    │
│  │                                            │    │
│  │   API Keys:                              │    │
│  │  ├─ Claude API Key: [••••••••••]           │    │
│  │  ├─ OpenAI API Key: [••••••••••]           │    │
│  │  ├─ Voyage API Key: [••••••••••]           │    │
│  │  └─ SerpAPI Key: [••••••••••]              │    │
│  │                                            │    │
│  │   Security:                              │    │
│  │  ├─ Change Password                        │    │
│  │  ├─ Session Timeout: 30 min                │    │
│  │  └─ Two-Factor Auth: OFF                   │    │
│  │                                            │    │
│  │   Preferences:                           │    │
│  │  ├─ Default LLM: Claude                    │    │
│  │  ├─ Cache TTL: 5 min                       │    │
│  │  └─ Log Level: info                        │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │ Memory Viewer                              │    │
│  │                                            │    │
│  │   Indexed Documents:                     │    │
│  │  ├─ Godot 4.6 Docs (installed)             │    │
│  │  ├─ React Hooks Guide (installed)          │    │
│  │  ├─ Web search results (temp, auto-clean)  │    │
│  │  └─ Custom docs (uploaded)                 │    │
│  │                                            │    │
│  │   Chat History:                          │    │
│  │  ├─ "What is Observer pattern?" (3h ago)   │    │
│  │  ├─ "How to use hooks?" (2h ago)           │    │
│  │  └─ "Best practices..." (1h ago)           │    │
│  │                                            │    │
│  │   Execution Logs:                        │    │
│  │  ├─ [View recent queries]                  │    │
│  │  ├─ [Download logs]                        │    │
│  │  └─ [Clear old logs]                       │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │ Dataset Manager (VAL Registry)             │    │
│  │                                            │    │
│  │   Installed Datasets:                    │    │
│  │  ├─ godot-4.6-docs (v4.6.1)                │    │
│  │  │  └─ [Uninstall] [Update] [Details]      │    │
│  │  ├─ react-hooks-guide (v2.1.0)             │    │
│  │  │  └─ [Uninstall] [Update] [Details]      │    │
│  │  └─ custom-company-docs (v1.0.0)           │    │
│  │     └─ [Uninstall] [Update] [Details]      │    │
│  │                                            │    │
│  │   Browse VAL Registry:                   │    │
│  │  ├─ [Search available datasets]            │    │
│  │  ├─ [Featured this month]                  │    │
│  │  └─ [Community contributions]              │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  [Logout]  [Help]  [GitHub]  [Docs]                 │
└──────────────────────────────────────────────────────┘
```

**Dashboard permite:**

- Configurar chaves de API (sem exigir código)
- Visualizar histórico de memory
- Gerenciar datasets (install, uninstall, update)
- Monitorar performance (queries/min, latência)
- Alterar senha e preferências
- Tudo via interface web (não requer CLI)

**Por que Dashboard é importante:**

- Usuários non-technical podem usar Vectora
- Configuração segura (sem expor chaves em código)
- Visibilidade de o que está acontecendo
- Gerenciamento sem terminal

---

## Stack Técnico (Simplificado)

O stack prioriza Go, LangChainGo e armazenamento local para manter baixa latencia e deploy simples.

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Frontend (User-Facing)                             │
│  ├─ React 18 + Vite (dashboard)                     │
│  ├─ TypeScript (type safety)                        │
│  └─ TailwindCSS (styling)                           │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Backend (Core Logic)                               │
│  ├─ Go 1.21+ (performance, concurrency)             │
│  ├─ Echo/Chi (HTTP router)                          │
│  ├─ GORM (database ORM)                             │
│  └─ Cobra (CLI framework)                           │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Vector & Memory                                    │
│  ├─ LanceDB (vector search, local)                  │
│  ├─ PostgreSQL embedded (metadata)                  │
│  ├─ Redis (cache + Pub/Sub)                         │
│  └─ Voyage AI SDK (embeddings + rerank)             │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ML/AI                                              │
│  ├─ Python 3.10+ (Vectora Cognitive Runtime separate repo)                │
│  ├─ PyTorch (model training)                        │
│  ├─ ONNX (model export, 35MB)                       │
│  └─ ONNX Runtime (4-8ms inference)                  │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  DevOps & Distribution                              │
│  ├─ Docker Compose (local development)              │
│  ├─ GitHub Actions (CI/CD)                          │
│  ├─ Package managers (brew, apt, winget)            │
│  └─ Pre-commit hooks (code quality)                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Por que esse stack?**

- **Go:** Rápido, concorrente, binário único (CLI perfeito)
- **React:** Interativo, modern, comunidade grande
- **LanceDB:** Vector search local, zero config
- **PostgreSQL embedded:** Robusto, sem servidor separado
- **Python (Vectora Cognitive Runtime):** ML libraries maduras, training rápido
- **ONNX:** Modelo pequeno (35MB), portável, rápido

---

## Estrutura do Monorepo

O workspace do Vectora está organizado nestas pastas:

- `vectora/`: produto principal com backend Go, frontend React e CLI
- `vectora-asset-library/`: registry público de assets e datasets
- `vectora-cognitive-runtime/`: VCR, o engine de decisão em Python
- `vectora-integrations/`: Turborepo com SDKs e adaptadores
- `vectora-website/`: site oficial e documentação Hugo/Hextra

**Por que esse formato?**

- **Separação clara:** cada domínio evolui no seu próprio diretório
- **Publicação independente:** cada área pode ter release/versionamento próprio
- **Desenvolvimento paralelo:** times trabalham sem acoplamento desnecessário
- **Documentação centralizada:** o conteúdo oficial vive em `vectora-website/content/`

---

## Fluxo de Dados (End-to-End)

O fluxo abaixo mostra como uma pergunta vira contexto recuperado, resposta e memoria persistida.

```
USUARIO (Claude Code)
  │
  │ "Ajude com React hooks"
  │
  ├──────────────────┐
  │                  │
  │ Agent Mode       │ Tool Mode
  │ (full RAG)       │ (structured)
  │                  │
  └────────┬─────────┴────────────────┐
           │                         │
    POST /api/v1/          POST /api/v1/knowledge/store
    chat/message           GET /api/v1/memory/query
           │               POST /api/v1/tools/websearch
           │               POST /api/v1/tools/rerank
           │                         │
           │                         │
    ┌──────▼───────────────────────────┐
    │  Vectora Backend                  │
    │                                  │
    │  RAG ORCHESTRATOR:               │
    │  1. Vector Search (LanceDB)      │
    │     └─ top-10 resultados         │
    │                                  │
    │  2. Rerank (Voyage v2.5)         │
    │     └─ top-5 reordenados         │
    │                                  │
    │  3. Optional: Web Search         │
    │     └─ se query não encontrado   │
    │                                  │
    │  4. Build Context (Agent Mode)   │
    │     └─ prepara prompt            │
    │                                  │
    │  5. Call LLM (Agent Mode only)   │
    │     └─ Claude/OpenAI             │
    │                                  │
    │  6. Store in Memory              │
    │     └─ LanceDB + PostgreSQL      │
    └──────┬───────────────────────────┘
           │
    ┌──────▼──────────────────────────┐
    │  RESPONSE (JSON)                 │
    │  ├─ result / response            │
    │  ├─ context_used (docs)          │
    │  ├─ sources (URLs)               │
    │  ├─ confidence (0-1)             │
    │  └─ metadata                     │
    └──────┬──────────────────────────┘
           │
    CLAUDE CODE (Recebe resposta)
    ├─ Usa no contexto
    ├─ Apresenta ao usuário
    └─ Opcionalmente armazena análise
       (POST /api/v1/knowledge/store)
```

---

## Key Features by Priority

As fases organizam o que entra primeiro no produto e o que fica para estabilizacao, ecossistema e uso enterprise.

### Phase 1 (MVP — 8 weeks)

A primeira fase entrega autenticacao, API key, RAG, dashboard, CLI e base local de deploy.

- User authentication (email + password)
- RAG orchestrator (search + rerank + LLM)
- Agent Mode (chat → LLM → response)
- Tool Mode (knowledge.store, memory.query)
- Dashboard (settings, memory viewer)
- CLI (init, start, auth, dataset)
- Docker Compose (local dev)

### Phase 2 (Stabilization — 4 weeks)

A segunda fase foca em qualidade, testes, performance e feedback real de uso.

- Comprehensive testing (E2E, load, security)
- Performance baselines
- Bug fixes + user feedback

### Phase 3 (Ecosystem — 8 weeks)

A terceira fase amplia integracoes, adapters e datasets comunitarios.

- Claude Code MCP integration
- Gemini CLI adapter
- Web search integration (SerpAPI)
- VAL Registry (community datasets)
- Monitoring (Prometheus + Sentry)

### Phase 4 (Enterprise — 6 weeks)

A quarta fase adiciona recursos operacionais para ambientes com multiplos usuarios e controle administrativo.

- Caching optimization
- System Tray (Windows)
- Package manager distribution
- RBAC + multi-user
- Auto-updates

### Phase 5 (Ongoing)

A fase continua cobre evolucao de grafo de conhecimento, plugins e crescimento da comunidade.

- Knowledge graphs
- Multi-agent orchestration
- SSO/SAML (enterprise)
- Plugin ecosystem
- Community growth

---

## Constraints & Guarantees

Estas restricoes definem o comportamento minimo esperado para que o Vectora continue local-first e previsivel.

### Must-Have (Non-Negotiable)

Os requisitos abaixo nao devem ser sacrificados durante a implementacao.

- Roda em KVM1: 2 vCPU, 4GB RAM, 50GB NVMe
- Open-source (Apache 2.0)
- Zero vendor lock-in
- Multi-agent compatible
- RAG + LLM agnostic

### Performance Targets

As metas de performance orientam as escolhas de armazenamento, cache e execucao.

- API response < 500ms p95
- Vector search < 150ms p95
- Vectora Cognitive Runtime inference 4-8ms
- Memory usage < 1.5GB peak

### Security

A seguranca precisa cobrir usuario, organizacao, API keys derivadas e buckets privados por agent.

- Per-user data isolation
- Encryption at rest (AES-256)
- JWT for auth
- bcrypt for passwords
- No secrets in logs

### Scalability

A escala esperada considera uso local e organizacoes pequenas antes de ambientes distribuidos maiores.

- Suporta 100+ users localmente
- 1M+ vectors em LanceDB
- Goroutines para concorrência
- Redis Pub/Sub para invalidation

---

## Why Vectora Matters

O valor do Vectora vem de reduzir perda de contexto entre agents e execucoes repetidas.

### Problem it Solves

Agents sem memoria compartilhada repetem trabalho e perdem conhecimento util entre sessoes.

- Agents isolated = cada um guarda seu conhecimento
- Código repetido = pattern, insight, análise são perdidos
- Sem memória = agent repete análise mesma coisa n vezes
- Multi-agent ineficiente = agents não compartilham contexto

### Vectora Solution

A solucao combina memoria privada por agent com buckets publicos compartilhados e exportacao controlada.

- **Shared Memory** — todos agents acessam mesmo knowledge base
- **Semantic Search** — encontra contexto relevante automaticamente
- **Intelligence Reuse** — análise anterior reutilizada
- **Agent Orchestration** — múltiplos agents colaboram
- **Persistent Learning** — sistema aprende ao longo do tempo

### For Who

Os publicos abaixo representam os primeiros casos de uso do projeto.

- **Developers** — integram Vectora em seus agents/tools
- **Companies** — deploy local, zero cloud lock-in
- **Communities** — podem contribuir datasets + integrações
- **Enterprise** — self-hosted, RBAC, audit logs

---

## Quick Start (Depois de implementação)

Os comandos abaixo descrevem o fluxo esperado para a primeira versao instalavel.

```bash
# Install
brew install vectora  # ou apt, winget, etc

# Initialize
vectora init
# → cria ~/.vectora (config + embeddings)
# → inicia PostgreSQL embedded
# → inicia Redis
# → pronto para usar

# Start
vectora start
# → servidor roda em http://localhost:3000
# → dashboard em web browser
# → aguardando queries

# Use via CLI
vectora query "What is React hooks?"
# → busca docs, reranqueia, chama Claude
# → retorna resposta + sources

# Use via Dashboard
# → Abre browser, login, settings, memory viewer

# Use via Agent (Claude Code)
# → Claude Code chama /api/v1/chat/message
# → ou /api/v1/knowledge/store (Tool Mode)
```

---

## Comparison: Vectora vs Alternatives

A comparacao destaca o posicionamento do Vectora frente a alternativas de RAG e memoria para agents.

| Feature                | Vectora        | LangChain      | RAGstack | Llamaindex    |
| ---------------------- | -------------- | -------------- | -------- | ------------- |
| **Local-first**        | Yes            | Cloud-oriented | Yes      | Cloud-focused |
| **Multi-agent**        | Native         | Possible       | Possible | Single agent  |
| **Zero config**        | Docker Compose | Complex setup  | Moderate | Moderate      |
| **KVM1 viable**        | Yes (<1.5GB)   | Borderline     | Yes      | Tight         |
| **Open-source**        | Apache 2.0     | MIT            | Various  | MIT           |
| **Dashboard**          | Built-in       | No             | External | No            |
| **Package mgrs**       | (Phase 4)      | pip/npm        | No       | pip only      |
| **Community datasets** | VAL Registry   | No             | No       | No            |
| **Cost**               | Free           | Free           | Free     | Free          |
| **Maturity**           | Pre-release    | Mature         | Alpha    | Mature        |

---

## Roadmap Visual

A linha do tempo resume as fases de entrega planejadas.

```
2026
 Q2 [Phase 1: MVP]      [Phase 2: Stabilize]
    May    Jun         July      Aug
    ├─────────────────────────────┤
    │ Backend ││ Testing
    │ Frontend││ Feedback
    │ CLI     ││ Optimization
    │ Docker  ││

 Q3 [Phase 3: Features]          [Phase 4: Enterprise]
    Sep    Oct         Nov      Dec    Jan
    ├─────────────────────────────┤
    │ Integrations │ Performance
    │ VAL Registry │ Package mgrs
    │ Web Search   │ System Tray

 2027 [Phase 5: Ecosystem — Ongoing]
    │ Community │ Advanced │ Enterprise │
    │ Growth    │ Features │ Support    │
```

---

## Contact & Community

Os canais abaixo concentram codigo, discussao, documentacao e contribuicoes.

- **GitHub:** github.com/vectora/vectora
- **Discord:** discord.gg/vectora (Phase 5)
- **Docs:** vectora.ai (Phase 3)
- **Contributing:** github.com/vectora/vectora/CONTRIBUTING.md

---

## tl;dr

A sintese final concentra a proposta principal do Vectora em poucos pontos.

**Vectora** = Knowledge hub inteligente que:

- Busca semanticamente (Vector search)
- Reordena localmente (Reranking)
- Integra com LLMs (Agent Mode)
- Funciona como ferramenta (Tool Mode)
- Persiste memória (Multi-user isolation)
- Funciona em KVM1 (2 vCPU, 4GB RAM)
- Roda localmente (Open-source, zero cloud)
- Integra agents (Claude Code, Gemini, Paperclip, etc)

**Próximos passos:**

1. Implementar Phase 1 (8 semanas)
2. Testar com usuários reais (Phase 2)
3. Expandir integrations (Phase 3)
4. Otimizar performance (Phase 4)
5. Crescer comunidade (Phase 5 — ongoing)

**Let's build the future of AI agents together!**

---

**Document Version:** 1.0
**Last Updated:** 2026-05-01
**Status:** Approved for Implementation
