# Vectora: AI Knowledge Agent Platform

Vectora é um knowledge hub inteligente que orquestra processamento de dados, RAG (Retrieval-Augmented Generation), e gerenciamento de memória para múltiplos agentes (Claude Code, Gemini CLI, Paperclip, etc). Roda localmente em qualquer VPS, sem vendor lock-in, com isolamento por usuário e suporte para 50+ agentes simultâneos. Este repositório contém o backend Go, frontend React, CLI, e o decision engine Python (Vectora Cognitive Runtime).

## Stack

O Vectora é construído com uma arquitetura polyglot, escolhendo a melhor ferramenta para cada camada. Backend em Go para performance e concorrência, frontend em React + Vite para UX moderna, e Python para o decision engine especializado. Banco de dados usa Embedded PostgreSQL para simplicidade de deploy, LanceDB para busca vetorial, e Redis para caching de respostas e invalidação de cache.

- **Backend:** Go 1.21+, Echo/Chi, GORM, Embedded PostgreSQL, LanceDB, Redis, JWT + bcrypt + AES-256, slog
- **Frontend:** React 19+, Vite 5+, TypeScript, TailwindCSS, Zustand, SWR, WebSocket
- **CLI:** Go + Cobra, Viper (config), Charmbracelet (formatting)
- **Vectora Cognitive Runtime:** PyTorch 2.1+, Transformers, PEFT (LoRA), ONNX Runtime (INT4, 35MB)
- **Docker:** Docker Compose (LanceDB, Redis, Vectora backend + Vectora Cognitive Runtime)

## Mapa Mental

Fluxo de dados centralizado onde requisições chegam via HTTP, são enriquecidas com contexto via LanceDB, passam pelo Vectora Cognitive Runtime para decisão, e executam a estratégia escolhida. Tudo isolado por user_id com cache em Redis. Múltiplos agentes (Paperclip, Claude Code, Gemini) se comunicam com um único Vectora singleton, compartilhando memória mas com isolamento lógico total.

```
┌──────────────────────────────────────────────────────────────┐
│                   Paperclip Agents (50 users)                │
│                                                              │
│  Agent A  Agent B  Agent C  ...  Agent Z                     │
└─────────────────────────┬──────────────────────────────────┘
                          │ HTTP REST
                          ▼
        ┌──────────────────────────────────────────┐
        │   Vectora Backend (Singleton - Go)        │
        │                                          │
        │  1. Enrich Query (LanceDB + memory)      │
        │  2. Vectora Cognitive Runtime Decision (Agent/Tool/Web Search) │
        │  3. Execute (Call LLM or return chunks)  │
        │  4. Cache Response (Redis, TTL 5min)     │
        │                                          │
        │  Isolação: user_id em todas as queries   │
        │  Cache: 3ms hit, 1610ms cold             │
        └──────────────────────────────────────────┘
```

## Estrutura

Arquitetura tier-based de 8 camadas, cada uma com responsabilidade clara. Backend em Go com tier separation (config → platform → storage → llm → core → api → mcp → shared), frontend React com estrutura componentizada, CLI separado, Vectora Cognitive Runtime em Python subdiretório.

```
vectora/
├── backend/
│   ├── cmd/
│   │   ├── server/main.go
│   │   └── cli/main.go
│   ├── internal/
│   │   ├── config/              (Tier 1: Configuration)
│   │   ├── platform/            (Tier 2: crypto, auth, logger)
│   │   ├── storage/             (Tier 3: db, vector, models)
│   │   ├── llm/                 (Tier 4: LLM integration)
│   │   ├── core/                (Tier 5: RAG + memory)
│   │   ├── api/                 (Tier 6: HTTP handlers + 6 middlewares)
│   │   ├── mcp/                 (Tier 7: MCP protocol)
│   │   └── shared/              (Tier 8: errors, types, constants)
│   ├── vectora-cognitive-runtime/                     (Python: PyTorch, Transformers, PEFT, ONNX)
│   ├── migrations/
│   ├── tests/
│   ├── go.mod
│   ├── Dockerfile
│   └── Makefile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── api/
│   │   ├── types/
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── cli/
│   ├── cmd/
│   ├── internal/
│   ├── go.mod
│   └── Dockerfile
├── infra/
│   ├── docker-compose.yml
│   └── scripts/
├── docs/
├── .github/workflows/
└── LICENSE
```

---

## Development Setup

```bash
git clone https://github.com/vectora/vectora.git
cd vectora
cp .env.example .env
docker-compose up -d
```

- Backend: http://localhost:3000
- Frontend dev: http://localhost:5173
- Redis: localhost:6379
- LanceDB: http://localhost:8081

## License

Apache 2.0
