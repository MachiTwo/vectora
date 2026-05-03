# Documentação da Stack do Vectora

**Vectora é um runtime local-first instalável, controlado por CLI, com interface web integrada.** Não é SaaS, não é cloud-native. É um produto que o usuário instala em sua máquina ou VPS e roda 24/7, como Paperclip.

Stack de tecnologia completa: todas as aplicações internas, bibliotecas externas, infraestrutura local, CLI, distribuição e deployment em VPS.

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Protocolos de Comunicação](#protocolos-de-comunicação)
3. [Instalação e Distribuição](#instalação-e-distribuição)
4. [CLI Vectora](#cli-vectora)
5. [Runtime Local](#runtime-local)
6. [API Backend](#api-backend)
7. [Frontend Web](#frontend-web)
8. [Vectora Cognitive Runtime](#vectora-cognitive-runtime)
9. [SDK de Integrações](#sdk-de-integrações)
10. [Banco de Dados e Armazenamento](#banco-de-dados-e-armazenamento)
11. [Pipeline de Ingestão](#pipeline-de-ingestão)
12. [Background Jobs](#background-jobs)
13. [Configuração Local](#configuração-local)
14. [Segurança e Autenticação](#segurança-e-autenticação)
15. [Observabilidade Local-First](#observabilidade-local-first)
16. [DevOps e Deployment](#devops-e-deployment)
17. [Website e Documentação](#website-e-documentação)
18. [Testes e Qualidade](#testes-e-qualidade)
19. [Release Engineering](#release-engineering)

---

## Visão Geral

**Vectora** é um sistema de IA local-first que roda em máquinas individuais ou VPS. Usuários instalam via CLI, gerenciam via `vectora` CLI, e acessam via interface web em `http://localhost:8000`.

### Arquitetura

```
┌──────────────────────────────────────────────────────────────────┐
│  Usuario (Navegador → http://localhost:8000)                     │
└────────────────────────┬─────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐     ┌───▼────┐     ┌──▼────────┐
    │Frontend  │     │Backend  │     │  External │
    │React+    │     │FastAPI  │     │  Agents   │
    │Vite      │     │LangChain│     │(MCP REST) │
    └────┬────┘     └────┬────┘     └──────────┘
         │                │
         └────────┬───────┘
                  │
    ┌─────────────┼──────────────────┐
    │             │                  │
┌───▼──┐    ┌────▼──┐    ┌──────┐  ┌▼────────┐
│ VCR  │    │Postgres│   │Lance │  │  Redis  │
│(Py)  │    │embedded│   │  DB  │  │embedded │
└──────┘    └────────┘   └──────┘  └─────────┘
    │
    └─ ~/.vectora/ (config, models, data)

┌──────────────────────────┐
│  CLI: vectora start      │
│  CLI: vectora status     │
│  CLI: vectora logs       │
│  CLI: vectora backup     │
└──────────────────────────┘
```

---

## Protocolos de Comunicação

Vectora expõe múltiplas interfaces para Web UI, CLI, agentes externos e integrações. Os protocolos são camadas centrais da arquitetura, não detalhes secundários.

### REST API

REST é a interface principal para Web UI, CLI e integrações HTTP simples.

| Aspecto           | Detalhes                             |
| ----------------- | ------------------------------------ |
| **Protocol**      | HTTP REST                            |
| **Payload**       | JSON                                 |
| **Streaming**     | Server-Sent Events (SSE) / WebSocket |
| **Autenticação**  | JWT Bearer Token                     |
| **Rate Limiting** | Por IP + por token                   |

**Endpoints Principais:**

```
# Health & Diagnostics
GET    /health                     → Status básico
GET    /ready                      → Readiness probe (DB, Redis, LanceDB)
GET    /metrics                    → Prometheus format

# Authentication
POST   /api/v1/auth/login          → JWT token
POST   /api/v1/auth/refresh        → Novo token
POST   /api/v1/auth/logout         → Invalidar token

# Chat & Search
POST   /api/v1/chat                → Query com RAG
GET    /api/v1/chat/:id            → Histórico sessão
POST   /api/v1/search              → Vector search
GET    /api/v1/search/:id/stream   → SSE streaming

# Memory
POST   /api/v1/memory              → Store custom memory
GET    /api/v1/memory              → Retrieve memory
DELETE /api/v1/memory/:id          → Delete memory

# Datasets
POST   /api/v1/datasets            → Upload/criar
GET    /api/v1/datasets            → Listar
GET    /api/v1/datasets/:id        → Details
POST   /api/v1/datasets/:id/ingest → Ingestão assíncrona
GET    /api/v1/datasets/:id/chunks → Listar chunks

# Jobs
GET    /api/v1/jobs/:id            → Job status
GET    /api/v1/jobs/:id/stream     → SSE progress
GET    /api/v1/jobs                → Listar jobs

# Agentes & API Keys
GET    /api/v1/agents              → Agentes conectados
POST   /api/v1/agents/:name/key    → Criar API key
GET    /api/v1/agents/:name/keys   → Listar chaves
DELETE /api/v1/agents/:name/keys/:key_id → Revogar

# Settings
GET    /api/v1/settings            → User settings
POST   /api/v1/settings            → Update settings

# Admin
POST   /api/v1/backup              → Trigger backup
GET    /api/v1/backup/list         → Listar backups
POST   /api/v1/restore             → Restore backup
```

**Consumidores:**

- Web UI (React + Vite)
- Vectora CLI
- Custom HTTP agentes
- Integrations (adapter via REST)

---

### MCP Server

Vectora implementa **Model Context Protocol** para agentes compatíveis com MCP (Claude Code, Gemini, Paperclip, etc).

| Aspecto            | Detalhes                         |
| ------------------ | -------------------------------- |
| **Protocol**       | MCP (Model Context Protocol)     |
| **Message Format** | JSON-RPC 2.0                     |
| **Transport**      | stdio (local), HTTP/SSE (remoto) |
| **Server Role**    | Vectora expõe ferramentas MCP    |
| **Client Role**    | Agentes consomem ferramentas     |

**Ferramentas MCP Expostas:**

```
vectora.search_context
  params: {query, dataset_id, user_id}
  returns: {chunks: [{content, score, source}]}

vectora.rerank
  params: {query, chunks}
  returns: {ranked_chunks: [...]}

vectora.store_memory
  params: {content, metadata}
  returns: {id, stored_at}

vectora.query_memory
  params: {query}
  returns: {results: [{content, score}]}

vectora.ingest_dataset
  params: {dataset_name, file_path}
  returns: {job_id, status: "pending"}

vectora.get_dataset
  params: {dataset_id}
  returns: {id, name, vector_count, metadata}

vectora.web_search
  params: {query}
  returns: {results: [{title, url, snippet}]}

vectora.get_user_context
  params: {}
  returns: {user_id, role, available_datasets}

vectora.execute_tool
  params: {tool_name, params}
  returns: {result}
```

**Fluxo MCP:**

```
Claude Code / Gemini CLI / Paperclip
    ↓ (stdio ou HTTP)
Vectora MCP Server
    ↓
Vectora Backend (FastAPI)
    ↓
PostgreSQL + LanceDB + Redis + VCR
    ↓
Resultado JSON
    ↓
Agente recebe ferramentas + respostas
```

**Consumidores:**

- Claude Code (MCP nativo)
- Gemini CLI (via adapter MCP)
- Paperclip (MCP ou REST bridge)
- Agentes customizados (MCP SDK)

---

### JSON-RPC 2.0

JSON-RPC é usado para comunicação leve entre processos, integrações internas e CLI local.

| Aspecto          | Detalhes                 |
| ---------------- | ------------------------ |
| **Protocol**     | JSON-RPC 2.0             |
| **Transport**    | HTTP, Unix socket, stdio |
| **Autenticação** | Bearer token ou API key  |

**Métodos Internos:**

```
vectora.runtime.status
  → {uptime, version, databases: {postgres, redis, lancedb}}

vectora.runtime.start
  → {pid, port, status}

vectora.runtime.stop
  → {status: "stopped"}

vectora.vcr.decide
  params: {query, context}
  → {action, confidence, parameters}

vectora.vcr.model_info
  → {model, params, trained_on, accuracy}

vectora.storage.health
  → {postgres: ok, redis: ok, lancedb: ok}

vectora.jobs.status
  params: {job_id}
  → {id, status, progress, result}

vectora.jobs.cancel
  params: {job_id}
  → {status: "cancelled"}

vectora.config.get
  params: {key}
  → {value}

vectora.config.set
  params: {key, value}
  → {updated: true}
```

**Exemplo Request:**

```json
{
  "jsonrpc": "2.0",
  "id": "req_xyz_123",
  "method": "vectora.search_context",
  "params": {
    "user_id": "user_abc",
    "query": "Como funciona VCR?",
    "dataset_id": "docs_main",
    "limit": 5
  }
}
```

**Exemplo Response:**

```json
{
  "jsonrpc": "2.0",
  "id": "req_xyz_123",
  "result": {
    "chunks": [
      {
        "content": "VCR usa XLM-RoBERTa-small...",
        "score": 0.92,
        "source": "README.md",
        "chunk_id": 1
      }
    ],
    "total_chunks": 5,
    "query_time_ms": 45
  }
}
```

**Consumidores:**

- Vectora CLI (controle local)
- VCR processo separado (comunicação backend)
- Adapter integrations (simplificar MCP via JSON-RPC)

---

### Streaming: SSE & WebSocket

Para chat em tempo real e progresso de jobs, Vectora usa Server-Sent Events (SSE) ou WebSocket.

**SSE (Recomendado para chat):**

```bash
curl -N -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/chat?stream=true \
  -d '{"query": "..."}' -X POST

# Resposta (one event per chunk):
data: {"chunk": "O Vectora é", "type": "token"}
data: {"chunk": " um sistema", "type": "token"}
data: {"chunk": " de IA local", "type": "token"}
data: {"type": "done", "metadata": {...}}
```

**WebSocket (Bidirecional):**

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/chat/stream");
ws.send(
  JSON.stringify({
    query: "...",
    session_id: "xyz",
  }),
);
ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log(data.chunk);
};
```

---

### Matriz de Protocolos por Consumidor

| Consumidor                | REST         | MCP          | JSON-RPC   | SSE/WS           |
| ------------------------- | ------------ | ------------ | ---------- | ---------------- |
| **Web UI (React)**        | ✅           | -            | -          | ✅ (SSE)         |
| **Vectora CLI**           | ✅           | -            | ✅ (local) | -                |
| **Claude Code**           | -            | ✅           | -          | ✅ (via MCP)     |
| **Gemini CLI**            | ✅ (adapter) | ✅ (adapter) | -          | ✅ (via adapter) |
| **Paperclip**             | ✅ (REST)    | ✅ (native)  | -          | ✅               |
| **Custom HTTP Agent**     | ✅           | -            | ✅         | ✅ (SSE)         |
| **VCR (subprocess)**      | -            | -            | ✅         | -                |
| **External Integrations** | ✅           | ✅           | ✅         | ✅               |

---

## Instalação e Distribuição

### Canais de Instalação

| Canal               | Comando                                        | Target                     |
| ------------------- | ---------------------------------------------- | -------------------------- |
| **PyPI**            | `pip install vectora`                          | Qualquer OS                |
| **pipx**            | `pipx install vectora`                         | Isolated env (recomendado) |
| **uv**              | `uv tool install vectora`                      | Fast, isolated             |
| **Homebrew**        | `brew install vectora`                         | macOS, Linux               |
| **WinGet**          | `winget install Vectora.Vectora`               | Windows 10+                |
| **Scoop**           | `scoop install vectora`                        | Windows (dev-friendly)     |
| **Chocolatey**      | `choco install vectora`                        | Windows (enterprise)       |
| **Script**          | `curl -fsSL https://install.vectora.dev \| sh` | Linux/macOS one-liner      |
| **GitHub Releases** | Download `.whl`, `.exe`, `.deb`, `.dmg`        | Manual install             |

### Requisitos Mínimos

| Requisito   | Versão                        | Notas                                |
| ----------- | ----------------------------- | ------------------------------------ |
| **Python**  | 3.10+                         | Para backend, CLI, VCR               |
| **Node.js** | 20+ LTS                       | Para frontend dev (build time only)  |
| **RAM**     | 2GB                           | Mínimo; 4GB+ recomendado             |
| **Disco**   | 1GB                           | Para binários; +espaço para datasets |
| **SO**      | Windows 10+, macOS 11+, Linux | x86_64 e ARM64                       |

### Checksums e Verificação

```bash
# Após download, verificar integridade
sha256sum -c vectora-1.0.0-checksums.txt

# Verificar assinatura (opcional, com GPG)
gpg --verify vectora-1.0.0.tar.gz.asc vectora-1.0.0.tar.gz
```

---

## CLI Vectora

### Comandos Principais

```bash
# Inicializar novo projeto
vectora init [--path /custom/path]

# Iniciar/parar/reiniciar
vectora start
vectora stop
vectora restart
vectora status

# Gerenciar
vectora logs [--follow] [--tail 100]
vectora open                    # Abre UI no navegador
vectora doctor                  # Valida instalação
vectora config show
vectora config edit

# Banco de dados
vectora migrate                 # Executa migrações Alembic
vectora backup                  # Backup completo de dados
vectora restore /path/to/backup # Restaurar backup
vectora db reset                # DANGEROUS: limpa tudo

# Modelos
vectora model pull              # Baixa XLM-RoBERTa-small
vectora model info
vectora model remove

# Segurança
vectora token create [--name "API Key" --scopes "read,write"]
vectora token list
vectora token revoke <token_id>
vectora key create [--agent "claude-code"]

# Atualização
vectora update                  # Atualiza para versão mais recente
vectora version
vectora uninstall               # Remove, preserva ~/.vectora/

# Desenvolvimento
vectora dev                     # Hot reload backend + frontend
vectora build                   # Build production
```

### Exit Codes

```
0  - Sucesso
1  - Erro genérico
2  - Erro de configuração
3  - Banco de dados inacessível
4  - Porta em uso
126 - Permissão negada
```

---

## Runtime Local

### Diretório `~/.vectora/`

```
~/.vectora/
├── config.toml                 # Configuração principal
├── .env                        # Variáveis de ambiente
│
├── postgres/                   # PostgreSQL embedded
│   ├── data/                   # Database files (PGDATA)
│   ├── logs/
│   └── [postgres.pid](http://postgres.pid)
│
├── redis/                      # Redis embedded
│   ├── data/
│   ├── dump.rdb
│   └── [redis.pid](http://redis.pid)
│
├── lancedb/                    # Vector database
│   ├── datasets/
│   ├── [...]_data
│   └── [...]_lance
│
├── models/                     # ML models (cached)
│   ├── xlm-roberta-small/
│   │   ├── pytorch_model.bin
│   │   ├── tokenizer.json
│   │   └── config.json
│   └── lora/
│       └── lora_r8_a16_final/
│
├── uploads/                    # Arquivos temporários do usuário
│   ├── session_xyz/
│   └── [...]
│
├── backups/                    # Backups automáticos e manuais
│   ├── 2026-05-03_backup.tar.gz
│   └── [...]
│
├── logs/                       # Logs da aplicação
│   ├── vectora.log
│   ├── postgres.log
│   ├── redis.log
│   └── vcr.log
│
└── run/                        # PIDs e sockets
    ├── [vectora.pid](http://vectora.pid)
    ├── postgres.pid
    ├── redis.pid
    ├── postgres.sock
    └── redis.sock
```

### Inicialização Automática

**macOS/Linux (systemd):**

```bash
vectora service install
vectora service start
systemctl status vectora
journalctl -u vectora -f
```

**Windows (Service):**

```powershell
vectora service install
sc start vectora
Get-EventLog -LogName Application -Source Vectora -Newest 10
```

**Docker Compose (dev/VPS):**

```bash
docker-compose up -d
docker-compose logs -f
```

---

## API Backend

### Framework e Core

| Componente   | Versão | Propósito                                    |
| ------------ | ------ | -------------------------------------------- |
| **FastAPI**  | 0.104+ | Framework web assíncrono                     |
| **Uvicorn**  | 0.24+  | ASGI server (dev)                            |
| **Gunicorn** | 21+    | Process manager (prod/VPS com UvicornWorker) |
| **Python**   | 3.10+  | Runtime                                      |
| **Pydantic** | 2.5+   | Validação de dados                           |

### Endpoints

```
GET    /health              → Status básico
GET    /ready               → Ready probe (DB, Redis, etc)
GET    /metrics             → Prometheus metrics
GET    /swagger             → API docs (dev only)

POST   /api/v1/chat         → Query com RAG
GET    /api/v1/chat/:id     → Histórico da sessão
POST   /api/v1/search       → Vector search

POST   /api/v1/datasets     → Upload/ingestão
GET    /api/v1/datasets     → Listar datasets
GET    /api/v1/datasets/:id → Dataset details

POST   /api/v1/memory       → Store custom memory
GET    /api/v1/memory       → Retrieve memory
DELETE /api/v1/memory/:id   → Delete memory

POST   /api/v1/auth/login   → JWT token
POST   /api/v1/auth/refresh → Novo token
POST   /api/v1/auth/logout  → Invalidar token

GET    /api/v1/agents       → Agentes conectados
POST   /api/v1/agents/:id/key → Criar API key

GET    /api/v1/settings     → User settings
POST   /api/v1/settings     → Update settings

POST   /api/v1/backup       → Trigger backup
GET    /api/v1/backup/list  → List backups
POST   /api/v1/restore      → Restore backup
```

### Integração LangChain

| Componente              | Versão | Propósito         |
| ----------------------- | ------ | ----------------- |
| **langchain**           | 0.1+   | Orquestração LLM  |
| **langchain-anthropic** | 0.1+   | Integração Claude |
| **langchain-core**      | 0.1+   | Tipos base        |
| **langchain-community** | 0.1+   | Tools ecosystem   |

### Requirements

```txt
# Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pydantic==2.5.0
pydantic-settings==2.1.0

# LangChain
langchain==0.1.0
langchain-anthropic==0.1.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pg8000-embedded==2.0.0
alembic==1.12.1
lancedb==0.3.0

# Cache
redis==5.0.1
aioredis==2.0.1

# Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.1

# Observability
sentry-sdk[fastapi]==1.38.0
opentelemetry-api==1.20.0
opentelemetry-sdk==1.20.0
opentelemetry-instrumentation-fastapi==0.41b0
python-json-logger==2.0.7

# Rate limiting
slowapi==0.1.9

# Dev & Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
ruff==0.1.11
mypy==1.7.1
black==23.10.1
```

---

## Frontend Web

### Stack

| Componente         | Versão | Propósito                |
| ------------------ | ------ | ------------------------ |
| **React**          | 18+    | UI framework             |
| **Vite**           | 5+     | Build tool (dev + prod)  |
| **TypeScript**     | 5+     | Type safety              |
| **TailwindCSS**    | 3.3+   | Styling                  |
| **Zustand**        | 4.4+   | State management         |
| **TanStack Query** | 5+     | Data fetching            |
| **React Router**   | 6+     | SPA routing              |
| **shadcn/ui**      | Latest | UI components (opcional) |

### Arquitetura

```
src/
├── pages/               # Rotas principais
│   ├── Chat.tsx
│   ├── Datasets.tsx
│   ├── Memory.tsx
│   ├── Settings.tsx
│   └── Admin.tsx
│
├── components/          # Componentes reutilizáveis
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   ├── ChatWindow.tsx
│   └── [...]
│
├── hooks/
│   ├── useChat.ts
│   ├── useDatasets.ts
│   └── [...]
│
├── store/               # Zustand
│   ├── authStore.ts
│   ├── settingsStore.ts
│   └── [...]
│
├── api/                 # API client
│   └── client.ts
│
├── types/
│   └── index.ts
│
└── styles/
    └── globals.css
```

### WebSocket/SSE para Streaming

```typescript
// Streaming respostas LLM em real-time
const stream = await fetch("/api/v1/chat", {
  method: "POST",
  body: JSON.stringify({ query: "..." }),
});

const reader = stream.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = new TextDecoder().decode(value);
  updateUI(chunk); // Update chat window incrementally
}
```

### Build & Deployment

```bash
# Development
npm run dev          # http://localhost:5173

# Production build
npm run build        # → dist/

# Preview
npm run preview

# Integrated no backend (served by FastAPI)
# ./frontend/dist → /static/ (FastAPI static files)
```

---

## Vectora Cognitive Runtime

### Modelo e Fine-tuning

| Componente       | Versão | Propósito           |
| ---------------- | ------ | ------------------- |
| **PyTorch**      | 2.1+   | Deep learning       |
| **transformers** | 4.35+  | Hugging Face models |
| **peft**         | 0.7+   | LoRA fine-tuning    |

### Modelo Base

- **XLM-RoBERTa-small**: 24M params, 101 idiomas (incl. PT-BR)
- **LoRA Fine-tuning**: r=8, alpha=16 (~2M params adicionais)
- **Saída**: 4 classes (agent_mode, tool_mode, web_search, recovery)

### Training

```bash
# Baixar modelo base
python scripts/download_base.py

# Build dataset (sintético ou real)
python scripts/build_dataset.py --synthetic

# Treinar
python scripts/train.py \
  --model FacebookAI/xlm-roberta-small \
  --epochs 3 \
  --batch_size 32

# Avaliar
python scripts/eval.py --model models/checkpoints/lora_r8_a16_final/
```

### Inference (Phase 1: Subprocess)

```python
# Backend chama VCR via subprocess
import json
import subprocess

input_data = {
    "query": "What is AI?",
    "context": ["machine learning", "neural networks"]
}

result = subprocess.run(
    ["python", "vectora-cognitive-runtime/src/inference.py"],
    input=json.dumps(input_data),
    capture_output=True,
    text=True
)

decision = json.loads(result.stdout)
# {"action": "agent_mode", "confidence": 0.92}
```

---

## SDK de Integrações

### Monorepo (Turborepo + pnpm)

```
vectora-integrations/
├── packages/
│   ├── shared/              (@vectora/shared)
│   ├── claude-code/         (@vectora/sdk-claude-code)
│   ├── gemini-cli/          (@vectora/sdk-gemini-cli)
│   ├── paperclip/           (@vectora/sdk-paperclip)
│   ├── hermes/              (@vectora/sdk-hermes)
│   └── custom-template/     (Template)
│
└── apps/
    └── docs/                (Integration docs)
```

### Protocolos

| Agente          | Protocolo  | Library                   |
| --------------- | ---------- | ------------------------- |
| **Claude Code** | MCP        | @modelcontextprotocol/sdk |
| **Gemini CLI**  | REST       | @google/generative-ai     |
| **Paperclip**   | MCP + REST | @paperclipai/core         |
| **Hermes**      | REST       | Custom                    |
| **Custom**      | REST       | Template                  |

### Publishing

```bash
npm publish @vectora/sdk-claude-code
npm publish @vectora/sdk-gemini-cli
# Cada SDK é independente no npm
```

---

## Banco de Dados e Armazenamento

### PostgreSQL Embedded

| Aspecto     | Configuração                | Propósito                          |
| ----------- | --------------------------- | ---------------------------------- |
| **Versão**  | 15+                         | Produção relacional                |
| **Runtime** | `pg8000-embedded` (PyPI)    | Gerenciado pelo Vectora CLI        |
| **PGDATA**  | `~/.vectora/postgres/data/` | Dados persistidos                  |
| **Porta**   | 5433 (padrão)               | Evita conflitos com localhost:5432 |
| **Backup**  | `pg_dump` nightly           | Recuperação de dados               |

**Lifecycle (gerenciado pelo CLI):**

```bash
vectora start   # Inicia PostgreSQL, Redis, aplicação
vectora stop    # Para tudo gracefully
vectora migrate # Executa Alembic
vectora backup  # pg_dump automático
```

### Redis Embedded

| Aspecto         | Configuração                      | Propósito            |
| --------------- | --------------------------------- | -------------------- |
| **Versão**      | 7+                                | Cache + sessions     |
| **Port**        | 6379 (padrão ou 6380 se conflito) | In-memory store      |
| **Persistence** | AOF (`appendonly.aof`)            | Durabilidade         |
| **TTL**         | Configurável por chave            | Expiração automática |

### LanceDB

| Aspecto       | Configuração               | Propósito            |
| ------------- | -------------------------- | -------------------- |
| **Path**      | `~/.vectora/lancedb/`      | Vector store local   |
| **Modo**      | Embedded (Python nativo)   | Sem servidor externo |
| **Tabelas**   | `datasets` (1 por dataset) | Vetores + metadata   |
| **Indexação** | IVF (Inverted File)        | Busca rápida         |
| **Embedding** | OpenAI/Anthropic/local     | Dimensão variável    |

**Schema:**

```python
# LanceDB table per dataset
{
  "id": "vector_id",
  "dataset_id": "uuid",
  "chunk_id": "int",
  "content": "text",
  "embedding": [0.1, 0.2, ...],  # 1536 dims (OpenAI)
  "metadata": {
    "source": "file.pdf",
    "page": 1,
    "section": "Introduction"
  },
  "created_at": "timestamp"
}
```

### PostgreSQL Schema

```sql
-- Users & Auth
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Datasets
CREATE TABLE datasets (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    source VARCHAR(50),  -- 'file', 'url', 'api'
    vector_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    started_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(id),
    content TEXT NOT NULL,
    role VARCHAR(50),  -- 'user', 'assistant'
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Memory (custom embeddings/facts)
CREATE TABLE memory (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- pgvector
    created_at TIMESTAMP DEFAULT NOW()
);

-- API Keys (agentes)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    agent_name VARCHAR(255),  -- 'claude-code', 'gemini', etc
    key_hash VARCHAR(255),
    scopes TEXT,  -- 'read,write,admin'
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    revoked_at TIMESTAMP
);

-- Audit logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(255),  -- 'chat', 'upload', 'delete'
    resource VARCHAR(255),
    changes JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Backups metadata
CREATE TABLE backups (
    id UUID PRIMARY KEY,
    filename VARCHAR(255),
    size_bytes BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    restored_at TIMESTAMP
);
```

---

## Pipeline de Ingestão

### Fluxo

```
Upload/Import
    ↓
Parser (detect format)
    ├─ PDF → pypdf
    ├─ Markdown → markdown-it-py
    ├─ Web → beautifulsoup4
    ├─ JSON/CSV → pandas
    └─ Binário → unstructured
    ↓
Chunking (overlap, size)
    ↓
Embedding (OpenAI / Anthropic / local)
    ↓
LanceDB insert + PostgreSQL metadata
    ↓
Reindex (rebuil IVF)
    ↓
Ready for search
```

### Libraries

| Componente         | Versão | Propósito           |
| ------------------ | ------ | ------------------- |
| **unstructured**   | 0.10+  | Parsing genérico    |
| **pypdf**          | 3.17+  | PDFs                |
| **beautifulsoup4** | 4.12+  | Web scraping        |
| **markdown-it-py** | 3.0+   | Markdown parsing    |
| **python-magic**   | 0.4+   | File type detection |
| **chardet**        | 5.2+   | Encoding detection  |

### Implementação

```python
# src/ingestion/pipeline.py
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.basic import chunk_by_title
from lancedb import connect

class IngestionPipeline:
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        self.db = connect("~/.vectora/lancedb")
        self.table = self.db.open_table(f"dataset_{dataset_id}")

    async def ingest(self, file_path: str):
        # Parse
        elements = partition_pdf(file_path)

        # Chunk
        chunks = chunk_by_title(elements, max_characters=1000)

        # Embed
        embeddings = await self.embed([c.text for c in chunks])

        # Insert LanceDB
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            self.table.add({
                "chunk_id": i,
                "content": chunk.text,
                "embedding": embedding,
                "metadata": {
                    "source": file_path,
                    "type": chunk.type
                }
            })

        # Update count
        self.update_vector_count(len(chunks))
```

---

## Background Jobs

### Job Queue

| Tool            | Broker       | Propósito              |
| --------------- | ------------ | ---------------------- |
| **RQ**          | Redis        | Recomendado (simples)  |
| **Celery**      | Redis        | Alternativa (complexo) |
| **APScheduler** | Local memory | Tarefas recorrentes    |

### Jobs

```python
# src/jobs/__init__.py

@job
async def dataset_ingest(dataset_id: str, file_path: str):
    """Ingestão assíncrona de arquivo"""
    pipeline = IngestionPipeline(dataset_id)
    await pipeline.ingest(file_path)

@job
async def dataset_reindex(dataset_id: str):
    """Rebuild índices LanceDB"""
    db = connect("~/.vectora/lancedb")
    table = db.open_table(f"dataset_{dataset_id}")
    table.delete_search_index()
    table.create_search_index()

@job
async def backup_create():
    """Backup automático diário"""
    subprocess.run(["vectora", "backup"])

@job
async def memory_compact(user_id: int):
    """Cleanup memória antiga"""
    db = get_session()
    # Remove entradas antigas
    db.query(Memory).filter(
        Memory.user_id == user_id,
        Memory.created_at < datetime.now() - timedelta(days=90)
    ).delete()

@job
async def embedding_batch(chunk_ids: list[str]):
    """Batch embedding para chunks"""
    chunks = db.query(Vector).filter(Vector.id.in_(chunk_ids)).all()
    embeddings = await embed([c.content for c in chunks])
    for chunk, emb in zip(chunks, embeddings):
        chunk.embedding = emb
    db.commit()

@job
async def trace_collect():
    """Coleta traces do dia para Sentry/OpenTelemetry"""
    pass
```

### Scheduler

```python
# src/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

scheduler.add_job(
    backup_create,
    'cron',
    hour=2,  # 2 AM
    minute=0
)

scheduler.add_job(
    memory_compact,
    'interval',
    days=1
)

scheduler.start()
```

---

## Configuração Local

### Prioridade (primeiro ganha)

1. **CLI flags**: `vectora start --port 9000`
2. **Env vars**: `VECTORA_PORT=9000`
3. **config.toml**: `~/.vectora/config.toml`
4. **Defaults**: código-fonte

### config.toml

```toml
[vectora]
environment = "local"
debug = false
log_level = "INFO"

[server]
host = "127.0.0.1"
port = 8000
workers = 4

[database]
postgresql_port = 5433
postgresql_user = "vectora"
postgresql_password = "auto-generated"

[redis]
port = 6379
ttl_seconds = 3600

[lancedb]
path = "~/.vectora/lancedb"

[langchain]
llm_provider = "anthropic"
embedding_provider = "openai"  # ou "anthropic"
embedding_model = "text-embedding-3-small"

[security]
jwt_secret = "auto-generated-on-init"
api_key_rotation_days = 90

[backup]
enabled = true
schedule = "0 2 * * *"  # Daily 2 AM
retention_days = 30
```

### Configuração via CLI

```bash
vectora config edit              # Abre editor
vectora config get database.postgresql_port
vectora config set server.port 9000
```

### Libraries

| Componente            | Versão | Propósito                                                   |
| --------------------- | ------ | ----------------------------------------------------------- |
| **pydantic-settings** | 2.1+   | Config validation                                           |
| **tomli/tomli-w**     | 1.2+   | TOML parsing                                                |
| **platformdirs**      | 4.0+   | ~/.vectora path                                             |
| **keyring**           | 24.0+  | Secure secrets (macOS Keychain, Windows Credential Manager) |

---

## Segurança e Autenticação

### JWT + API Keys

**JWT (usuário web):**

- Token gerado em login
- TTL: 24 horas
- Refresh token: 7 dias
- Stored: localStorage (frontend)

**API Keys (agentes):**

- Gerada por usuário por agente
- TTL: customizável (padrão: sem expiração)
- Scopes: read, write, admin
- Rotation: manual ou automático

### RBAC (5 papéis)

```python
ROLES = {
    "admin": ["user:*", "dataset:*", "agent:*", "settings:*", "logs:view"],
    "researcher": ["dataset:read", "dataset:create", "agent:read"],
    "developer": ["agent:*", "dataset:read"],
    "user": ["profile:read", "profile:write", "dataset:read"],
    "guest": ["public:read"]
}

AGENT_SCOPES = {
    "claude-code:read": "Read-only access",
    "claude-code:write": "Chat + memory write",
    "memory:read": "Query custom memory",
    "memory:write": "Store custom memory",
    "datasets:read": "List + search",
    "datasets:write": "Upload + delete",
    "admin:*": "Full access (no restrictions)"
}
```

### Middleware de Segurança

```python
# FastAPI middlewares
app.add_middleware(CORSMiddleware, allow_origins=[...])
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
app.add_middleware(SecurityHeadersMiddleware)  # HSTS, CSP, etc
app.add_middleware(RequestLoggingMiddleware)  # Audit logs
```

### Secrets Management

```python
# src/security/secrets.py
from keyring import get_password, set_password

# Armazenar sensíveis em OS keyring (macOS Keychain, Windows Credential Manager)
set_password("vectora", "anthropic_api_key", "sk-...")
api_key = get_password("vectora", "anthropic_api_key")

# Ou via .env (git-ignored)
JWT_SECRET = os.getenv("JWT_SECRET", generate_secret())
```

---

## Observabilidade Local-First

### Default (Built-in)

```
Logs em arquivo: ~/.vectora/logs/vectora.log
Health endpoint: GET /health → {"status": "healthy"}
Ready endpoint: GET /ready → {postgres: ok, redis: ok, lancedb: ok}
Metrics endpoint: GET /metrics → Prometheus format
```

### Advanced (Opcional)

**Prometheus + Grafana local:**

```bash
docker-compose -f docker-compose.dev.yml up -d prometheus grafana
# Acessa http://localhost:3000 (admin/admin)
```

**Sentry (opcional, cloud ou self-hosted):**

```python
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", None),  # Se vazio, desativado
    environment="local",
    traces_sample_rate=0.1 if not DEBUG else 1.0
)
```

**OpenTelemetry (exportar traces):**

```python
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
# Exportar apenas se Jaeger está rodando
# Caso contrário, logs locais são suficientes
```

**LangSmith (LLM tracing):**

```python
# Opcional: tracear todas as chamadas LangChain
os.environ["LANGSMITH_API_KEY"] = "..."  # Se vazio, desativado
```

---

## DevOps e Deployment

### Local Development

```bash
# Terminal 1: Backend
uv venv
source .venv/bin/activate  # ou .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: VCR (if training)
python vectora-cognitive-runtime/src/server.py

# Acessa:
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# API docs: http://localhost:8000/docs
```

### Docker (Dev + VPS)

**docker-compose.dev.yml** (development):

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: local
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    command: uvicorn src.main:app --reload --host 0.0.0.0
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:local@postgres:5432/vectora
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - .:/app

  frontend:
    build: ./frontend
    command: npm run dev
    ports:
      - "5173:5173"
```

**Dockerfile** (produção):

```dockerfile
# Multi-stage: build + runtime
FROM python:3.11-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY src ./src
COPY frontend/dist ./static
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "src.main:app"]
```

### VPS Deployment

**systemd service:**

```ini
# /etc/systemd/system/vectora.service
[Unit]
Description=Vectora Runtime
After=network.target

[Service]
Type=simple
User=vectora
WorkingDirectory=/home/vectora/vectora
ExecStart=/usr/local/bin/vectora start
ExecStop=/usr/local/bin/vectora stop
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Caddyfile (reverse proxy):**

```
api.example.com {
    encode gzip
    reverse_proxy localhost:8000

    # Logs
    log {
        level info
        output file /var/log/caddy/vectora.log
    }
}
```

**.env production:**

```
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARN
JWT_SECRET=<auto-generated>
ANTHROPIC_API_KEY=<user-provided>
DATABASE_URL=postgresql://vectora:password@localhost:5433/vectora
REDIS_URL=redis://localhost:6379
```

**Deploy workflow:**

```bash
# 1. SSH into VPS
ssh user@vps.example.com

# 2. Update Vectora
vectora update

# 3. Backup before restart
vectora backup

# 4. Restart
vectora service restart

# 5. Verify
vectora status
curl http://localhost:8000/health
```

### CI/CD

**GitHub Actions (test + build + release):**

```yaml
name: Tests & Build

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest --cov=src
      - run: ruff check .
      - run: mypy src/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v2
      - uses: docker/login-action@v2
        with:
          registry: ghcr.io
      - uses: docker/build-push-action@v4
        with:
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ghcr.io/vectora/vectora:latest
```

**Jenkins (VPS deployment):**

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t vectora:${BUILD_NUMBER} .'
            }
        }
        stage('Test') {
            steps {
                sh 'docker run vectora:${BUILD_NUMBER} pytest'
            }
        }
        stage('Deploy') {
            when { branch 'main' }
            steps {
                sh '''
                    docker tag vectora:${BUILD_NUMBER} vectora:latest
                    docker push registry.example.com/vectora:latest
                    ssh vectora@vps.example.com "vectora update && vectora restart"
                '''
            }
        }
    }
}
```

### Security Scanning

| Tool         | Propósito                |
| ------------ | ------------------------ |
| **Trivy**    | Container image scanning |
| **Bandit**   | Python security linting  |
| **Gitleaks** | Secret detection         |
| **Semgrep**  | SAST (opcional)          |

---

## Website e Documentação

### Stack

| Componente       | Versão | Propósito             |
| ---------------- | ------ | --------------------- |
| **Hugo**         | 0.120+ | Static site generator |
| **Hextra Theme** | Latest | Modern theme          |

### Estrutura

```
vectora-website/
├── content/
│   ├── en/
│   │   ├── docs/
│   │   │   ├── getting-started/
│   │   │   ├── architecture/
│   │   │   ├── api-reference/
│   │   │   ├── cli/
│   │   │   └── [...]
│   │   └── blog/
│   └── pt-br/
│       └── [mirrors en/]
│
└── static/
    ├── images/
    └── downloads/
        ├── vectora-1.0.0-py3-none-any.whl
        ├── vectora-1.0.0-x86_64-linux
        ├── vectora-1.0.0.dmg
        └── vectora-1.0.0.exe
```

---

## Testes e Qualidade

### Testing

| Framework          | Versão | Propósito   |
| ------------------ | ------ | ----------- |
| **pytest**         | 7.4+   | Unit tests  |
| **pytest-asyncio** | 0.21+  | Async tests |
| **pytest-cov**     | 4.1+   | Coverage    |

### Linting & Type Checking

| Tool       | Versão | Propósito        |
| ---------- | ------ | ---------------- |
| **ruff**   | 0.1+   | Fast linter      |
| **mypy**   | 1.7+   | Type checking    |
| **black**  | 23.10+ | Formatter        |
| **bandit** | 1.7+   | Security linting |

### Coverage Requirement

```bash
pytest --cov=src --cov-fail-under=80
# Minimum 80% code coverage
```

---

## Release Engineering

### Versioning

- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **File**: `.version` in root
- **Git Tags**: `v1.0.0`

### Build Matrix

| Target                   | Runtime       | Format                     |
| ------------------------ | ------------- | -------------------------- |
| **Linux x86_64**         | CPython 3.10+ | `.whl`, `.tar.gz`, `.deb`  |
| **macOS x86_64 + ARM64** | CPython 3.10+ | `.whl`, `.dmg`             |
| **Windows x86_64**       | CPython 3.10+ | `.whl`, `.exe` (installer) |

### Release Process

```bash
# 1. Tag release
git tag -a v1.0.0 -m "Release 1.0.0"

# 2. GitHub Actions builds all artifacts (matrix)
# Outputs: wheel, exe, dmg, deb, checksums, SBOM

# 3. Create GitHub Release
gh release create v1.0.0 --generate-notes

# 4. Upload artifacts
gh release upload v1.0.0 dist/*

# 5. Publish to PyPI
twine upload dist/*.whl

# 6. Update Homebrew tap
# (auto via GitHub Actions)
```

### Artifacts & Checksums

```
vectora-1.0.0-py3-none-any.whl
vectora-1.0.0-py3-none-any.whl.sha256
vectora-1.0.0.tar.gz
vectora-1.0.0.tar.gz.sha256
vectora-1.0.0-x86_64-linux
vectora-1.0.0-x86_64-linux.sha256
vectora-1.0.0.dmg
vectora-1.0.0.dmg.sha256
vectora-1.0.0.exe
vectora-1.0.0.exe.sha256
vectora-1.0.0-SBOM.spdx.json
```

### SBOM & Assinatura

```bash
# SBOM (Software Bill of Materials)
pip install syft
syft packages > vectora-1.0.0-SBOM.spdx.json

# Assinatura (opcional, com GPG)
gpg --detach-sign --armor vectora-1.0.0.tar.gz
# Outputs: vectora-1.0.0.tar.gz.asc
```

---

## Referência Rápida: Stack Resumida

| Layer                     | Tecnologia               | Versão | Propósito                                           |
| ------------------------- | ------------------------ | ------ | --------------------------------------------------- |
| **Protocolo: REST API**   | FastAPI                  | 0.104+ | Web UI, CLI, HTTP integrations                      |
| **Protocolo: MCP Server** | Python MCP SDK           | Latest | Agent integrations (Claude Code, Gemini, Paperclip) |
| **Protocolo: JSON-RPC**   | JSON-RPC 2.0             | 2.0    | Internal process communication, CLI local           |
| **Protocolo: Streaming**  | SSE / WebSocket          | Native | Chat streaming, job progress                        |
| **Linguagem Backend**     | Python                   | 3.10+  | Core logic                                          |
| **Framework Web**         | FastAPI                  | 0.104+ | REST API server                                     |
| **Linguagem Frontend**    | TypeScript               | 5+     | UI logic                                            |
| **Framework UI**          | React                    | 18+    | Components                                          |
| **Build Tool**            | Vite                     | 5+     | Fast dev + prod build                               |
| **Gerenciador Estado**    | Zustand                  | 4.4+   | Client state                                        |
| **HTTP Client**           | TanStack Query           | 5+     | Data fetching                                       |
| **ORM**                   | SQLAlchemy               | 2.0+   | Database abstraction                                |
| **Database**              | PostgreSQL               | 15+    | Relational data                                     |
| **Embedded DB**           | pg8000-embedded          | 2.0+   | Local PostgreSQL                                    |
| **Cache**                 | Redis                    | 7+     | Sessions + cache                                    |
| **Vector DB**             | LanceDB                  | 0.3+   | Semantic search                                     |
| **ML Framework**          | PyTorch                  | 2.1+   | Neural networks                                     |
| **Transformers**          | HuggingFace              | 4.35+  | Pre-trained models                                  |
| **Fine-tuning**           | LoRA (PEFT)              | 0.7+   | Efficient training                                  |
| **LLM Orchestration**     | LangChain                | 0.1+   | RAG pipeline                                        |
| **LLM Provider**          | Anthropic (Claude)       | Latest | Main LLM                                            |
| **Embedding Provider**    | OpenAI / Anthropic       | Latest | Embeddings                                          |
| **Job Queue**             | RQ                       | 1.15+  | Background jobs                                     |
| **Scheduler**             | APScheduler              | 3.10+  | Cron jobs                                           |
| **Error Tracking**        | Sentry                   | Latest | Optional                                            |
| **Observability**         | OpenTelemetry            | 1.20+  | Tracing standard                                    |
| **Container**             | Docker                   | 24+    | Dev + VPS                                           |
| **Reverse Proxy**         | Caddy                    | 2.7+   | VPS reverse proxy                                   |
| **Service Manager**       | systemd                  | Native | VPS lifecycle                                       |
| **Testing**               | pytest                   | 7.4+   | Unit tests                                          |
| **Linting**               | ruff                     | 0.1+   | Fast lint                                           |
| **Type Checking**         | mypy                     | 1.7+   | Static types                                        |
| **CLI Framework**         | Click/Typer              | Latest | Command interface                                   |
| **Documentation**         | Hugo + Hextra            | Latest | Static docs site                                    |
| **Version Control**       | Git                      | Latest | Source control                                      |
| **CI/CD**                 | GitHub Actions + Jenkins | Latest | Build + deploy automation                           |

---

**Status**: Stack document completo (local-first, instalável, não SaaS)  
**Última Atualização**: 2026-05-03  
**Proprietário**: Vectora Engineering Team  
**Licença**: Apache 2.0
