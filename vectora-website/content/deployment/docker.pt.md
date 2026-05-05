---
title: "Docker & Docker Compose"
slug: docker
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - compose
  - containerization
  - deployment
  - docker
  - vectora
---

{{< lang-toggle >}}

Docker Compose simplifica deployment de Vectora com PostgreSQL, Redis e LanceDB em um único comando. Ideal para VPS ou desenvolvimento local com todas as dependências.

## Docker Compose (Recomendado)

Crie um arquivo `docker-compose.yml`:

```yaml
version: "3.8"

services:
  # Vectora backend
  vectora:
    image: anthropics/vectora:latest
    container_name: vectora
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: "postgresql://vectora:vectora@postgres:5432/vectora"
      REDIS_HOST: "redis"
      REDIS_PORT: 6379
      LANCEDB_PATH: "/data/lancedb"
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      VOYAGE_API_KEY: ${VOYAGE_API_KEY}
      LLM_PROVIDER: "anthropic"
      LLM_MODEL: "claude-sonnet-4-6"
    depends_on:
      - postgres
      - redis
    volumes:
      - vectora-data:/data
    networks:
      - vectora-net
    restart: unless-stopped

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: vectora-postgres
    environment:
      POSTGRES_USER: vectora
      POSTGRES_PASSWORD: vectora
      POSTGRES_DB: vectora
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - vectora-net
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vectora"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: vectora-redis
    volumes:
      - redis-data:/data
    networks:
      - vectora-net
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: vectora-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl/:/etc/nginx/ssl/:ro
    depends_on:
      - vectora
    networks:
      - vectora-net
    restart: unless-stopped

volumes:
  vectora-data:
  postgres-data:
  redis-data:

networks:
  vectora-net:
    driver: bridge
```

## Setup Inicial

### 1. Preparar Variáveis de Ambiente

Crie `.env` na mesma pasta do `docker-compose.yml`:

```bash
ANTHROPIC_API_KEY=sk-ant-xxx
VOYAGE_API_KEY=sk-voyage-xxx
LLM_MODEL=claude-sonnet-4-6
```

### 2. Iniciar Stack

```bash
docker-compose up -d

# Aguardar inicialização
docker-compose logs -f vectora
# Espere por "Application startup complete"
```

### 3. Verificar Saúde

```bash
curl http://localhost:8000/health
# {"status": "ok", "services": {...}}
```

### 4. Indexar Repositório

```bash
# Executar comando dentro do container
docker-compose exec vectora vectora index add /repo --name "my-repo"

# Ou copiar repo para volume e indexar
docker cp ./my-repo vectora-container:/data/repos/
docker-compose exec vectora vectora index add /data/repos/my-repo
```

## Dockerfile Personalizado

Se precisar customizar a imagem:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar Vectora
RUN pip install vectora

# Criar diretórios
RUN mkdir -p /data/lancedb

# Configurar
COPY ./config.yaml /app/
ENV LANCEDB_PATH=/data/lancedb

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Iniciar
CMD ["vectora", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

Buildar imagem:

```bash
docker build -t vectora-custom .
```

E usar em `docker-compose.yml`:

```yaml
services:
  vectora:
    image: vectora-custom # Em vez de anthropics/vectora:latest
```

## Nginx Reverse Proxy

Arquivo `nginx.conf` para HTTPS/SSL:

```nginx
upstream vectora {
    server vectora:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://vectora;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Streaming
        proxy_buffering off;
        proxy_request_buffering off;
    }

    location /health {
        proxy_pass http://vectora/health;
        access_log off;
    }
}
```

Gerar certificado SSL (auto-assinado):

```bash
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes
```

## Gerenciamento

### Ver logs

```bash
docker-compose logs -f vectora
docker-compose logs -f postgres
```

### Pausar stack

```bash
docker-compose down
# Dados persistem em volumes
```

### Remover tudo (cuidado!)

```bash
docker-compose down -v
# -v remove volumes também (DELETA DADOS!)
```

### Backup de dados

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U vectora vectora > backup.sql

# Backup volumes
docker run --rm -v vectora-data:/data -v $(pwd):/backup alpine tar czf /backup/lancedb.tar.gz /data/

# Restore
docker-compose exec postgres psql -U vectora < backup.sql
```

## Troubleshooting

### Container não inicia

```bash
docker-compose logs vectora
# Verificar erro específico
```

### Conexão PostgreSQL recusada

```bash
docker-compose ps
# Verificar se postgres está running

docker-compose exec postgres psql -U vectora -c "SELECT 1"
# Testar conexão diretamente
```

### Redis não conecta

```bash
docker-compose exec redis redis-cli ping
# PONG = ok
```

### Sem espaço em disco

```bash
docker system prune -a
docker volume prune
# Remove images/volumes não usados
```

## Performance em Produção

Para produção, ajuste:

```yaml
services:
  vectora:
    # ...
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 4G
        reservations:
          cpus: "1"
          memory: 2G

  postgres:
    environment:
      POSTGRES_INITDB_ARGS: >
        -c shared_buffers=256MB
        -c effective_cache_size=1GB
        -c maintenance_work_mem=64MB

  redis:
    command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

## External Linking

| Conceito              | Recurso                      | Link                                                            |
| --------------------- | ---------------------------- | --------------------------------------------------------------- |
| **Docker Compose**    | Official documentation       | [docs.docker.com/compose](https://docs.docker.com/compose/)     |
| **Docker Hub**        | Pre-built images             | [hub.docker.com](https://hub.docker.com/)                       |
| **Nginx**             | Web server and reverse proxy | [nginx.org/docs](https://nginx.org/en/docs/)                    |
| **PostgreSQL Docker** | Official PostgreSQL image    | [hub.docker.com/\_/postgres](https://hub.docker.com/_/postgres) |
| **Redis Docker**      | Official Redis image         | [hub.docker.com/\_/redis](https://hub.docker.com/_/redis)       |
