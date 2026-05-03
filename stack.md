# Documentação da Stack do Vectora

**Vectora é um single binary instalável (aplicação única), controlado por CLI, com interface web integrada.** Não é SaaS, não é cloud-native, não é modular separado. É um produto que o usuário instala (`vectora` ou `vectora.exe`) em sua máquina ou VPS e roda 24/7, como Paperclip.

Stack de tecnologia completa: tudo integrado em um único aplicativo, com todos componentes internos (CLI, Backend, Frontend, Databases) rodando juntos.

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Protocolos de Comunicação](#protocolos-de-comunicação)
3. [Vectora App](#vectora-app)
   - [CLI](#cli)
   - [Backend API](#backend-api)
   - [Frontend Web](#frontend-web)
   - [Runtime Local](#runtime-local)
   - [PostgreSQL Embedded](#postgresql-embedded)
   - [Redis Embedded](#redis-embedded)
   - [LanceDB](#lancedb)
   - [Pipeline de Ingestão](#pipeline-de-ingestão)
   - [Background Jobs](#background-jobs)
   - [Configuração Local](#configuração-local)
   - [Segurança e Autenticação](#segurança-e-autenticação)
   - [Observabilidade Local-First](#observabilidade-local-first)
   - [DevOps e Deployment](#devops-e-deployment)
4. [Vectora Cognitive Runtime](#vectora-cognitive-runtime)
5. [SDK de Integrações](#sdk-de-integrações)
6. [Website e Documentação](#website-e-documentação)
7. [Testes e Qualidade](#testes-e-qualidade)
8. [Release Engineering](#release-engineering)

---

## Visão Geral

**Vectora** é um aplicativo local-first que roda em máquinas individuais ou VPS. É **um único binário executável** que incorpora:

- CLI (Python Click/Typer) → entry point principal
- Backend (FastAPI) → daemon HTTP, inicia via CLI
- Frontend (React/Vite built) → served via backend
- Databases (PostgreSQL, Redis, LanceDB embedded) → gerenciados via CLI
- VCR (Vectora Cognitive Runtime) → spawned como subprocess quando necessário

### Arquitetura: Single Binary

```
┌─────────────────────────────────────────────────────────┐
│  VECTORA APP (Single Binary: vectora / vectora.exe)     │
│                                                         │
│  $ vectora start                                        │
│  $ vectora stop                                         │
│  $ vectora status                                       │
│  $ vectora backup                                       │
│  $ vectora logs                                         │
│  $ vectora open  (abre navegador em localhost:8000)    │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  CLI (Python) — Interface Principal              │ │
│  │  ├─ Controla daemon                              │ │
│  │  ├─ Gerencia databases (start/stop)              │ │
│  │  ├─ Executa migrações                            │ │
│  │  └─ Backup/restore                               │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Backend Daemon (FastAPI)                         │ │
│  │  ├─ HTTP REST API (localhost:8000)                │ │
│  │  ├─ MCP Server (stdio para agentes)               │ │
│  │  ├─ LangChain RAG pipeline                        │ │
│  │  ├─ Job queue (RQ + Redis)                        │ │
│  │  └─ Ingestão, search, memory, etc                 │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Frontend Web (React + Vite built)                │ │
│  │  ├─ Served em /static pelo backend                │ │
│  │  ├─ Acessa backend via localhost:8000             │ │
│  │  └─ Chat, datasets, memory, settings              │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────┬──────────────┬──────────────────────┐ │
│  │ PostgreSQL  │    Redis     │     LanceDB         │ │
│  │ Embedded    │  Embedded    │  (Vector DB)        │ │
│  │ pg8000      │  Native      │  Embedded           │ │
│  └─────────────┴──────────────┴──────────────────────┘ │
│         ~/.vectora/                                     │
│  ├─ config.toml                                        │
│  ├─ postgres/ (data dir)                               │
│  ├─ redis/ (data dir)                                  │
│  ├─ lancedb/ (vector store)                            │
│  ├─ models/ (LoRA weights)                             │
│  ├─ backups/ (diários)                                 │
│  └─ logs/                                              │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  VCR Subprocess (Python)                          │ │
│  │  ├─ Spawned pelo backend quando needed            │ │
│  │  ├─ XLM-RoBERTa-small + LoRA                      │ │
│  │  └─ JSON-RPC communication                        │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  MCP Server (Built-in)                            │ │
│  │  ├─ Expõe ferramentas para agentes externos       │ │
│  │  ├─ Claude Code, Gemini, Paperclip, etc           │ │
│  │  └─ Transport: stdio ou HTTP                      │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
         │
         └─ External Agentes (via MCP)
            └─ Custom HTTP integrations (via REST)
```

---

## Protocolos de Comunicação

Vectora expõe múltiplas interfaces para Web UI, CLI, agentes externos. Os protocolos são camadas centrais, não detalhes secundários.

### REST API

REST é a interface HTTP para Web UI, CLI local e integrações HTTP.

| Aspecto       | Detalhes         |
| ------------- | ---------------- |
| **Protocol**  | HTTP REST        |
| **Payload**   | JSON             |
| **Streaming** | SSE / WebSocket  |
| **Auth**      | JWT Bearer Token |

**Endpoints (40+ total):**

```
GET    /health
GET    /ready
GET    /metrics
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
POST   /api/v1/chat
GET    /api/v1/chat/:id
POST   /api/v1/search
POST   /api/v1/memory
GET    /api/v1/memory
POST   /api/v1/datasets
GET    /api/v1/datasets
POST   /api/v1/datasets/:id/ingest
GET    /api/v1/jobs/:id
POST   /api/v1/backup
GET    /api/v1/backup/list
POST   /api/v1/restore
... (mais)
```

### MCP Server

Vectora expõe **Model Context Protocol** para agentes (Claude Code, Gemini, Paperclip).

| Aspecto       | Detalhes                         |
| ------------- | -------------------------------- |
| **Protocol**  | MCP (Model Context Protocol)     |
| **Format**    | JSON-RPC 2.0                     |
| **Transport** | stdio (local), HTTP/SSE (remoto) |

**Ferramentas MCP:**

```
vectora.search_context
vectora.rerank
vectora.store_memory
vectora.query_memory
vectora.ingest_dataset
vectora.get_dataset
vectora.web_search
vectora.execute_tool
```

### JSON-RPC 2.0

JSON-RPC para comunicação leve entre processos internos e CLI.

| Aspecto       | Detalhes                 |
| ------------- | ------------------------ |
| **Protocol**  | JSON-RPC 2.0             |
| **Transport** | HTTP, Unix socket, stdio |

**Métodos:**

```
vectora.runtime.status
vectora.runtime.start
vectora.runtime.stop
vectora.vcr.decide
vectora.storage.health
vectora.jobs.status
```

### Streaming: SSE & WebSocket

Para chat em tempo real e progresso de jobs.

```
SSE: POST /api/v1/chat?stream=true
WebSocket: ws://localhost:8000/api/v1/chat/stream
```

---

## Vectora App

**Vectora é uma aplicação única.** Tudo abaixo é parte integrada do mesmo binário executável.

---

### CLI

Interface de linha de comando (entry point principal).

**Linguagem:** Python 3.10+ com Click/Typer

**Comandos Principais:**

```bash
# Ciclo de vida
vectora init                # Inicializa ~/.vectora/
vectora start               # Inicia todos os serviços
vectora stop                # Para todos os serviços
vectora restart             # Restart
vectora status              # Status de cada componente

# Gerenciamento
vectora logs [--follow]     # Tail de logs
vectora open                # Abre UI no navegador
vectora doctor              # Valida instalação

# Dados
vectora migrate             # Alembic migrations
vectora backup              # Backup completo
vectora restore PATH        # Restaurar backup

# Modelos
vectora model pull          # Download XLM-RoBERTa-small
vectora model info
vectora model remove

# Chaves & Segurança
vectora token create
vectora token list
vectora key create --agent claude-code

# Atualização
vectora update
vectora uninstall
vectora version
```

**Lifecycle:**

```python
# ~vectora/bin/vectora (ou vectora.exe)
import click
from vectora.cli import app

if __name__ == "__main__":
    app()  # entry point
```

---

### Backend API

**Framework:** FastAPI 0.104+  
**Server:** Uvicorn (dev), Gunicorn + UvicornWorker (prod/VPS)  
**Porta:** 8000 (padrão)

**Componentes:**

1. **HTTP Router** - Endpoints REST (40+)
2. **Middleware Stack** - CORS, Auth, Rate Limit, Logging, Sentry
3. **LangChain Integration** - RAG pipeline com Claude (Anthropic API)
4. **MCP Server** - Model Context Protocol (built-in)
5. **Job Queue** - RQ com Redis backend
6. **Database ORM** - SQLAlchemy + PostgreSQL

**Requirements:**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pg8000-embedded==2.0.0
lancedb==0.3.0
redis==5.0.1
langchain==0.1.0
langchain-anthropic==0.1.0
sentry-sdk[fastapi]==1.38.0
slowapi==0.1.9
```

**Startup:**

```bash
# Via CLI
$ vectora start
# Inicia: PostgreSQL → Redis → FastAPI daemon

# Backend inicia em background
$ curl http://localhost:8000/health
{"status": "healthy"}
```

---

### Frontend Web

**Framework:** React 18+  
**Build Tool:** Vite 5+  
**Styling:** TailwindCSS 3.3+  
**State:** Zustand 4.4+  
**Data Fetching:** TanStack Query 5+  
**Language:** TypeScript 5+

**Build:**

```bash
cd frontend
npm run build  # → dist/
```

**Serving:**

```python
# Backend serves frontend como static files
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

**Acesso:**

```
http://localhost:8000/
```

---

### Runtime Local

**Directory:** `~/.vectora/`

```
~/.vectora/
├── config.toml              # Configuração principal
├── postgres/                # PostgreSQL embedded
│   ├── data/                # PGDATA
│   ├── logs/
│   └── postgres.pid
├── redis/                   # Redis embedded
│   ├── data/
│   └── redis.pid
├── lancedb/                 # Vector database
│   └── datasets/
├── models/                  # ML weights
│   ├── xlm-roberta-small/
│   └── lora/lora_r8_a16_final/
├── backups/                 # Backups automáticos
├── logs/                    # Application logs
│   ├── vectora.log
│   ├── postgres.log
│   └── redis.log
└── run/                     # PIDs e sockets
    ├── vectora.pid
    ├── postgres.pid
    ├── redis.pid
    ├── postgres.sock
    └── redis.sock
```

---

### PostgreSQL Embedded

**Library:** `pg8000-embedded` (PyPI)  
**Version:** 15+  
**Port:** 5433 (padrão, evita conflito com localhost:5432)  
**Data Dir:** `~/.vectora/postgres/data`

**Lifecycle (gerenciado por CLI):**

```bash
vectora start    # Inicia PostgreSQL
vectora stop     # Para PostgreSQL
vectora migrate  # Executa Alembic
vectora backup   # pg_dump
```

**Connection:**

```python
DATABASE_URL = "postgresql://vectora:auto-pass@localhost:5433/vectora"
```

---

### Redis Embedded

**Version:** 7+  
**Port:** 6379 (padrão)  
**Data Dir:** `~/.vectora/redis/`  
**Persistence:** AOF (appendonly.aof)

**Uso:**

```python
# Session store
# Job queue (RQ)
# Cache
# Memory TTL
```

---

### LanceDB

**Version:** 0.3+  
**Path:** `~/.vectora/lancedb/`  
**Mode:** Embedded (Python nativo)

**Schema:**

```python
{
  "id": "chunk_id",
  "dataset_id": "uuid",
  "content": "text",
  "embedding": [0.1, 0.2, ...],  # 1536 dims
  "metadata": {
    "source": "file.pdf",
    "page": 1
  },
  "created_at": "timestamp"
}
```

---

### Pipeline de Ingestão

**Fluxo:**

```
Upload → Parser → Chunking → Embedding → LanceDB + PostgreSQL
```

**Libraries:**

```txt
unstructured==0.10+
pypdf==3.17+
beautifulsoup4==4.12+
markdown-it-py==3.0+
python-magic==0.4+
chardet==5.2+
```

**Processamento:**

```python
# src/ingestion/pipeline.py
@job
async def ingest_dataset(dataset_id, file_path):
    # Parse file → elements
    # Chunk by title/size
    # Embed with OpenAI/Anthropic/local
    # Insert LanceDB
    # Update metadata PostgreSQL
```

---

### Background Jobs

**Queue:** RQ (Redis Queue)  
**Scheduler:** APScheduler

**Jobs:**

```python
@job
async def dataset_ingest(dataset_id, file_path)

@job
async def dataset_reindex(dataset_id)

@job
async def backup_create()

@job
async def embedding_batch(chunk_ids)
```

**Schedule:**

```python
scheduler.add_job(backup_create, 'cron', hour=2, minute=0)  # Daily 2am
```

---

### Configuração Local

**Prioridade:**

1. CLI flags: `vectora start --port 9000`
2. Env vars: `VECTORA_PORT=9000`
3. config.toml: `~/.vectora/config.toml`
4. Defaults: código

**config.toml:**

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

[redis]
port = 6379
ttl_seconds = 3600

[langchain]
llm_provider = "anthropic"
embedding_provider = "openai"

[security]
jwt_secret = "auto-generated-on-init"
```

**Libraries:**

```txt
pydantic-settings==2.1+
tomli/tomli-w==1.2+
platformdirs==4.0+
keyring==24.0+
```

---

### Segurança e Autenticação

**JWT (Users):**

- Token: 24h TTL
- Refresh: 7d TTL
- Storage: localStorage (frontend)

**API Keys (Agents):**

- Por agente
- Scopes: read, write, admin
- Rotation: customizável

**RBAC (5 roles):**

```
admin → All permissions
researcher → dataset:read, agent:read
developer → agent:*, dataset:read
user → profile:*, dataset:read
guest → public:read
```

**Middleware:**

```python
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(RateLimitMiddleware, ...)
app.add_middleware(SecurityHeadersMiddleware, ...)
```

---

### Observabilidade Local-First

**Default (Built-in):**

```
Logs: ~/.vectora/logs/vectora.log
Health: GET /health
Ready: GET /ready
Metrics: GET /metrics (Prometheus format)
```

**Advanced (Optional):**

```
Sentry: Error tracking (cloud ou self-hosted)
OpenTelemetry: Traces (opcional)
Prometheus: Metrics (local docker-compose)
```

---

### DevOps e Deployment

**Local Development:**

```bash
vectora start  # All-in-one
```

**Docker (Dev/VPS):**

```bash
docker-compose -f docker-compose.dev.yml up -d
```

**VPS Deployment:**

```bash
# systemd service
vectora service install
vectora service start

# Caddy reverse proxy
# .env production
# cron backup
```

**Arquivos:**

```
Dockerfile (multi-stage)
docker-compose.dev.yml (dev)
docker-compose.prod.yml (VPS)
~/.vectora/systemd/vectora.service
/etc/caddy/Caddyfile
```

---

## Vectora Cognitive Runtime

**Componente externo** (pode rodar como subprocess ou separado).

**Papel:** Decidir qual estratégia usar (agent_mode, tool_mode, web_search, recovery).

**Stack:**

```txt
PyTorch==2.1+
transformers==4.35+
peft==0.7+
```

**Modelo:** XLM-RoBERTa-small (24M params) + LoRA (r=8, alpha=16)

**Deployment:**

- Phase 1: Subprocess (backend chama via stdin/stdout)
- Phase 4+: gRPC server separado (opcional)

---

## SDK de Integrações

**Consumidores** de Vectora (não parte do app, mas integram-se a ele).

**Repositório:** `vectora-integrations/` (Turborepo)

**Packages:**

```
@vectora/shared
@vectora/sdk-claude-code (MCP)
@vectora/sdk-gemini-cli (REST + MCP adapter)
@vectora/sdk-paperclip (MCP + REST)
@vectora/sdk-hermes (REST)
```

**Protocolos:**

- Claude Code: MCP nativo
- Gemini: REST ou MCP adapter
- Paperclip: MCP ou REST
- Custom: REST ou MCP

---

## Website e Documentação

**Generator:** Hugo 0.120+  
**Theme:** Hextra (modern, open-source)  
**Languages:** EN, PT-BR  
**Deployment:** GitHub Pages / Netlify / Fly.io

---

## Testes e Qualidade

**Testing:** pytest 7.4+  
**Type Checking:** mypy 1.7+  
**Linting:** ruff 0.1+  
**Formatting:** black 23.10+  
**Security:** bandit 1.7+

**Coverage:** Minimum 80%

---

## Release Engineering

**Versioning:** Semantic (MAJOR.MINOR.PATCH)

**Channels:**

```
PyPI (pip install vectora)
Homebrew (brew install vectora)
WinGet (winget install Vectora)
Scoop (scoop install vectora)
Chocolatey (choco install vectora)
GitHub Releases (download .exe, .dmg, .deb)
curl script (curl -fsSL https://install.vectora.dev | sh)
```

**Build Matrix:**

```
Linux x86_64 → .whl, .tar.gz, .deb
macOS x86_64 + ARM64 → .whl, .dmg
Windows x86_64 → .whl, .exe (installer)
```

**Artifacts:**

```
Checksums (SHA256)
SBOM (SPDX)
Signatures (GPG optional)
```

---

## Referência Rápida: Stack Resumida

| Layer                    | Tecnologia         | Versão   | Propósito                   |
| ------------------------ | ------------------ | -------- | --------------------------- |
| **Protocolo: REST**      | FastAPI            | 0.104+   | HTTP API                    |
| **Protocolo: MCP**       | Python MCP SDK     | Latest   | Agent integration           |
| **Protocolo: JSON-RPC**  | JSON-RPC 2.0       | 2.0      | Internal IPC                |
| **Protocolo: Streaming** | SSE / WebSocket    | Native   | Real-time chat              |
| **App: CLI**             | Click/Typer        | Latest   | Entry point, daemon control |
| **App: Backend**         | FastAPI            | 0.104+   | HTTP server, RAG pipeline   |
| **App: Frontend**        | React + Vite       | 18+ / 5+ | Web UI                      |
| **App: Database**        | PostgreSQL         | 15+      | Relational data             |
| **App: DB Embedded**     | pg8000-embedded    | 2.0+     | Managed by CLI              |
| **App: Cache**           | Redis              | 7+       | Sessions, jobs              |
| **App: Vector DB**       | LanceDB            | 0.3+     | Semantic search             |
| **ML: Framework**        | PyTorch            | 2.1+     | Neural networks             |
| **ML: Transformers**     | HuggingFace        | 4.35+    | Pre-trained models          |
| **ML: Fine-tuning**      | LoRA (PEFT)        | 0.7+     | Efficient training          |
| **LLM: Orchestration**   | LangChain          | 0.1+     | RAG pipeline                |
| **LLM: Provider**        | Anthropic (Claude) | Latest   | Main LLM                    |
| **Embedding: Provider**  | OpenAI / Anthropic | Latest   | Embeddings                  |
| **Jobs: Queue**          | RQ                 | 1.15+    | Background jobs             |
| **Jobs: Scheduler**      | APScheduler        | 3.10+    | Cron tasks                  |
| **Error Tracking**       | Sentry             | Latest   | Optional                    |
| **Observability**        | OpenTelemetry      | 1.20+    | Tracing                     |
| **Container**            | Docker             | 24+      | Dev + VPS                   |
| **Reverse Proxy**        | Caddy              | 2.7+     | VPS proxy                   |
| **Service Manager**      | systemd            | Native   | VPS lifecycle               |
| **Testing**              | pytest             | 7.4+     | Unit tests                  |
| **Linting**              | ruff               | 0.1+     | Code quality                |
| **Type Checking**        | mypy               | 1.7+     | Static types                |
| **Documentation**        | Hugo + Hextra      | Latest   | Static docs                 |

---

**Status:** Documentação completa de Vectora App (single binary, local-first, instalável)  
**Última Atualização:** 2026-05-03  
**Proprietário:** Vectora Engineering Team  
**Licença:** Apache 2.0
