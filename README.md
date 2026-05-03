# VECTORA — Executive Overview

Vectora centraliza memoria, busca, contexto e permissoes para agents que precisam colaborar sem perder isolamento operacional.

## O que e Vectora?

Vectora e um hub de conhecimento inteligente open-source para agents, construido em Go e orquestrado com LangChainGo. Ele combina busca vetorial, reranking, integracao com LLMs, memoria persistente e permissoes separadas por agent.

**Vectora** gerencia processamento e analise de dados com:

- **Busca vetorial** - busca semantica em documentos com LanceDB e Voyage embeddings.
- **Reranking local** - reordena resultados localmente com Voyage v2.5, sem API adicional.
- **Busca web** - integra resultados da web via SerpAPI.
- **Integracao com LLMs** - conecta Claude, OpenAI e Google por meio de LangChainGo.
- **Sistema de memoria** - persiste conhecimento em vector db, PostgreSQL, Redis e buckets de contexto.
- **Compatibilidade multi-agent** - integra com Claude Code, Gemini CLI, Paperclip e outros agents.
- **Permissoes separadas por agent** - cada agent pode operar com API key propria e bucket privado completo.
- **Contexto exportavel** - dados podem ser exportados e importados entre usuarios, organizacoes e agents autorizados.

**NÃO é:**

- SaaS proprietary
- Chat interface genérica
- Apenas wrapper de RAG
- Dependente de nuvem

**E:**

- Open-source, rode localmente em KVM1 (2 vCPU, 4GB RAM).
- Knowledge hub com inteligencia reutilizavel.
- Orquestrador com suporte a Agent Mode e Tool Mode.
- Multi-agent com permissoes, memoria e contexto separados.
- Exportavel entre agents quando a hierarquia de permissoes autorizar.

---

## Mapa Mental Completo

A visao abaixo resume os componentes principais e as relacoes entre modos de uso, backend e dados persistidos.

```
┌─────────────────────────────────────────────────────────────┐
│                     Vectora                                  │
│          Knowledge Hub Inteligente                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼──┐       ┌──▼──┐       ┌──▼────────┐
    │AGENT │       │TOOL │       │Dashboard  │
    │MODE  │       │MODE │       │ & CONFIG  │
    │(LLM) │       │     │       │           │
    │      │       │     │       │(Web UI)   │
    └───┬──┘       └──┬──┘       └──┬────────┘
        │              │             │
        └──────────────┼─────────────┘
                       │
   ┌───────────────────▼────────────────────┐
   │    Vectora Backend (Go)                 │
   │                                        │
   │  ┌─────────────────────────────────┐   │
   │  │   RAG Orchestrator              │   │
   │  │  ├─ Vector Search (LanceDB)     │   │
   │  │  ├─ Rerank (Voyage v2.5)        │   │
   │  │  ├─ Web Search (SerpAPI)        │   │
   │  │  └─ LLM Integration (multi)     │   │
   │  └─────────────────────────────────┘   │
   │                                        │
   │  ┌─────────────────────────────────┐   │
   │  │   Memory Management             │   │
   │  │  ├─ Knowledge Storage           │   │
   │  │  ├─ Context Building            │   │
   │  │  └─ Per-user Isolation          │   │
   │  └─────────────────────────────────┘   │
   │                                        │
   │  ┌─────────────────────────────────┐   │
   │  │   Protocol Handlers             │   │
   │  │  ├─ REST API (/api/v1/*)        │   │
   │  │  ├─ MCP (Model Context Proto)   │   │
   │  │  └─ WebSocket (real-time)       │   │
   │  └─────────────────────────────────┘   │
   └────────┬────────────────────┬──────────┘
            │                    │
      ┌─────▼──┐          ┌──────▼────┐
      │LanceDB │          │PostgreSQL │
      │Vectors │          │Metadata   │
      │(local) │          │+ Cache    │
      └────────┘          └───────────┘
            ▲                    ▲
            │                    │
      ┌─────┴────────────────────┴─────────┐
      │                                    │
   ┌──▼──┐  ┌───────────┐  ┌──────────┐  │
   │Redis│  │Voyage API │  │SerpAPI   │  │
   │Pub/ │  │(Embed +   │  │(Web      │  │
   │Sub  │  │Rerank)    │  │Search)   │  │
   └─────┘  └───────────┘  └──────────┘  │
            │                             │
            └─────────────────────────────┘
```

