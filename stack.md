# Documentação da Stack do Vectora

Stack de tecnologia completa para o Vectora: todos os aplicativos internos, serviços externos, infraestrutura de DevOps e opções de implantação.

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [API Backend](#api-backend)
4. [Vectora Cognitive Runtime](#vectora-cognitive-runtime)
5. [SDK de Integrações](#sdk-de-integrações)
6. [Site e Documentação](#site-e-documentação)
7. [Banco de Dados e Armazenamento](#banco-de-dados-e-armazenamento)
8. [Stack de Observabilidade](#stack-de-observabilidade)
9. [DevOps e Infraestrutura](#devops-e-infraestrutura)
10. [Segurança e Autenticação](#segurança-e-autenticação)
11. [Testes e Qualidade](#testes-e-qualidade)
12. [Ferramentas e Utilitários](#ferramentas-e-utilitários)
13. [Alvos de Implantação](#alvos-de-implantação)

---

## Visão Geral

O Vectora é um sistema impulsionado por IA de múltiplos componentes com:

- **API Backend**: Microsserviço em Python FastAPI com integração LangChain
- **Componente ML**: VCR (Vectora Cognitive Runtime) para classificação de decisões
- **Integrações**: SDKs para Claude Code, Gemini, Paperclip e agentes customizados
- **Documentação**: Site estático Hugo com o tema Hextra
- **Infraestrutura**: Docker, Kubernetes, pipeline CI/CD completo
- **Observabilidade**: LangSmith, Prometheus, Jaeger, Grafana, Sentry
- **Bancos de Dados**: PostgreSQL, Redis, LanceDB

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    External Agents                              │
│  (Claude Code, Gemini CLI, Paperclip, Custom, Hermes)          │
└──────────────────┬──────────────────────────────────────────────┘
                   │ HTTP REST + MCP Protocol
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Vectora Backend API (Python/FastAPI)               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ HTTP Router (Chi-like with FastAPI)                      │   │
│  │ ├─ /api/v1/chat (POST)          → LLM pipeline          │   │
│  │ ├─ /api/v1/memory (GET/POST)    → Memory store          │   │
│  │ ├─ /api/v1/search (POST)        → Vector search         │   │
│  │ ├─ /api/v1/datasets (GET/POST)  → Dataset management    │   │
│  │ ├─ /api/v1/auth (POST)          → JWT tokens            │   │
│  │ ├─ /api/v1/settings (GET/POST)  → User settings         │   │
│  │ └─ /health, /ready              → Health checks         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Middleware Stack                                          │   │
│  │ ├─ CORS (allowed origins)                                │   │
│  │ ├─ HTTPBearer (JWT validation)                           │   │
│  │ ├─ RateLimiting (slowapi)                                │   │
│  │ ├─ RequestLogging (structured logs)                      │   │
│  │ ├─ ErrorHandling (Sentry capture)                        │   │
│  │ └─ Observability (OpenTelemetry tracing)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ LangChain Integration                                     │   │
│  │ ├─ LLM Provider: Claude (via Anthropic SDK)              │   │
│  │ ├─ Vector Store: LanceDB (local)                         │   │
│  │ ├─ Memory: Redis + SQLAlchemy (persistent)               │   │
│  │ ├─ Tools: Knowledge.store, memory.query, web.search      │   │
│  │ ├─ RAG Pipeline: retrieve → rerank → contextualize       │   │
│  │ └─ Callbacks: LangSmith tracing (production)             │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐
│  VCR        │  │ Databases    │  │ Observability Stack │
│  (Decision) │  │ (Persistence)│  │ (Monitoring)        │
│             │  │              │  │                     │
│ XLM-RoBERTa │  │ PostgreSQL   │  │ LangSmith (LLM)    │
│ + LoRA      │  │ Redis        │  │ Prometheus         │
│ + PyTorch   │  │ LanceDB      │  │ Jaeger (Tracing)   │
│             │  │              │  │ Grafana (Viz)      │
│ Python      │  │ SQLAlchemy   │  │ Sentry (Errors)    │
│ subprocess  │  │ TypeORM      │  │ OpenTelemetry      │
│ or gRPC     │  │              │  │                    │
└─────────────┘  └──────────────┘  └─────────────────────┘
```

---

## API Backend

### Framework e Núcleo

| Component             | Version | Purpose                           |
| --------------------- | ------- | --------------------------------- |
| **FastAPI**           | 0.104+  | Framework web assíncrono moderno  |
| **Uvicorn**           | 0.24+   | Servidor ASGI (desenvolvimento)   |
| **Gunicorn**          | 21+     | Servidor WSGI de produção         |
| **Python**            | 3.10+   | Runtime                           |
| **Pydantic**          | 2.5+    | Validação e serialização de dados |
| **Pydantic Settings** | 2.5+    | Configuração de ambiente          |

### Integração LangChain

| Component               | Version | Purpose                    |
| ----------------------- | ------- | -------------------------- |
| **langchain**           | 0.1+    | Framework principal        |
| **langchain-anthropic** | 0.1+    | Integração Claude          |
| **langchain-core**      | 0.1+    | Tipos base e callbacks     |
| **langchain-community** | 0.1+    | Ecossistema de ferramentas |

### Autenticação e Segurança

| Component            | Version | Purpose                        |
| -------------------- | ------- | ------------------------------ |
| **python-jose**      | 3.3+    | Codificação/decodificação JWT  |
| **passlib**          | 1.7+    | Hashing de senha (bcrypt)      |
| **bcrypt**           | 4.0+    | Hashing criptográfico          |
| **python-multipart** | 0.0.6+  | Análise de dados de formulário |

### Banco de Dados e ORM

| Component           | Version | Purpose                                 |
| ------------------- | ------- | --------------------------------------- |
| **SQLAlchemy**      | 2.0+    | ORM (PostgreSQL)                        |
| **psycopg2-binary** | 2.9+    | Adaptador PostgreSQL                    |
| **alembic**         | 1.12+   | Migrações de banco de dados             |
| **lancedb**         | 0.3+    | Banco de dados vetorial (Nativo Python) |

### Caching e Gerenciamento de Sessão

| Component             | Version | Purpose                    |
| --------------------- | ------- | -------------------------- |
| **redis**             | 5.0+    | Cache em memória + sessões |
| **aioredis**          | 2.0+    | Cliente Redis assíncrono   |
| **python-redis-lock** | 4.0+    | Bloqueio distribuído       |

### Observabilidade e Logging

| Component                                    | Version | Purpose                        |
| -------------------------------------------- | ------- | ------------------------------ |
| **opentelemetry-api**                        | 1.20+   | Padrões de rastreamento        |
| **opentelemetry-sdk**                        | 1.20+   | Implementação de rastreamento  |
| **opentelemetry-exporter-jaeger**            | 1.20+   | Exportador Jaeger              |
| **opentelemetry-exporter-prometheus**        | 0.41b+  | Exportador Prometheus          |
| **opentelemetry-instrumentation-fastapi**    | 0.41b+  | Auto-instrumentação FastAPI    |
| **opentelemetry-instrumentation-sqlalchemy** | 0.41b+  | Auto-instrumentação SQLAlchemy |
| **opentelemetry-instrumentation-redis**      | 0.41b+  | Auto-instrumentação Redis      |
| **sentry-sdk**                               | 1.38+   | Rastreamento de erros          |
| **python-json-logger**                       | 2.0+    | Logging estruturado em JSON    |

### Limitação de Taxa e Validação

| Component           | Version | Purpose                        |
| ------------------- | ------- | ------------------------------ |
| **slowapi**         | 0.1+    | Limitação de taxa para FastAPI |
| **email-validator** | 2.1+    | Validação de e-mail            |

### Ferramentas de Desenvolvimento

| Component          | Version | Purpose                      |
| ------------------ | ------- | ---------------------------- |
| **ruff**           | 0.1+    | Linter Python rápido         |
| **mypy**           | 1.7+    | Verificação de tipo estática |
| **black**          | 23.10+  | Formatador de código         |
| **pytest**         | 7.4+    | Framework de testes          |
| **pytest-asyncio** | 0.21+   | Suporte a testes assíncronos |
| **pytest-cov**     | 4.1+    | Relatório de cobertura       |
| **httpx**          | 0.25+   | Cliente HTTP (assíncrono)    |

### Exemplo de Arquivo de Dependências

```txt
# requirements.txt (Backend API)

# Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pydantic==2.5.0
pydantic-settings==2.1.0

# LangChain
langchain==0.1.0
langchain-anthropic==0.1.0
langchain-core==0.1.0
langchain-community==0.1.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.1
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
lancedb==0.3.0

# Cache
redis==5.0.1
aioredis==2.0.1
python-redis-lock==4.0.0

# Observability
opentelemetry-api==1.20.0
opentelemetry-sdk==1.20.0
opentelemetry-exporter-jaeger==1.20.0
opentelemetry-exporter-prometheus==0.41b0
opentelemetry-instrumentation-fastapi==0.41b0
opentelemetry-instrumentation-sqlalchemy==0.41b0
opentelemetry-instrumentation-redis==0.41b0
sentry-sdk[fastapi]==1.38.0
python-json-logger==2.0.7

# Rate limiting
slowapi==0.1.9
email-validator==2.1.0

# Development
ruff==0.1.11
mypy==1.7.1
black==23.10.1
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
```

---

## Vectora Cognitive Runtime

### Stack ML em Python

| Component        | Version | Purpose                                    |
| ---------------- | ------- | ------------------------------------------ |
| **PyTorch**      | 2.1+    | Framework de deep learning                 |
| **transformers** | 4.35+   | Carregamento de modelos (Hugging Face)     |
| **peft**         | 0.7+    | Ajuste fino eficiente em parâmetros (LoRA) |
| **numpy**        | 1.24+   | Computação numérica                        |
| **scikit-learn** | 1.3+    | Métricas de avaliação                      |

### Modelo Base

| Component                | Params | Languages         | Purpose                    |
| ------------------------ | ------ | ----------------- | -------------------------- |
| **XLM-RoBERTa-small**    | 24M    | 101 (incl. PT-BR) | Codificador base           |
| **LoRA (r=8, alpha=16)** | ~2M    | -                 | Adaptadores de ajuste fino |

### Treinamento e Avaliação

| Component       | Version | Purpose                                 |
| --------------- | ------- | --------------------------------------- |
| **tensorboard** | 2.14+   | Visualização de treinamento             |
| **wandb**       | 0.16+   | Rastreamento de experimentos (opcional) |
| **pandas**      | 2.1+    | Processamento de dados                  |
| **tqdm**        | 4.66+   | Barras de progresso                     |

### Processamento de Dados

| Component      | Version | Purpose                                  |
| -------------- | ------- | ---------------------------------------- |
| **datasets**   | 2.14+   | Datasets do Hugging Face (opcional)      |
| **jsonschema** | 4.20+   | Validar formato dos dados de treinamento |

### Exemplo de Arquivo de Dependências

```txt
# requirements-vcr.txt (VCR)

# Core ML
torch==2.1.0
transformers==4.35.2
peft==0.7.1
numpy==1.24.3
scikit-learn==1.3.2

# Training
tensorboard==2.14.1
wandb==0.16.0
pandas==2.1.3
tqdm==4.66.1

# Data
datasets==2.14.1
jsonschema==4.20.0
```

### Estrutura de Diretórios

```
vectora-cognitive-runtime/
├── scripts/
│   ├── download_base.py        # Download XLM-RoBERTa-small
│   ├── build_dataset.py        # Synthetic (Phase 1) or Real (Phase 2+)
│   ├── train.py                # Fine-tune with LoRA
│   ├── eval.py                 # Evaluate accuracy, calibration
│   └── export_onnx.py          # Export to ONNX (Phase 4+)
├── src/
│   ├── model.py                # XLM-RoBERTa + classification head
│   ├── decision.py             # Decision logic (Agent/Tool/Web/Recovery)
│   ├── recovery.py             # Fallback strategies
│   ├── inference.py            # Inference loop (subprocess)
│   ├── server.py               # gRPC server (Phase 4+)
│   └── __init__.py
├── data/
│   ├── raw/
│   │   ├── synthetic_queries.jsonl
│   │   └── production_traces.jsonl
│   └── processed/
│       ├── train_set.jsonl
│       ├── val_set.jsonl
│       └── test_set.jsonl
├── models/
│   ├── checkpoints/
│   │   ├── lora_r8_a16_epoch1/
│   │   ├── lora_r8_a16_epoch3/
│   │   └── lora_r8_a16_final/
│   └── exports/
│       └── vcr-policy-v1.onnx  (Phase 4+)
├── evaluation/
│   ├── golden_queries.jsonl
│   ├── metrics.py
│   └── test_production_readiness.py
├── config.yaml                 # Hyperparameters
├── requirements.txt
├── .env.example
├── Makefile
└── README.md
```

---

## SDK de Integrações

### Configuração do Monorepo

| Component      | Version | Purpose                               |
| -------------- | ------- | ------------------------------------- |
| **Turborepo**  | 1.10+   | Orquestração do monorepo              |
| **pnpm**       | 8.12+   | Gerenciador de pacotes (modo estrito) |
| **TypeScript** | 5.2+    | Language                              |
| **Node.js**    | 20+ LTS | Runtime                               |

### Pacote Compartilhado (@vectora/shared)

| Component        | Version | Purpose                          |
| ---------------- | ------- | -------------------------------- |
| **zod**          | 3.22+   | Validação com segurança de tipos |
| **jsonwebtoken** | 9.1+    | Manipulação de JWT               |
| **axios**        | 1.6+    | HTTP client                      |

### SDK do Claude Code (@vectora/sdk-claude-code)

| Component                     | Version | Purpose      |
| ----------------------------- | ------- | ------------ |
| **@modelcontextprotocol/sdk** | 0.1+    | MCP protocol |

### SDK da CLI do Gemini (@vectora/sdk-gemini-cli)

| Component                 | Version | Purpose       |
| ------------------------- | ------- | ------------- |
| **@google/generative-ai** | 0.3+    | Gemini client |

### SDK do Paperclip (@vectora/sdk-paperclip)

| Component             | Version | Purpose        |
| --------------------- | ------- | -------------- |
| **@paperclipai/core** | -       | Paperclip core |

### Testes e Qualidade

| Component                  | Version | Purpose                    |
| -------------------------- | ------- | -------------------------- |
| **jest**                   | 29.7+   | Framework de testes        |
| **@testing-library/react** | 14.0+   | Teste de componentes React |
| **eslint**                 | 8.53+   | Linting                    |
| **prettier**               | 3.0+    | Formatting                 |

### Exemplo de Arquivo de Dependências

```json
{
  "name": "@vectora/shared",
  "version": "1.0.0",
  "dependencies": {
    "zod": "^3.22.4",
    "jsonwebtoken": "^9.1.2",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "typescript": "^5.2.2",
    "@types/node": "^20.8.0",
    "jest": "^29.7.0",
    "eslint": "^8.53.0",
    "prettier": "^3.0.3"
  }
}
```

### Estrutura de Diretórios

```
vectora-integrations/
├── packages/
│   ├── shared/
│   │   ├── src/
│   │   │   ├── types/
│   │   │   │   ├── vectora.ts
│   │   │   │   ├── agents.ts
│   │   │   │   └── auth.ts
│   │   │   ├── auth/
│   │   │   │   ├── jwt.ts
│   │   │   │   └── encryption.ts
│   │   │   ├── http/
│   │   │   │   └── client.ts
│   │   │   └── errors/
│   │   │       └── index.ts
│   │   └── package.json
│   │
│   ├── claude-code/
│   │   ├── src/
│   │   │   ├── mcp/
│   │   │   │   ├── server.ts
│   │   │   │   ├── handlers.ts
│   │   │   │   └── types.ts
│   │   │   ├── client.ts
│   │   │   ├── tools/
│   │   │   │   ├── search.ts
│   │   │   │   ├── rerank.ts
│   │   │   │   ├── websearch.ts
│   │   │   │   └── knowledge.ts
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   ├── gemini-cli/
│   ├── paperclip/
│   ├── hermes/
│   └── custom-template/
│
├── apps/
│   └── docs/
│       ├── content/
│       └── package.json
│
├── turbo.json
├── pnpm-workspace.yaml
├── tsconfig.base.json
├── package.json
└── .github/
    └── workflows/
        ├── test.yml
        ├── build.yml
        └── publish.yml
```

---

## Site e Documentação

### Gerador de Site Estático

| Component        | Version | Purpose                   |
| ---------------- | ------- | ------------------------- |
| **Hugo**         | 0.120+  | Static site generator     |
| **Hextra Theme** | latest  | Tema moderno e responsivo |

### Idiomas do Conteúdo

- **English** (/en/)
- **Portuguese Brazil** (/pt-br/)

### Seções de Conteúdo

```
content/
├── en/
│   ├── docs/
│   │   ├── getting-started/ (setup: local, docker, vps)
│   │   ├── architecture/ (overview, tier-based, data-flow)
│   │   ├── api-reference/ (chat, memory, datasets, auth, settings)
│   │   ├── integrations/ (claude-code, gemini, paperclip, custom)
│   │   ├── contributing/ (dev-setup, code-style, pull-requests)
│   │   └── faq/
│   ├── blog/
│   └── about/
│
└── pt-br/
    ├── docs/
    ├── blog/
    └── about/
```

### Implantação

| Platform         | Method                    | Purpose                       |
| ---------------- | ------------------------- | ----------------------------- |
| **GitHub Pages** | Deploy automático da main | Hospedagem estática           |
| **Netlify**      | Integração de hook do Git | CDN + deploys de visualização |
| **Fly.io**       | Contêiner Docker          | Alternativa serverless        |

---

## Banco de Dados e Armazenamento

### PostgreSQL

| Aspect          | Configuration                         | Purpose                               |
| --------------- | ------------------------------------- | ------------------------------------- |
| **Version**     | 15+                                   | Banco de dados relacional de produção |
| **Embedded**    | SQLite (dev) ou PostgreSQL gerenciado | Local development                     |
| **Persistence** | 50Gi (Kubernetes)                     | Volume persistente                    |
| **Backup**      | Scripts pg_dump (diário)              | Recuperação de dados                  |

### Redis

| Aspect          | Configuration          | Purpose                    |
| --------------- | ---------------------- | -------------------------- |
| **Version**     | 7+                     | Cache em memória + sessões |
| **Persistence** | AOF (Append-Only File) | Durabilidade de dados      |
| **Persistence** | 10Gi (Kubernetes)      | Volume persistente         |
| **TTL**         | Configurável por chave | Expiração automática       |

### LanceDB

| Aspect            | Configuration            | Purpose                         |
| ----------------- | ------------------------ | ------------------------------- |
| **Version**       | 0.3+                     | Banco de dados vetorial         |
| **Mode**          | Diretório local (Python) | Armazenamento vetorial embutido |
| **Indexing**      | IVF (Inverted File)      | Pesquisa de similaridade rápida |
| **Armazenamento** | 20Gi (Kubernetes)        | Volume persistente              |

### Exemplo de Esquema (PostgreSQL)

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat sessions
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
    role VARCHAR(50) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Datasets
CREATE TABLE datasets (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    vector_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Stack de Observabilidade

### LangSmith (Rastreamento de LLM)

| Aspect       | Configuration                      | Purpose                            |
| ------------ | ---------------------------------- | ---------------------------------- |
| **Endpoint** | api.smith.langchain.com            | Rastreamento de LLM na nuvem       |
| **SDK**      | langsmith==0.0.65+                 | Integration                        |
| **Tracing**  | Automático via callbacks LangChain | Rastreia todas as chamadas LLM     |
| **Pricing**  | Nível gratuito disponível          | Sem custo de configuração para dev |

**Setup:**

```bash
# .env
LANGSMITH_API_KEY=your-api-key
LANGSMITH_PROJECT=vectora-dev
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

### Prometheus (Coleta de Métricas)

| Aspect              | Configuration     | Purpose                                        |
| ------------------- | ----------------- | ---------------------------------------------- |
| **Version**         | 2.48+             | Banco de dados de métricas de séries temporais |
| **Scrape Interval** | 15s               | Frequência de coleta padrão                    |
| **Retention**       | 15d               | Período de retenção de dados                   |
| **Port**            | 9090 (standalone) | Web UI                                         |

**Configuration Example:**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "vectora-api"
    static_configs:
      - targets: ["localhost:8000"]
    metrics_path: "/metrics"

  - job_name: "vectora-vcr"
    static_configs:
      - targets: ["localhost:8001"]
    metrics_path: "/metrics"
```

### Jaeger (Rastreamento Distribuído)

| Aspect             | Configuration                     | Purpose                  |
| ------------------ | --------------------------------- | ------------------------ |
| **Version**        | 1.50+                             | Rastreamento distribuído |
| **Port UI**        | 16686                             | Jaeger UI                |
| **Port Collector** | 14268                             | Coleta de spans          |
| **Backend**        | Elasticsearch ou Cassandra (prod) | Armazenamento            |

**Docker Compose:**

```yaml
jaeger:
  image: jaegertracing/all-in-one:latest
  ports:
    - "16686:16686" # Web UI
    - "14268:14268" # Collector (HTTP)
    - "6831:6831/udp" # Agent (UDP)
```

### Grafana (Visualização)

| Aspect           | Configuration                     | Purpose                        |
| ---------------- | --------------------------------- | ------------------------------ |
| **Version**      | 10.2+                             | Visualização de métricas       |
| **Port**         | 3000                              | Web UI                         |
| **Data Sources** | Prometheus, Jaeger, Loki          | Múltiplas fontes               |
| **Dashboards**   | Pré-construídos ou personalizados | Visualizações de monitoramento |

**Default Credentials:**

```
Username: admin
Password: admin (change after first login)
```

### Sentry (Rastreamento de Erros)

| Aspect      | Configuration                     | Purpose                        |
| ----------- | --------------------------------- | ------------------------------ |
| **Version** | latest                            | Rastreamento e alerta de erros |
| **Port**    | 9000                              | Web UI (local)                 |
| **Backend** | PostgreSQL + Redis                | Armazenamento                  |
| **DSN**     | https://<key>@<host>/<project_id> | Endpoint do SDK                |

**Local Docker Compose:**

```yaml
sentry-postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: sentry
    POSTGRES_USER: sentry
    POSTGRES_PASSWORD: sentry-local-dev

sentry-redis:
  image: redis:7-alpine

sentry:
  image: sentry:latest
  environment:
    SENTRY_SECRET_KEY: your-secret-key
    SENTRY_POSTGRES_HOST: sentry-postgres
    SENTRY_REDIS_HOST: sentry-redis
  ports:
    - "9000:9000"
```

### OpenTelemetry (Padrões)

| Component                             | Version | Purpose                  |
| ------------------------------------- | ------- | ------------------------ |
| **opentelemetry-api**                 | 1.20+   | API padrão               |
| **opentelemetry-sdk**                 | 1.20+   | Implementação do SDK     |
| **opentelemetry-exporter-jaeger**     | 1.20+   | Enviar para o Jaeger     |
| **opentelemetry-exporter-prometheus** | 0.41b+  | Enviar para o Prometheus |
| **opentelemetry-instrumentation-\***  | 0.41b+  | Auto-instrumentação      |

### Stack de Observabilidade Unificada (Local)

**docker-compose.local.yml:**

```yaml
version: "3.8"

services:
  # Metrics
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./observability/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  # Tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
      - "6831:6831/udp"
    environment:
      COLLECTOR_ZIPKIN_HOST_PORT: ":9411"

  # Visualization
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - ./observability/grafana/datasources:/etc/grafana/provisioning/datasources
      - ./observability/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

  # Error Tracking
  sentry-postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: sentry
      POSTGRES_USER: sentry
      POSTGRES_PASSWORD: sentry-local-dev
    volumes:
      - sentry_postgres:/var/lib/postgresql/data

  sentry-redis:
    image: redis:7-alpine

  sentry:
    image: sentry:latest
    ports:
      - "9000:9000"
    environment:
      SENTRY_SECRET_KEY: your-secret-key-change-this
      SENTRY_POSTGRES_HOST: sentry-postgres
      SENTRY_POSTGRES_USER: sentry
      SENTRY_POSTGRES_PASSWORD: sentry-local-dev
      SENTRY_REDIS_HOST: sentry-redis
    depends_on:
      - sentry-postgres
      - sentry-redis
    volumes:
      - sentry_data:/var/lib/sentry

  sentry-worker:
    image: sentry:latest
    environment:
      SENTRY_SECRET_KEY: your-secret-key-change-this
      SENTRY_POSTGRES_HOST: sentry-postgres
      SENTRY_POSTGRES_USER: sentry
      SENTRY_POSTGRES_PASSWORD: sentry-local-dev
      SENTRY_REDIS_HOST: sentry-redis
    depends_on:
      - sentry-postgres
      - sentry-redis
    command: run worker
    volumes:
      - sentry_data:/var/lib/sentry

volumes:
  prometheus_data:
  grafana_data:
  sentry_postgres:
  sentry_data:
```

---

## DevOps e Infraestrutura

### Conteinerização

#### Docker

| Aspect       | Configuration                         | Purpose                        |
| ------------ | ------------------------------------- | ------------------------------ |
| **Engine**   | Docker 24+                            | Tempo de execução do contêiner |
| **Compose**  | 2.20+                                 | Orquestração local             |
| **Registry** | Docker Hub, GitHub Container Registry | Armazenamento de imagens       |

#### Dockerfile da API Backend

```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY src/ ./src/
COPY config/ ./config/

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "src.main:app"]
```

#### Dockerfile do VCR

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-vcr.txt .
RUN pip install --no-cache-dir -r requirements-vcr.txt

COPY vectora-cognitive-runtime/src ./src/
COPY vectora-cognitive-runtime/models ./models/

EXPOSE 8001
CMD ["python", "src/server.py", "--port", "8001"]
```

### Pipeline CI/CD

#### GitHub Actions

**Estrutura do Workflow:**

```
.github/workflows/
├── test.yml              # Run tests on PR
├── lint.yml              # Ruff, Mypy, Black
├── build.yml             # Build Docker images
├── security-scan.yml     # Trivy, SAST
└── deploy.yml            # Deploy to production
```

**Example: test.yml**

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**Example: deploy.yml**

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: [test, lint, security-scan]

    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v2

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/vectora-api:latest
            ${{ secrets.DOCKER_USERNAME }}/vectora-api:${{ github.sha }}

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/vectora-api \
            vectora-api=docker.io/${{ secrets.DOCKER_USERNAME }}/vectora-api:${{ github.sha }}
```

#### Jenkins

**Estrutura do Jenkinsfile:**

```groovy
pipeline {
    agent any

    environment {
        REGISTRY = credentials('docker-registry')
        DOCKER_IMAGE = "${REGISTRY}/vectora-api"
        VERSION = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    python -m pytest
                '''
            }
        }

        stage('Lint & Type Check') {
            steps {
                sh '''
                    ruff check .
                    mypy src/
                    black --check src/
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    pip install bandit
                    bandit -r src/
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${VERSION} .
                    docker push ${DOCKER_IMAGE}:${VERSION}
                '''
            }
        }

        stage('Deploy to Dev') {
            steps {
                sh '''
                    kubectl set image deployment/vectora-api-dev \
                      vectora-api=${DOCKER_IMAGE}:${VERSION} \
                      -n dev
                '''
            }
        }

        stage('Manual Approval for Prod') {
            steps {
                input 'Deploy to Production?'
            }
        }

        stage('Deploy to Production') {
            steps {
                sh '''
                    kubectl set image deployment/vectora-api-prod \
                      vectora-api=${DOCKER_IMAGE}:${VERSION} \
                      -n production
                '''
            }
        }
    }

    post {
        failure {
            script {
                sh '''
                    curl -X POST -H 'Content-type: application/json' \
                      --data '{"text":"Build failed: ${BUILD_URL}"}' \
                      ${SLACK_WEBHOOK}
                '''
            }
        }
    }
}
```

### Kubernetes e Helm

#### Estrutura do Helm Chart

```
helm/vectora/
├── Chart.yaml                    # Chart metadata
├── values.yaml                   # Default configuration
├── values-dev.yaml               # Dev overrides
├── values-prod.yaml              # Prod overrides
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secret.yaml
    ├── statefulset-postgres.yaml
    ├── statefulset-redis.yaml
    └── statefulset-lancedb.yaml
```

#### Exemplo de Valores do Helm

**values.yaml (Default):**

```yaml
namespace: default
replicaCount: 1

image:
  repository: docker.io/vectora/api
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
  targetPort: 8000

ingress:
  enabled: false
  className: nginx
  hosts:
    - host: vectora.local
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 3
  targetCPUUtilizationPercentage: 80

postgres:
  enabled: true
  storage: 50Gi
  persistence:
    storageClass: standard

redis:
  enabled: true
  storage: 10Gi

lancedb:
  enabled: true
  storage: 20Gi

env:
  ENVIRONMENT: development
  LOG_LEVEL: INFO
```

**values-prod.yaml (Produção Override):**

```yaml
namespace: vectora-production
replicaCount: 3

image:
  tag: v1.0.0 # Pinned version
  pullPolicy: Always

service:
  type: LoadBalancer

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: api.vectora.ai
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: vectora-tls
      hosts:
        - api.vectora.ai

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 1000m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

postgres:
  storage: 500Gi
  backup:
    enabled: true
    schedule: "0 2 * * *" # Daily at 2 AM

redis:
  storage: 100Gi
  persistence: true

env:
  ENVIRONMENT: production
  LOG_LEVEL: WARN
```

#### Script de Implantação

**deploy.sh:**

```bash
#!/bin/bash

ENV=${1:-dev}
HELM_RELEASE=vectora
HELM_CHART=./helm/vectora

# Validate environment
if [[ "$ENV" != "dev" && "$ENV" != "prod" ]]; then
    echo "Usage: $0 {dev|prod}"
    exit 1
fi

# Build values file path
VALUES_FILE="helm/vectora/values-${ENV}.yaml"
if [[ ! -f "$VALUES_FILE" ]]; then
    VALUES_FILE="helm/vectora/values.yaml"
fi

echo "🚀 Deploying Vectora to $ENV environment..."
echo "📄 Using values: $VALUES_FILE"

# Helm upgrade or install
helm upgrade --install $HELM_RELEASE $HELM_CHART \
    -f $VALUES_FILE \
    -n vectora-$ENV \
    --create-namespace \
    --wait \
    --timeout 5m

echo "✅ Deployment complete!"
echo "🔗 Get service info: kubectl get svc -n vectora-$ENV"
```

---

## Segurança e Autenticação

### Autenticação JWT

| Component                     | Purpose                          | Details                        |
| ----------------------------- | -------------------------------- | ------------------------------ |
| **Geração de Token**          | Assinar JWT com segredo          | Payload: user_id, role, exp    |
| **Validação de Token**        | Verificar assinatura e expiração | Em toda requisição autenticada |
| **Atualização de Token**      | Gerar novo token                 | Via endpoint refresh_token     |
| **Gerenciamento de Segredos** | Armazenar no ambiente            | Nunca envie segredos (commit)  |

**Implementation:**

```python
# src/auth/jwt.py
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")
```

### RBAC (Controle de Acesso Baseado em Funções)

| Role           | Permissions                          | Use Case                             |
| -------------- | ------------------------------------ | ------------------------------------ |
| **admin**      | Todas as permissões                  | Administradores do sistema           |
| **researcher** | Ler datasets, rodar experimentos     | Cientistas de dados                  |
| **developer**  | Ler/escrever integrações             | Consumidores da API                  |
| **user**       | Ler próprios dados, gerenciar perfil | Usuários finais                      |
| **guest**      | Ler apenas dados públicos            | Usuários em período de teste (trial) |

**Permissions Matrix:**

```python
PERMISSIONS = {
    "admin": [
        "user:create", "user:read", "user:update", "user:delete",
        "dataset:create", "dataset:read", "dataset:update", "dataset:delete",
        "integration:create", "integration:read", "integration:update", "integration:delete",
        "settings:manage", "logs:view"
    ],
    "researcher": [
        "dataset:read", "dataset:create",
        "integration:read",
        "settings:view"
    ],
    "developer": [
        "integration:read", "integration:create",
        "dataset:read",
        "settings:view"
    ],
    "user": [
        "profile:read", "profile:update",
        "dataset:read",
    ],
    "guest": [
        "public:read"
    ]
}
```

### Segurança de Senha

| Component     | Configuration                                                 | Purpose                        |
| ------------- | ------------------------------------------------------------- | ------------------------------ |
| **Hashing**   | bcrypt (rounds=12)                                            | Armazenamento seguro de senha  |
| **Salt**      | Gerado automaticamente por senha                              | Proteção contra rainbow tables |
| **Validação** | Mín. 12 caracteres, maiúsculas, minúsculas, dígitos, especial | Senhas fortes                  |

### HTTPS e TLS

| Environment  | Certificate               | Auto-Renewal              |
| ------------ | ------------------------- | ------------------------- |
| **Local**    | Autoassinado (apenas dev) | Manual                    |
| **Produção** | Let's Encrypt             | cert-manager (Kubernetes) |

**Ingress with TLS:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vectora-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.vectora.ai
      secretName: vectora-tls
  rules:
    - host: api.vectora.ai
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: vectora-api
                port:
                  number: 80
```

### Configuração de CORS

```python
# src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vectora.ai",
        "https://app.vectora.ai",
        "http://localhost:3000",  # local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Limitação de Taxa

```python
# src/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/chat")
@limiter.limit("10/minute")
async def chat(request: Request, query: ChatRequest):
    return {"response": "..."}
```

---

## Testes e Qualidade

### Testes Unitários

| Framework          | Version | Purpose                         |
| ------------------ | ------- | ------------------------------- |
| **pytest**         | 7.4+    | Executor de testes              |
| **pytest-asyncio** | 0.21+   | Suporte a testes assíncronos    |
| **pytest-cov**     | 4.1+    | Relatório de cobertura          |
| **hypothesis**     | 6.87+   | Testes baseados em propriedades |

**Example Test:**

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_chat_endpoint(db_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={"query": "Hello", "session_id": "test-session"}
        )
        assert response.status_code == 200
```

### Testes de Integração

```python
# tests/integration/test_rag_pipeline.py
@pytest.mark.asyncio
async def test_rag_pipeline_end_to_end(db_session, vcr_service):
    # 1. Upload dataset
    dataset = await upload_dataset("test_docs.pdf")

    # 2. Query
    response = await query_service.process("What is Vectora?", dataset_id=dataset.id)

    # 3. Verify LLM response
    assert response["answer"] is not None
    assert len(response["sources"]) > 0
```

### Testes de Carga

| Tool       | Version | Purpose                     |
| ---------- | ------- | --------------------------- |
| **locust** | 2.17+   | Framework de teste de carga |
| **k6**     | 0.47+   | Teste de carga moderno      |

**Example Locust Test:**

```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class VectoraUser(HttpUser):
    wait_time = between(1, 3)

    @task(1)
    def health_check(self):
        self.client.get("/health")

    @task(3)
    def chat(self):
        self.client.post("/api/v1/chat", json={
            "query": "Hello",
            "session_id": "load-test"
        })

# Run: locust -f locustfile.py -u 100 -r 10 -t 5m
```

### Qualidade de Código

| Tool       | Version | Purpose              |
| ---------- | ------- | -------------------- |
| **ruff**   | 0.1+    | Linter Python rápido |
| **mypy**   | 1.7+    | Type checking        |
| **black**  | 23.10+  | Formatador de código |
| **pylint** | 3.0+    | Linting avançado     |
| **bandit** | 1.7+    | Linting de segurança |

**GitHub Actions Quality Gate:**

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Lint with Ruff
        run: ruff check .

      - name: Type check with Mypy
        run: mypy src/

      - name: Format check with Black
        run: black --check src/

      - name: Security with Bandit
        run: bandit -r src/
```

### Cobertura de Testes

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Minimum 80% coverage requirement
pytest --cov=src --cov-fail-under=80
```

---

## Ferramentas e Utilitários

### Ferramentas CLI

| Tool            | Version | Purpose                           |
| --------------- | ------- | --------------------------------- |
| **vectora-cli** | -       | Interface de linha de comando     |
| **docker**      | 24+     | Gerenciamento de contêineres      |
| **kubectl**     | 1.28+   | Gerenciamento de Kubernetes       |
| **helm**        | 3.13+   | Gerenciador de pacotes Kubernetes |
| **git**         | 2.40+   | Controle de versão                |

### Desenvolvimento Local

| Tool       | Version  | Purpose                   |
| ---------- | -------- | ------------------------- |
| **venv**   | Built-in | Ambiente virtual Python   |
| **make**   | GNU      | Automação de build        |
| **direnv** | 2.33+    | Gerenciamento de ambiente |

**Makefile Example:**

```makefile
.PHONY: help setup install test lint format clean run

help:
	@echo "Vectora Development Commands"
	@echo "  make setup    - Initialize dev environment"
	@echo "  make install  - Install dependencies"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Lint & format check"
	@echo "  make format   - Auto-format code"
	@echo "  make run      - Run development server"

setup:
	python -m venv venv
	source venv/bin/activate
	pip install --upgrade pip

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest --cov=src --cov-report=html

lint:
	ruff check .
	mypy src/
	black --check src/

format:
	ruff check --fix .
	black src/

clean:
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +

run:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Gerenciamento de Pacotes

| Tool          | Version | Purpose                              |
| ------------- | ------- | ------------------------------------ |
| **pip**       | 23.3+   | Gerenciador de pacotes Python        |
| **pip-tools** | 7.3+    | Travamento de dependências (locking) |
| **poetry**    | 1.7+    | Alternativa (opcional)               |

**requirements.txt Management:**

```bash
# Generate locked requirements
pip-compile requirements.in --output-file=requirements.txt

# Install locked versions
pip install -r requirements.txt

# Update specific package
pip-compile --upgrade-package flask requirements.in
```

### Gerenciamento de Versão

| Tool                    | Purpose                | Configuration     |
| ----------------------- | ---------------------- | ----------------- |
| **Semantic Versioning** | Numeração de versão    | MAJOR.MINOR.PATCH |
| **.version** file       | Única fonte de verdade | `1.0.0`           |
| **git tags**            | Marcadores de release  | `v1.0.0`          |

**Version Workflow:**

```bash
# Read version
VERSION=$(cat .version)

# Create release
git tag -a v${VERSION} -m "Release ${VERSION}"
git push origin v${VERSION}

# Docker build with version
docker build -t vectora/api:${VERSION} .
```

---

## Alvos de Implantação

### Desenvolvimento Local

**Ambiente: Máquina do Desenvolvedor**

```bash
# Setup
docker-compose -f docker-compose.local.yml up -d

# Access points
API: http://localhost:8000
Docs: http://localhost:8000/docs
Prometheus: http://localhost:9090
Jaeger: http://localhost:16686
Grafana: http://localhost:3000
Sentry: http://localhost:9000
```

### Staging

**Ambiente: VM na Nuvem ou Self-Hosted**

```bash
# Deploy
helm upgrade --install vectora ./helm/vectora \
  -f helm/vectora/values-staging.yaml \
  -n vectora-staging
```

**Access:**

```
API: https://staging-api.vectora.ai
Docs: https://staging-api.vectora.ai/docs
```

### Produção

**Ambiente: Cluster Kubernetes**

```bash
# High-availability deployment
helm upgrade --install vectora ./helm/vectora \
  -f helm/vectora/values-prod.yaml \
  -n vectora-production \
  --wait
```

**Recursos:**

- 3+ réplicas com auto-scaling (3-10)
- PostgreSQL com backups diários
- Redis com persistência
- TLS com Let's Encrypt
- Failover multirregional (opcional)

**Monitoramento:**

```bash
# Watch deployment
kubectl rollout status deployment/vectora-api -n vectora-production

# View logs
kubectl logs -f deployment/vectora-api -n vectora-production

# Get metrics
kubectl top pods -n vectora-production
```

### Provedores de Nuvem

| Provider         | Service  | Configuration          |
| ---------------- | -------- | ---------------------- |
| **AWS**          | EKS      | Cluster Kubernetes     |
| **GCP**          | GKE      | Cluster Kubernetes     |
| **Azure**        | AKS      | Cluster Kubernetes     |
| **DigitalOcean** | DOKS     | Cluster Kubernetes     |
| **Fly.io**       | Machines | Implantação serverless |

---

## Variáveis de Ambiente

### .env Obrigatório (API Backend)

```env
# Core
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/vectora
REDIS_URL=redis://localhost:6379/0
LANCEDB_PATH=./data/lancedb

# Authentication
JWT_SECRET_KEY=your-secret-key-min-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# LangChain
ANTHROPIC_API_KEY=your-anthropic-api-key
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=vectora-dev
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Observability
SENTRY_DSN=https://key@localhost:9000/project_id
JAEGER_ENDPOINT=http://localhost:14268/api/traces
PROMETHEUS_PUSHGATEWAY_URL=http://localhost:9091

# Security
CORS_ORIGINS=["http://localhost:3000", "https://vectora.ai"]
TRUSTED_HOSTS=["localhost", "vectora.ai"]
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# External Services
SERPAPI_API_KEY=optional-for-web-search
```

### .env Obrigatório (VCR)

```env
# Model
MODEL_PATH=./models/checkpoints/lora_r8_a16_final/
DEVICE=cpu  # or cuda
BATCH_SIZE=32

# Inference
CONFIDENCE_THRESHOLD=0.7
MAX_CONTEXT_LENGTH=512
```

---

## Referência Rápida: Resumo da Stack

| Layer                   | Technology       | Version   | Purpose                          |
| ----------------------- | ---------------- | --------- | -------------------------------- |
| **Language (Backend)**  | Python           | 3.10+     | Desenvolvimento rápido de API    |
| **Framework**           | FastAPI          | 0.104+    | Framework web assíncrono moderno |
| **Server**              | Uvicorn/Gunicorn | 0.24+/21+ | Produção-grade serving           |
| **ORM**                 | SQLAlchemy       | 2.0+      | Abstração de banco de dados      |
| **Vector DB**           | LanceDB          | 0.3+      | Embedded vector search           |
| **Cache**               | Redis            | 7+        | Session & in-memory cache        |
| **ML Framework**        | PyTorch          | 2.1+      | Redes neurais                    |
| **Transformers**        | Hugging Face     | 4.35+     | Modelos pré-treinados            |
| **LangChain**           | LangChain        | 0.1+      | Orquestração de LLM              |
| **Observability**       | OpenTelemetry    | 1.20+     | Rastreamento padronizado         |
| **Metrics**             | Prometheus       | 2.48+     | Time-series DB                   |
| **Tracing**             | Jaeger           | 1.50+     | Rastreamento distribuído         |
| **Viz**                 | Grafana          | 10.2+     | Dashboard de métricas            |
| **Error Tracking**      | Sentry           | latest    | Monitoramento de erros           |
| **LLM Tracing**         | LangSmith        | Cloud     | Observabilidade do LangChain     |
| **Conteinerização**     | Docker           | 24+       | Tempo de execução do contêiner   |
| **Orchestration**       | Kubernetes       | 1.28+     | Orquestração de contêineres      |
| **Package Manager**     | Helm             | 3.13+     | Pacotes Kubernetes               |
| **CI/CD**               | GitHub Actions   | -         | Workflows automatizados          |
| **Pipeline**            | Jenkins          | 2.400+    | CI/CD alternativo                |
| **Static Site**         | Hugo             | 0.120+    | Gerador de documentação          |
| **Documentation Theme** | Hextra           | latest    | Tema Hugo moderno                |
| **Testing**             | pytest           | 7.4+      | Testes em Python                 |
| **Linting**             | Ruff             | 0.1+      | Linter Python rápido             |
| **Type Checking**       | Mypy             | 1.7+      | Verificação de tipo estática     |
| **Formatting**          | Black            | 23.10+    | Formatador de código             |
| **Security**            | Bandit           | 1.7+      | Security linter                  |

---

## Próximos Passos

1. **Fase 1 (Atual):** Desenvolvimento local com docker-compose
2. **Fase 2:** Pipeline CI/CD com GitHub Actions
3. **Fase 3:** Integração com Jenkins para implantações em produção
4. **Fase 4:** Configuração do cluster Kubernetes
5. **Fase 5:** Failover multirregional e observabilidade avançada

---

**Última Atualização:** 2026-05-03  
**Status:** Documentação Completa da Stack  
**Proprietário:** Equipe de Engenharia Vectora
