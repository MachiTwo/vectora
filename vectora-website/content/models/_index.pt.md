---
title: Modelos e Runtimes
slug: models
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - ai
  - architecture
  - concepts
  - embeddings
  - integration
  - models
  - privacy
  - pytorch
  - rag
  - reranker
  - vcr
  - vectora
  - voyage
---

{{< lang-toggle >}}

{{< section-toggle >}}

Vectora usa uma arquitetura de **modelos especializados**, cada um otimizado para uma tarefa específica: orquestração (LangChain), decisão tática (VCR), embeddings (VoyageAI) e reranking (XLM-RoBERTa). Todos os modelos rodam **localmente** — a inferência nunca sai da sua máquina.

## Vectora Cognitive Runtime (VCR)

O cérebro decisório local do Vectora. VCR roda em seu CPU usando PyTorch quantizado com XLM-RoBERTa-small + LoRA fine-tuning. Ele toma decisões sobre qual contexto buscar, como validar respostas e quando delegar a LLMs externos.

**Especificações:**

- **Modelo Base**: XLM-RoBERTa-small (110M parâmetros)
- **Fine-tuning**: LoRA adapters (< 2% de overhead)
- **Quantização**: INT8 (90% redução de memória)
- **Latência Target**: < 10ms p99 em CPU
- **Memória**: < 500MB RAM
- **Compatibilidade**: CPU-only (nenhuma GPU necessária)

**[Ver Arquitetura Detalhada](./vectora-cognitive-runtime.md)**

## Embeddings (VoyageAI)

VoyageAI fornece embeddings de alta performance para busca semântica. Resultados são cacheados em Redis para reduzir custos.

**Especificações:**

- **Modelo**: voyage-3-large
- **Dimensão**: 1024D
- **Taxa de Tokens**: ~2M tokens / $0.10
- **Cache**: Redis (TTL 24h)
- **Latência**: ~200ms (primeira requisição), <1ms (cached)

## Reranking Local (XLM-RoBERTa)

XLM-RoBERTa-small refina candidatos de busca com score de relevância local. Roda em CPU, < 10ms para 100 candidatos.

**Especificações:**

- **Modelo**: xlm-roberta-small
- **Tarefa**: Binary relevance classification
- **Latência**: < 10ms p99 para top-100 candidatos
- **Threshold**: Score > 0.65 considerado relevante

## Orchestração (LangChain + Deep Agents)

LangChain orquestra o fluxo de execução, gerenciando tools, prompts e memória. Deep Agents adiciona planejamento e execução multi-etapas.

**Specificações:**

- **Framework**: LangChain 0.1.0+
- **State Machine**: LangGraph
- **Memory**: Truncate/Delete/Summarize strategies
- **Tool Binding**: Automático via schema inspection

## Modelos Externos (Opcional)

Você pode opcionalmente integrar LLMs externos para raciocínio mais profundo:

- **claude-sonnet-4-6** (recomendado) — Melhor custo/performance
- **claude-opus-4-7** — Máxima capacidade de raciocínio
- **GPT-4o** — Alternativa OpenAI
- **Qualquer LLM via OpenAI-compatible API** — Suporte genérico

Vectora roda **sem** LLM externo — use VCR + Deep Agents localmente para maioria das tarefas.

## Tabela Comparativa

| Componente                  | Local | Caching     | Latência | Custo           |
| --------------------------- | ----- | ----------- | -------- | --------------- |
| **VCR (XLM-RoBERTa)**       | Sim   | Via memória | <10ms    | Grátis          |
| **Embeddings (VoyageAI)**   | Não   | Redis 24h   | 200ms    | $0.10/2M tokens |
| **Reranking (XLM-RoBERTa)** | Sim   | Via memória | <10ms    | Grátis          |
| **LLM Externo**             | Não   | Não         | 1-5s     | Por token       |

## Configuração

Por padrão, Vectora vem com:

- VCR ativado (local)
- VoyageAI embeddings (requer chave de API)
- XLM-RoBERTa reranking (local)
- Sem LLM externo

Para adicionar LLM externo:

```yaml
# .env ou vectora config
OPENAI_API_KEY=sk-...  # Para GPT-4, Claude 3, etc via OpenAI API
ANTHROPIC_API_KEY=sk-ant-...  # Para Claude nativo
```

## Recursos Relacionados

- [Vectora Cognitive Runtime — Arquitetura Detalhada](./vectora-cognitive-runtime.md)
- [VoyageAI Embeddings — Setup e Uso](../search/embeddings.md)
- [Context Engine — Como VCR valida contexto](../core/context-engine.md)
- [Deep Agents — Planejamento e orquestração](../core/agentic-framework.md)

## External Linking

| Conceito        | Recurso                              | Link                                                                         |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| **XLM-RoBERTa** | Modelo multilíngue de código aberto  | [huggingface.co/xlm-roberta-small](https://huggingface.co/xlm-roberta-small) |
| **PyTorch**     | Framework de deep learning           | [pytorch.org](https://pytorch.org/)                                          |
| **LoRA**        | Low-Rank Adaptation para fine-tuning | [arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)                 |
| **VoyageAI**    | Embeddings de alta performance       | [voyageai.com](https://www.voyageai.com/)                                    |
| **LangChain**   | Framework de orquestração LLM        | [python.langchain.com/docs](https://python.langchain.com/docs)               |
