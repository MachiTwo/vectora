---
title: "Troubleshooting: Diagnóstico e Resolução de Problemas"
slug: troubleshooting
date: "2026-05-04T10:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - debug
  - docker
  - embeddings
  - jwt
  - lancedb
  - postgresql
  - redis
  - troubleshooting
  - vectora
  - vcr
draft: false
---

{{< lang-toggle >}}

{{< section-toggle >}}

Guia de diagnóstico para os problemas mais comuns do Vectora: erros de autenticação, falhas de embedding, lentidão no pipeline e problemas de infraestrutura.

## Erros de Autenticação

### `401 Unauthorized` em todas as rotas

O token JWT está ausente, expirado ou malformado. Verifique:

```bash
# Inspecionar o token
vectora auth token --show

# Regenerar token
vectora auth login --email admin@empresa.com
```

Se o token for válido mas a rota retornar 401, o `jti` pode ter sido revogado:

```sql
-- Checar se o token foi revogado
SELECT revoked_at FROM sessions WHERE token_id = '<jti>';
```

### `403 Forbidden` com token válido

O usuário não tem permissão para a operação. Verifique o role:

```bash
vectora admin list-users --email usuario@empresa.com
# Role atual vs permissão necessária

# Promover role (requer superadmin)
vectora admin set-role --email usuario@empresa.com --role operator
```

### Token expira muito rápido

Access tokens têm TTL de 1 hora por design. Use refresh tokens para sessões longas:

```bash
# Configurar refresh automático
vectora config set auto_refresh true
```

## Erros de Embedding e Busca

### `VoyageAIError: invalid api key`

```bash
# Verificar chave configurada
vectora config get voyage_api_key

# Reconfigurar
vectora config set voyage_api_key sk-voyage-xxx
```

### Busca retorna zero resultados

Causas prováveis:

1. **Namespace vazio** — o codebase não foi indexado ainda:

```bash
vectora index status
# Se chunks = 0, indexe primeiro:
vectora index . --namespace meu-projeto
```

2. **Namespace errado** — a query usa namespace diferente do índice:

```bash
vectora search "jwt validation" --namespace src/auth
# vs o namespace correto do índice
vectora index status --namespace src/auth
```

3. **LanceDB corrompido** — tente reindexar:

```bash
vectora index drop --namespace meu-projeto
vectora index . --namespace meu-projeto
```

### Indexação trava em um arquivo específico

O arquivo pode ter encoding incomum ou ser muito grande. Use `--exclude` para isolar:

```bash
vectora index . --namespace projeto --exclude "**/*.min.js" --exclude "**/vendor/**"
```

Para depurar qual arquivo causa o travamento:

```bash
vectora index . --namespace projeto --verbose 2>&1 | tail -20
```

### Latência de busca acima de 500ms

| Sintoma             | Causa provável            | Solução                      |
| ------------------- | ------------------------- | ---------------------------- |
| Embed sempre ~200ms | Cache Redis ausente       | `docker compose up -d redis` |
| Search >50ms        | Índice HNSW não criado    | `vectora index rebuild`      |
| Rerank >50ms        | Modelo VCR em CPU lento   | Verificar `OMP_NUM_THREADS`  |
| Total >1s           | Todas as etapas sem cache | Redis + índice HNSW          |

## Erros de VCR (Vectora Cognitive Runtime)

### `VCRError: model file not found`

O modelo XLM-RoBERTa não foi baixado ainda:

```bash
# Baixar modelo
vectora vcr download

# Verificar integridade
vectora vcr status
# Expected: model=ok, quantized=true, latency_p99=<10ms
```

### Faithfulness validation falha (score < 0.70)

O VCR está rejeitando contexto por baixa fidelidade. Isso é comportamento esperado quando os resultados de busca são pouco relevantes. Verifique a qualidade do índice:

```bash
# Inspecionar scores de um resultado
vectora search "minha query" --verbose
# Olhar faithfulness_score no output JSON
```

