---
title: "FAQ: Perguntas Frequentes"
slug: faq
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - auth
  - embeddings
  - faq
  - lancedb
  - performance
  - privacy
  - vectora
draft: false
---

{{< lang-toggle >}}

{{< section-toggle >}}

Respostas às perguntas mais comuns sobre instalação, busca semântica, performance e privacidade do Vectora.

## Instalação e Setup

### Como instalar o Vectora?

```bash
uv tool install vectora
```

Requer Python 3.12+ e `uv`. Após instalar, configure a chave VoyageAI:

```bash
vectora config set voyage_api_key sk-voyage-xxx
```

### O Vectora funciona offline?

Parcialmente. Busca vetorial (LanceDB) e reranking (XLM-RoBERTa) rodam 100% local. A geração de embeddings exige VoyageAI API — sem conexão, embeddings novos não são gerados (mas queries já cacheadas no Redis funcionam). Para modo completamente offline, configure `embedding_provider=local` (experimental).

### Preciso do Docker?

Não, mas é recomendado para PostgreSQL e Redis. Em modo local simples, o Vectora usa SQLite como fallback. Docker facilita o setup da infraestrutura:

```bash
docker compose up -d postgres redis
```

## Busca e Embeddings

### Por que a busca retorna resultados sem as palavras que digitei?

Porque o Vectora usa busca semântica, não por palavras-chave. "Segurança" traz resultados de `validate_token`, `bcrypt`, `jwt_verify` — mesmo sem essas palavras na query. O VoyageAI voyage-4 entende o significado do código, não apenas os tokens.

### Como limitar a busca a um diretório específico?

```bash
vectora search "validar JWT" --namespace src/auth
```

Via API:

```json
{
  "query": "validar JWT",
  "filters": { "namespace": "src/auth" }
}
```

### Quantos arquivos o Vectora consegue indexar?

LanceDB suporta até ~50M chunks eficientemente. Um projeto típico de 500K linhas de código gera ~10K-50K chunks. Performance de busca permanece < 50ms nessa escala.

### Por que meu codebase demora para indexar na primeira vez?

O tempo de indexação depende do número de arquivos e da latência VoyageAI. Chunks são enviados em batches de 128 — para 10K chunks, espere 2-5 minutos. Indexações subsequentes são incrementais.

## Performance e Latência

### Qual a latência esperada por query?

| Etapa             | Latência    |
| ----------------- | ----------- |
| Embed (cached)    | < 1ms       |
| Embed (API)       | ~200ms      |
| Vector Search     | < 50ms      |
| Reranking         | < 10ms      |
| Total (cache hit) | < 100ms     |
| Total (sem cache) | < 500ms p95 |

### O Redis é obrigatório?

Não, mas altamente recomendado. Sem Redis, cada query chama VoyageAI mesmo para queries repetidas — aumentando latência e custo. Com Redis (TTL 24h), queries repetidas custam < 1ms.

## Autenticação e RBAC

### Como criar o primeiro usuário admin?

```bash
vectora admin create-user --email admin@empresa.com --role superadmin
```

### Qual a diferença entre roles?

| Role         | Acesso                        |
| ------------ | ----------------------------- |
| `viewer`     | Apenas leitura de resultados  |
| `developer`  | Busca + execução de agente    |
| `operator`   | Developer + indexação         |
| `admin`      | Operator + gestão de usuários |
| `superadmin` | Admin + configuração global   |

## Privacidade

### O meu código é enviado para servidores externos?

O texto dos chunks é enviado para VoyageAI para gerar embeddings. Os vetores resultantes ficam localmente no LanceDB. Se usar um LLM externo (Claude, GPT-4), os top-10 chunks relevantes são enviados — nunca o codebase inteiro. Para uso 100% offline, configure `embedding_provider=local`.

### Posso usar o Vectora em projetos confidenciais?

Sim, com cuidado. Revise a política de privacidade do VoyageAI e do LLM que você usa. O Vectora em si não coleta dados de uso. Para máxima privacidade, use modo offline + LLM local (Ollama).

## External Linking

| Conceito              | Recurso                  | Link                                                       |
| --------------------- | ------------------------ | ---------------------------------------------------------- |
| **VoyageAI Privacy**  | Voyage AI privacy policy | [voyageai.com/privacy](https://www.voyageai.com/privacy/)  |
| **uv**                | Python package manager   | [docs.astral.sh/uv](https://docs.astral.sh/uv/)            |
| **LanceDB**           | Vector database docs     | [lancedb.com/docs](https://lancedb.com/docs)               |
| **Anthropic Privacy** | Claude data policy       | [anthropic.com/privacy](https://www.anthropic.com/privacy) |
