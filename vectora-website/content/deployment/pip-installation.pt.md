---
title: "Instalação via pip/pipx"
slug: pip-installation
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - cli
  - deployment
  - installation
  - pip
  - python
  - vectora
---

{{< lang-toggle >}}

A forma mais rápida de começar é instalar o Vectora via `pip` (desenvolvimento) ou `pipx` (isolado, recomendado para produção).

## Requisitos

- **Python 3.10+** (3.12 recomendado)
- **pip 23.0+** ou **pipx 1.0+**
- **PostgreSQL 15+** (rodando localmente ou remoto)
- **Redis 7+** (rodando localmente ou remoto)

## Instalação via pipx (Recomendado)

`pipx` instala o Vectora em um ambiente isolado, sem conflito com outras dependências:

```bash
# Instalar pipx se necessário
python3 -m pip install pipx

# Instalar Vectora
pipx install vectora

# Verificar instalação
vectora --version
# vectora 0.1.0
```

## Instalação via pip (Development)

Para desenvolvimento ou em ambientes virtuais:

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Instalar Vectora
pip install vectora

# Verificar
vectora --version
```

## Setup Inicial

### 1. Criar Arquivo de Configuração

Vectora procura por `.vectora/config.yaml` na home directory:

```bash
mkdir -p ~/.vectora
cat > ~/.vectora/config.yaml << 'EOF'
# LLM (Claude recomendado, ou GPT-4o, ou Gemini)
anthropic_api_key: "sk-ant-xxx"
llm_provider: "anthropic"
llm_model: "claude-sonnet-4-6"

# Embeddings (VoyageAI — obrigatório)
voyage_api_key: "sk-voyage-xxx"

# Database (PostgreSQL)
database_url: "postgresql://user:password@localhost:5432/vectora"

# Cache (Redis)
redis_host: "localhost"
redis_port: 6379
redis_db: 0

# Local (LanceDB)
lancedb_path: "./vectora-data"
EOF
```

Ou usar variáveis de ambiente:

```bash
export ANTHROPIC_API_KEY="sk-ant-xxx"
export VOYAGE_API_KEY="sk-voyage-xxx"
export DATABASE_URL="postgresql://user:password@localhost:5432/vectora"
export REDIS_HOST="localhost"
export REDIS_PORT=6379
```

### 2. Inicializar Banco de Dados

```bash
# Criar schema PostgreSQL
vectora init

# Verificar saúde
vectora health
# anthropic: ok
# voyage: ok (quota: 2M/2M tokens)
# database: ok
# redis: ok
# lancedb: ok
```

### 3. Indexar um Repositório

```bash
# Clone um repo (exemplo: este site)
git clone https://github.com/anthropics/vectora

# Indexar
vectora index add ./vectora --name "vectora"

# Ver progress
vectora index status
# vectora: 123 files, 456 chunks, 12% indexed
```

## Usando Vectora CLI

Depois de setup, você pode usar a CLI:

```bash
# Buscar em um bucket
vectora search "how to use vector search" --bucket vectora

# Iniciar conversa interativa
vectora chat

# Listar buckets
vectora bucket list

# Ver configuração
vectora config get
```

## Usando via Web Server

Para UI web interativa, rode:

```bash
vectora serve
# Server running at http://localhost:8000
```

Acesse `http://localhost:8000` no navegador.

## Verificação de Health

Antes de usar, sempre verifique:

```bash
vectora health
```

Saída esperada:

```text
System Health Check
══════════════════════════════════════════════════════════════
anthropic           ✓ Ready (model: claude-sonnet-4-6)
voyage              ✓ Ready (quota: 1.8M/2M tokens)
database            ✓ Connected (vectora@localhost:5432)
redis               ✓ Connected (uptime: 42h)
lancedb             ✓ Ready (buckets: 2)
──────────────────────────────────────────────────────────────
Overall Status      ✓ All systems operational
```

Se algum estiver ✗, veja [Troubleshooting](../troubleshooting/).

## Próximos Passos

1. Leia [Primeira Integração](../getting-started/first-integration.md)
2. Explore a [CLI Reference](../reference/cli-reference.md)
3. Para produção, considere [Docker Compose](./docker.md)

## Troubleshooting

### `command not found: vectora`

Se pipx instalou mas o comando não funciona:

```bash
# Verificar se está no PATH
pipx ensurepath

# Ou adicionar manualmente
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
exec $SHELL
```

### Erro de conexão PostgreSQL

```bash
# Verificar se PostgreSQL está rodando
psql -U postgres -h localhost -c "SELECT 1"

# Se falhar, instale PostgreSQL
# macOS:
brew install postgresql@15
brew services start postgresql@15

# Linux (Debian/Ubuntu):
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Erro de conexão Redis

```bash
# Verificar se Redis está rodando
redis-cli ping
# PONG = ok
# Connection refused = Redis não está running

# Instalar Redis
# macOS:
brew install redis
brew services start redis

# Linux:
sudo apt install redis-server
sudo systemctl start redis-server
```

## External Linking

| Conceito               | Recurso                    | Link                                                                   |
| ---------------------- | -------------------------- | ---------------------------------------------------------------------- |
| **pipx Documentation** | Installation and usage     | [pipx.pypa.io](https://pipx.pypa.io/)                                  |
| **Python venv**        | Virtual environments guide | [python.org/venv](https://docs.python.org/3/library/venv.html)         |
| **PostgreSQL Install** | Installation guide         | [postgresql.org/download](https://www.postgresql.org/download/)        |
| **Redis Install**      | Getting started with Redis | [redis.io/docs/getting-started](https://redis.io/docs/getting-started) |
| **Anthropic API**      | Claude API docs            | [docs.anthropic.com](https://docs.anthropic.com/)                      |