Se o score for consistentemente < 0.70, o namespace pode precisar de reindexação com chunks menores:

```bash
vectora config set chunk_size 256  # padrão: 512
vectora index drop --namespace meu-projeto
vectora index . --namespace meu-projeto
```

### `RuntimeError: CUDA out of memory`

O VCR usa CPU por padrão. Se você forçou GPU e a VRAM está esgotada:

```bash
vectora config set vcr_device cpu
```

## Erros de Infraestrutura

### PostgreSQL não conecta

```bash
# Verificar se o container está rodando
docker compose ps postgres

# Ver logs
docker compose logs postgres --tail=20

# Testar conexão direta
docker exec -it vectora-postgres psql -U vectora -d vectora -c "SELECT 1"
```

Erro comum: `FATAL: database "vectora" does not exist` — rode as migrations:

```bash
vectora db migrate
```

### Redis não conecta

```bash
# Verificar container
docker compose ps redis
docker compose logs redis --tail=10

# Testar conexão
docker exec -it vectora-redis redis-cli ping
# Esperado: PONG
```

Se Redis não estiver disponível, o Vectora opera sem cache (com penalidade de latência). Não é erro fatal, apenas warning:

```text
[WARNING] Redis unavailable, cache disabled. Embedding calls will be uncached.
```

### LanceDB: `OSError: No space left on device`

O banco vetorial cresceu além do espaço disponível:

```bash
# Ver tamanho do banco
vectora index status --all
du -sh ~/.vectora/lancedb/

# Remover namespaces não utilizados
vectora index drop --namespace projeto-antigo
```

## Diagnóstico com Logs

### Ativar logs detalhados

```bash
# Nível DEBUG
vectora serve --log-level debug

# Ou via variável de ambiente
VECTORA_LOG_LEVEL=debug vectora serve
```

### Formato dos logs (JSON estruturado)

```json
{
  "timestamp": "2026-05-04T10:30:00Z",
  "level": "ERROR",
  "event": "embedding_failed",
  "error": "VoyageAI timeout after 5000ms",
  "query_hash": "sha256:abc123",
  "namespace": "src/auth"
}
```

### Arquivos de log

| Arquivo            | Conteúdo                            |
| ------------------ | ----------------------------------- |
| `logs/vectora.log` | Log geral da aplicação              |
| `logs/mcp.log`     | Tráfego MCP (requisições/respostas) |
| `logs/vcr.log`     | Scores VCR, faithfulness, latências |
| `logs/auth.log`    | Login, logout, tokens revogados     |

### Health Check

```bash
# Status completo de todos os componentes
vectora health

# Saída esperada
# postgres: ok (latency: 2ms)
# redis: ok (latency: 0.4ms)
# lancedb: ok (chunks: 12450, namespaces: 3)
# vcr: ok (model: xlm-roberta-small-int8, p99: 8.2ms)
# voyage: ok (quota: 1.8M/2M tokens)
```

## External Linking

| Conceito                    | Recurso                      | Link                                                                                          |
| --------------------------- | ---------------------------- | --------------------------------------------------------------------------------------------- |
| **LanceDB Troubleshooting** | LanceDB common issues        | [lancedb.com/docs](https://lancedb.com/docs)                                                  |
| **pytest Debug**            | pytest debugging guide       | [docs.pytest.org/how-to/failures](https://docs.pytest.org/en/stable/how-to/failures.html)     |
| **Docker Compose**          | Docker Compose CLI reference | [docs.docker.com/compose/reference](https://docs.docker.com/compose/reference/)               |
| **VoyageAI Status**         | VoyageAI service status      | [voyageai.com](https://www.voyageai.com/)                                                     |
| **Redis Diagnostics**       | Redis troubleshooting guide  | [redis.io/docs/management/troubleshooting](https://redis.io/docs/management/troubleshooting/) |
