---
title: "PostgreSQL: Metadados e Contexto"
slug: postgresql
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - acid
  - database
  - metadata
  - persistence
  - postgresql
  - sql
  - storage
  - vectora
---

{{< lang-toggle >}}

PostgreSQL armazena todos os metadados do Vectora: usuários, permissões (RBAC), histórico de queries, contexto de conversas e configurações. O banco é conectado via `pg8000` (driver Python puro).

## Schema Principal

O Vectora cria automaticamente as tabelas na inicialização:

```sql
-- Usuários e autenticação
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'developer',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Permissões por usuário
CREATE TABLE user_permissions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permission VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Buckets (namespaces de código)
CREATE TABLE buckets (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner_id UUID REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Histórico de queries
CREATE TABLE queries (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    bucket_id UUID REFERENCES buckets(id),
    query_text TEXT NOT NULL,
    embedding_time_ms FLOAT,
    search_time_ms FLOAT,
    rerank_time_ms FLOAT,
    llm_time_ms FLOAT,
    total_time_ms FLOAT,
    results_count INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Contexto de conversas (multi-turn)
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    bucket_id UUID REFERENCES buckets(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Mensagens da conversa
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50),  -- 'user' ou 'assistant'
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Configuração

Via ambiente:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/vectora"
```

Via config CLI:

```bash
vectora config set database_url postgresql://user:password@localhost:5432/vectora
```

Variáveis esperadas:

- `DATABASE_HOST` (padrão: localhost)
- `DATABASE_PORT` (padrão: 5432)
- `DATABASE_USER` (padrão: vectora)
- `DATABASE_PASSWORD` (obrigatório)
- `DATABASE_NAME` (padrão: vectora)

## Inicialização do Banco

O Vectora migra automaticamente no startup:

```bash
vectora init
# Creates tables, indexes, and default roles
```

Para reset completo (cuidado — apaga tudo):

```bash
vectora db reset --confirm
```

## Índices para Performance

O Vectora cria índices automaticamente para queries frequentes:

```sql
-- Lookups rápidos
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_buckets_owner ON buckets(owner_id);
CREATE INDEX idx_queries_user_bucket ON queries(user_id, bucket_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);

-- Busca por tempo (para limpeza de histórico)
CREATE INDEX idx_queries_created_at ON queries(created_at);
CREATE INDEX idx_messages_conversation_created_at ON messages(conversation_id, created_at);
```

## Backups e Replicação

Para backup regular:

```bash
# Full dump
pg_dump postgresql://user:pass@localhost:5432/vectora > backup.sql

# Compressed
pg_dump -F c postgresql://user:pass@localhost/vectora > backup.dump

# Restore
pg_restore -d vectora backup.dump
```

Para setup de replicação em alta disponibilidade, consulte a [documentação oficial do PostgreSQL](https://www.postgresql.org/docs/current/warm-standby.html).

## Pool de Conexões

O Vectora usa `pg8000` com um pool padrão de **5-10 conexões**. Configure via:

```bash
vectora config set database_pool_size 10
vectora config set database_pool_timeout 30
```

Para aplicações com muitos usuários simultâneos, aumente o pool ou use um proxy como **PgBouncer**:

```bash
# PgBouncer config (pgbouncer.ini)
[databases]
vectora = host=localhost port=5432 dbname=vectora

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

## Limpeza de Histórico

Para manter o banco otimizado, remova queries antigas periodicamente:

```sql
-- Remover queries com mais de 30 dias
DELETE FROM queries WHERE created_at < NOW() - INTERVAL '30 days';

-- Remover conversas órfãs
DELETE FROM conversations
WHERE created_at < NOW() - INTERVAL '90 days'
AND user_id NOT IN (SELECT DISTINCT user_id FROM conversations ORDER BY created_at DESC LIMIT 100);
```

## Monitoramento

Ver estatísticas do banco:

```sql
-- Tamanho do banco
SELECT pg_size_pretty(pg_database_size('vectora'));

-- Tabelas grandes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Queries lentas (requer log_statement = 'all')
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

## External Linking

| Conceito               | Recurso                                  | Link                                                                                                                       |
| ---------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **PostgreSQL Docs**    | Official PostgreSQL documentation        | [postgresql.org/docs](https://www.postgresql.org/docs/)                                                                    |
| **pg8000**             | Pure Python PostgreSQL driver            | [github.com/tlocke/pg8000](https://github.com/tlocke/pg8000)                                                               |
| **Connection Pooling** | PostgreSQL connection pooling strategies | [postgresql.org/docs/current/runtime-config-connection](https://www.postgresql.org/docs/current/runtime-config-connection) |
| **PgBouncer**          | Lightweight PostgreSQL pooler            | [pgbouncer.github.io](https://pgbouncer.github.io/)                                                                        |
| **EXPLAIN ANALYZE**    | Query optimization in PostgreSQL         | [postgresql.org/docs/current/sql-explain](https://www.postgresql.org/docs/current/sql-explain.html)                        |
