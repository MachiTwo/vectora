---
title: "Reranking: Conceitos e Arquitetura"
slug: reranker
date: "2026-05-03T22:30:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - ai
  - architecture
  - concepts
  - cross-encoder
  - embeddings
  - rag
  - reranker
  - semantic-search
  - vector-search
  - vectora
  - xlm-roberta
---

{{< lang-toggle >}}

{{< section-toggle >}}

Reranking é a etapa que transforma os top-100 candidatos retornados pela busca vetorial em top-10 verdadeiramente relevantes. O Vectora usa XLM-RoBERTa-small como reranker local — roda em CPU, sem custo de API, latência menor que 10ms.

## O Problema da Busca Vetorial Pura

Busca vetorial com HNSW é extremamente eficiente para encontrar candidatos similares, mas usa um atalho: cada documento é convertido em vetor independentemente da query. Isso significa que a busca é feita em dois passos separados.

Para uma query como "Como cancelar assinatura?", a busca vetorial pode retornar:

```text
1. src/billing/cancel.py       (score: 0.91) <- correto
2. src/billing/subscription.py (score: 0.89) <- parcialmente relevante
3. src/auth/session.py         (score: 0.87) <- irrelevante
4. docs/billing.md             (score: 0.86) <- genérico
5. src/billing/refund.py       (score: 0.85) <- irrelevante
... e mais 95 candidatos
```

O problema: todos parecem "similares", mas não necessariamente relevantes para a query específica.

## Bi-Encoder vs Cross-Encoder

A diferença fundamental entre busca vetorial e reranking está na arquitetura dos modelos.

### Bi-Encoder (Busca Vetorial)

```text
Query  -> Encoder -> vetor_q [0.12, -0.45, 0.89, ...]
Doc_1  -> Encoder -> vetor_1 [0.11, -0.46, 0.88, ...]
Doc_2  -> Encoder -> vetor_2 [0.05,  0.23, 0.11, ...]

Similaridade = cosine(vetor_q, vetor_i)
```

Vantagens: rápido, escalável para milhões de documentos, pré-computa vetores.
Limitação: query e documento nunca interagem diretamente — o modelo não vê a combinação.

### Cross-Encoder (Reranking)

```text
Input: [CLS] query [SEP] documento [SEP]
       -> Transformer com atenção completa
       -> Score de relevância: 0.0 a 1.0
```

O cross-encoder processa query e documento simultaneamente. A atenção pode capturar relações sutis entre os dois textos — detecta quando um documento menciona o conceito mas não responde a pergunta.

Limitação: lento para bases grandes. Por isso é usado apenas nos top-100 candidatos pré-filtrados.

## O Pipeline Completo

```text
Query
  |
  +-> VoyageAI embed -> vetor 1024D
  |
  +-> LanceDB HNSW -> top-100 candidatos (< 50ms)
  |
  +-> XLM-RoBERTa cross-encoder -> score por candidato (< 10ms)
  |
  +-> top-10 ordenados por relevância
  |
  +-> Compactação + VCR validation
  |
  +-> Contexto final para o LLM
```

Cada etapa filtra candidatos com base em critérios progressivamente mais precisos. O custo computacional aumenta a cada etapa, mas o volume de dados diminui proporcionalmente.

## Por Que XLM-RoBERTa Local

O Vectora usa XLM-RoBERTa-small como reranker local, parte do VCR (Vectora Cognitive Runtime). A escolha prioriza privacidade e custo zero:

| Critério            | XLM-RoBERTa (local) | Voyage Rerank (API)     |
| ------------------- | ------------------- | ----------------------- |
| **Latência**        | < 10ms              | 50-150ms                |
| **Custo**           | Grátis              | $2/1M tokens            |
| **Privacidade**     | Dados locais        | Dados enviados para API |
| **Disponibilidade** | Sempre (offline)    | Depende de internet     |
| **Customização**    | Fine-tuning LoRA    | Sem customização        |

XLM-RoBERTa-small tem 117M parâmetros e suporta 100+ idiomas nativamente, incluindo código.

## Impacto no Contexto do LLM

O reranking reduz drasticamente o volume de contexto enviado ao LLM:

| Etapa           | Candidatos     | Tokens (estimado) |
| --------------- | -------------- | ----------------- |
| Pós HNSW        | 100            | ~50.000           |
| Pós reranking   | 10             | ~5.000            |
| Pós compactação | 10 (truncados) | ~2.000            |

Menos contexto significa menos custo no LLM, menor latência de geração, e menor risco de o modelo se perder em informação irrelevante.

## Métricas de Qualidade

O reranker é avaliado por NDCG@10 (Normalized Discounted Cumulative Gain): mede se os documentos mais relevantes aparecem no topo da lista.

```text
Ranking perfeito (relevantes no topo): NDCG@10 = 1.0
Ranking aleatório:                     NDCG@10 ~ 0.5
XLM-RoBERTa-small (target do VCR):    NDCG@10 >= 0.80
```

A implementação detalhada do reranker local — incluindo código, configuração e fine-tuning — está documentada em [Reranker Local](./reranker-local.md).

## External Linking

| Conceito          | Recurso                                | Link                                                                                                         |
| ----------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **XLM-RoBERTa**   | Multilingual pre-trained model         | [huggingface.co/xlm-roberta-small](https://huggingface.co/xlm-roberta-small)                                 |
| **Cross-Encoder** | Sentence Transformers cross-encoders   | [sbert.net/docs/cross_encoder/usage](https://www.sbert.net/docs/cross_encoder/usage/usage.html)              |
| **NDCG**          | Normalized Discounted Cumulative Gain  | [en.wikipedia.org/wiki/Discounted_cumulative_gain](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) |
| **RAG**           | Retrieval-Augmented Generation         | [arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)                                                 |
| **HNSW**          | Efficient approximate nearest neighbor | [arxiv.org/abs/1603.09320](https://arxiv.org/abs/1603.09320)                                                 |