---

## 2 Modos Operacionais

Os modos operacionais separam quando o Vectora decide a resposta e quando ele atua como ferramenta estruturada para outro agent.

### Mode 1: Agent Mode (Full RAG — Modo Orquestrador)

Nesse modo, o Vectora executa o ciclo completo de busca, reranking, contexto e chamada ao LLM.

```
┌─────────────────────────────────┐
│  Agente Externo (Claude Code)   │
│  "Ajude com React hooks"         │
└──────────────┬──────────────────┘
               │ POST /api/v1/chat/message
               │
   ┌───────────▼──────────────┐
   │  Vectora Backend          │
   │                          │
   │  1. Vector Search        │
   │     └─ encontra docs     │
   │                          │
   │  2. Rerank               │
   │     └─ ordena top-5      │
   │                          │
   │  3. Web Search           │
   │     └─ se necessário     │
   │                          │
   │  4. Build Context        │
   │     └─ prepara prompt    │
   │                          │
   │  5. Call LLM             │
   │     └─ Claude/OpenAI     │
   │                          │
   │  6. Return Response      │
   │     └─ + save to memory  │
   └───────────┬──────────────┘
               │
   ┌───────────▼──────────────────────┐
   │ Response: JSON com resposta       │
   │ + contexto + metadata             │
   │                                  │
   │ {                                │
   │   "response": "React hooks ...",  │
   │   "sources": [...],              │
   │   "confidence": 0.92,            │
   │   "tools_used": ["search"]       │
   │ }                                │
   └──────────────────────────────────┘
```

**Quando usar Agent Mode:**

- Agent precisa de resposta completa + contexto
- Decisão é crítica (precisa de LLM)
- Quer que Vectora decida qual LLM usar (routing)
- Resultado é único e determinístico

**Exemplo:**

```
Claude Code: "O que é o padrão Observer em TypeScript?"
→ Vectora busca docs de design patterns
→ Reranqueia, pega top-3
→ Chama Claude API com contexto
→ Responde com explicação + exemplos
→ Salva em memory para futuras queries
```

---

### Mode 2: Tool Mode (Structured Integration — Modo Ferramenta)

Nesse modo, o agent externo chama endpoints especificos e usa os dados retornados em sua propria analise.

```
┌─────────────────────────────────┐
│  Agente Externo (Claude Code)   │
│  (análise própria)              │
└──────────────┬──────────────────┘
               │
     ┌─────────┴─────────┬───────────┬──────────┐
     │                   │           │          │
   ┌─▼──┐          ┌────▼──┐   ┌────▼───┐  ┌──▼──────┐
   │POST │          │GET    │   │POST    │  │GET      │
   │knowledge       │memory │   │tools/  │  │tools/   │
   │/store          │/query │   │rerank  │  │websearch│
   └─┬──┘          └────┬──┘   └────┬───┘  └──┬──────┘
     │                  │           │         │
   [1]              [2]           [3]       [4]
   Save            Query          Rerank    Web
   analyzed        embeddings     documents Search
   results         (sem LLM)      locally   + Fetch

     │                  │           │         │
     └──────────────────┴───────────┴─────────┘
                        │
       ┌────────────────▼────────────────┐
       │   Agent usa resultados          │
       │   em sua própria análise        │
       │                                │
       │   (Vectora = storage +           │
       │    retrieval, não decisão)      │
       └────────────────────────────────┘
```

**Quando usar Tool Mode:**

- Agent tem sua própria inteligência (faz análise)
- Agent precisa **armazenar** conhecimento (knowledge.store)
- Agent quer **buscar** contexto sem decisão (memory.query)
- Agent quer **reranquear** documentos localmente
- Agent quer **buscar na web** sem passar por LLM

**Exemplo:**

```
Claude Code (análise própria):
  1. Analisa código do usuário
  2. POST /api/v1/knowledge/store
     └─ salva "padrão Observer detectado em UserObserver.ts"
  3. Depois, GET /api/v1/memory/query?q=observer
     └─ encontra análise anterior
  4. Usa contexto na próxima análise
  5. POST /api/v1/tools/websearch?q=observer pattern
     └─ busca web, fetch conteúdo, armazena
```

---

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
