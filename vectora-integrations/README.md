# Vectora Integrations: Turborepo com SDKs para Múltiplos Agentes

Vectora Integrations é um monorepo Turborepo que contém todos os SDKs e adaptadores para conectar diferentes agentes ao Vectora. Cada integração traduz o protocolo específico do agente (MCP, REST, Plugin) para as APIs padrão do Vectora, permitindo que Claude Code, Gemini CLI, Paperclip, Hermes, e agentes customizados acessem o mesmo backend Vectora compartilhado. Todas as integrações compartilham tipos, autenticação, e cliente HTTP via @vectora/shared.

## Stack

O stack de integrations usa TypeScript como linguagem única, Turborepo para gerenciar múltiplos packages interdependentes, e pnpm para package management. Cada integração é um package NPM independente (@vectora/sdk-\*) que pode ser instalado via npm. Shared package fornece tipos, autenticação, e utilitários HTTP para evitar duplicação. Todas as integrações comunicam com o Vectora backend via REST ou MCP protocol.

- **Monorepo:** Turborepo (caching, parallel builds)
- **Package Manager:** pnpm (workspace, faster)
- **Language:** TypeScript (type-safe across all packages)
- **Shared Utilities:** @vectora/shared (types, auth, HTTP client, errors)
- **Integration Protocols:** MCP (Claude Code), REST (Gemini, Hermes, custom)
- **Publishing:** npm registry (@vectora/sdk-claude-code, @vectora/sdk-gemini-cli, etc)
- **Testing:** Jest (@testing-library/react for components)
- **CI/CD:** GitHub Actions (lint, test, build, publish to npm)

## Mapa Mental

Arquitetura hub-and-spoke onde Vectora backend é o centro, e cada integração é um spoke que adapta seu protocolo específico para as APIs padrão do Vectora. @vectora/shared fornece a coluna vertebral (types, auth, HTTP client) que todas as integrações usam. Cada integração é independente em versioning e publish, mas compartilha tipos comuns para consistência.

```
┌──────────────────────────────────────────────────────────────┐
│                       @vectora/shared                         │
│          (Types, Auth, HTTP Client, Error Handling)          │
└───────────────┬────────┬────────┬─────────┬────────┬─────────┘
                │        │        │         │        │
        ┌───────▼──┐ ┌──▼──────┐ ┌──────┐  │   ┌─────▼──────┐
        │ Claude   │ │ Gemini  │ │Paper │  │   │ Custom     │
        │ Code     │ │ CLI     │ │ clip │  │   │ Template   │
        │ (MCP)    │ │ (REST)  │ │(REST)│  │   │ (Template) │
        └────┬─────┘ └────┬────┘ └──┬───┘  │   └──────┬──────┘
             │            │        │      │          │
             └────────────┼────────┼──────┼──────────┘
                          │        │      │
                 ┌────────▼────────▼──────▼────────┐
                 │   Vectora Backend (Go)           │
                 │   HTTP REST API + MCP Protocol  │
                 └─────────────────────────────────┘
```

## Estrutura

Monorepo Turborepo com packages compartilhados (shared) e packages específicos para cada integração. Cada package tem seu próprio tsconfig, package.json, e pode ser published independentemente. Shared package é a dependência comum que fornece tipos, autenticação, e utilitários.

```
vectora-integrations/
├── packages/
│   ├── shared/                          (@vectora/shared)
│   │   ├── src/
│   │   │   ├── types/
│   │   │   │   ├── vectora.ts           (Vectora API types)
│   │   │   │   ├── agents.ts           (Agent types)
│   │   │   │   └── auth.ts             (Auth types)
│   │   │   ├── auth/
│   │   │   │   ├── jwt.ts
│   │   │   │   └── encryption.ts
│   │   │   ├── http/
│   │   │   │   └── client.ts           (HTTP client wrapper)
│   │   │   ├── errors/
│   │   │   │   └── index.ts            (Error types)
│   │   │   └── constants.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── claude-code/                     (@vectora/sdk-claude-code)
│   │   ├── src/
│   │   │   ├── mcp/
│   │   │   │   ├── server.ts           (MCP protocol server)
│   │   │   │   ├── handlers.ts         (Tool handlers)
│   │   │   │   └── types.ts
│   │   │   ├── client.ts               (Vectora client)
│   │   │   ├── tools/
│   │   │   │   ├── search.ts           (Vector search tool)
│   │   │   │   ├── rerank.ts           (Reranking tool)
│   │   │   │   ├── websearch.ts        (Web search tool)
│   │   │   │   └── knowledge.ts        (Knowledge store tool)
│   │   │   └── index.ts
│   │   ├── examples/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── README.md
│   │
│   ├── gemini-cli/                      (@vectora/sdk-gemini-cli)
│   │   ├── src/
│   │   │   ├── client.ts               (Gemini client wrapper)
│   │   │   ├── vectora-adapter.ts       (REST adapter to Vectora)
│   │   │   ├── tools.ts                (Tool definitions)
│   │   │   └── index.ts
│   │   ├── examples/
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── paperclip/                       (@vectora/sdk-paperclip)
│   │   ├── src/
│   │   │   ├── plugin.ts               (Paperclip plugin)
│   │   │   ├── mcp-bridge.ts           (MCP protocol bridge)
│   │   │   ├── rest-bridge.ts          (REST API bridge)
│   │   │   └── index.ts
│   │   ├── examples/
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── hermes/                          (@vectora/sdk-hermes)
│   │   ├── src/
│   │   │   ├── client.ts               (Hermes client)
│   │   │   ├── vectora-adapter.ts       (REST adapter)
│   │   │   └── index.ts
│   │   ├── examples/
│   │   ├── package.json
│   │   └── README.md
│   │
│   └── custom-template/                 (Template para custom agents)
│       ├── src/
│       │   ├── client.ts
│       │   ├── adapter.ts
│       │   └── index.ts
│       ├── package.json
│       └── README.md
│
├── apps/
│   └── docs/                            (Integration documentation)
│       ├── content/
│       ├── package.json
│       └── next.config.js
│
├── turbo.json                           (Turborepo config)
├── pnpm-workspace.yaml                  (pnpm workspace)
├── tsconfig.base.json                   (Base TypeScript config)
├── package.json
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── build.yml
│       └── publish.yml
├── .gitignore
├── README.md
└── LICENSE
```

---

## Development Setup

```bash
git clone https://github.com/vectora/vectora-integrations.git
cd vectora-integrations

# Install dependencies (pnpm)
pnpm install

# Build all packages (with Turborepo caching)
turbo build

# Run tests
turbo test

# Publish to npm (from CI/CD, not local)
turbo publish
```

## Publishing Packages

Cada package é published independentemente para npm:

```bash
npm install @vectora/shared
npm install @vectora/sdk-claude-code
npm install @vectora/sdk-gemini-cli
# ... etc
```

## License

Apache 2.0
