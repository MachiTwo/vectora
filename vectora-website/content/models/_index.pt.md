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

O Vectora combina três camadas de modelos com papéis distintos: um **LLM principal** (swappável) para raciocínio, **VoyageAI** (fixo) para embeddings e **XLM-RoBERTa** (local) para reranking. Cada camada tem sua responsabilidade e não pode ser substituída pela outra.

## LLM Principal (Swappável)

O LLM é o "cérebro de raciocínio" do Vectora — interpreta a query do usuário, decide quais ferramentas chamar e gera a resposta final com base no contexto recuperado. Você escolhe qual LLM usar:

| LLM                              | Provedor          | Recomendado para                      |
| -------------------------------- | ----------------- | ------------------------------------- |
| [Claude sonnet-4-6](./claude.md) | Anthropic         | Uso geral — melhor custo/performance  |
| [Claude opus-4-7](./claude.md)   | Anthropic         | Análise complexa, raciocínio profundo |
| [GPT-4o](./openai.md)            | OpenAI            | Alternativa de alta qualidade         |
| [Gemini 2.0 Flash](./gemini.md)  | Google            | Alto volume, custo baixo              |
| [Ollama (local)](./openai.md)    | OpenAI-compatible | Uso 100% offline                      |

A troca de LLM é feita por configuração — o pipeline de busca, reranking e contexto permanece idêntico.

## Embeddings (VoyageAI — Fixo no MVP)

VoyageAI é o provedor exclusivo de embeddings no Vectora. Não é swappável no MVP porque todos os vetores no LanceDB foram gerados com o mesmo modelo — trocar exigiria reindexar todo o codebase.

**[Ver documentação completa do VoyageAI](./voyage/)**

| Especificação    | Valor                       |
| ---------------- | --------------------------- |
| **Modelo**       | voyage-3-large              |
| **Dimensões**    | 1024D                       |
| **Preço**        | $0.10 / 2M tokens           |
| **Cache Redis**  | TTL 24h, < 1ms em cache hit |
| **Latência API** | ~200ms (sem cache)          |

## Reranking Local (XLM-RoBERTa)

XLM-RoBERTa-small roda localmente para reordenar os top-100 candidatos do LanceDB em top-10 por relevância semântica real. Zero chamadas de rede, inferência em CPU.

| Especificação   | Valor                          |
| --------------- | ------------------------------ |
| **Modelo**      | xlm-roberta-small              |
| **Quantização** | INT8 (< 120MB RAM)             |
| **Latência**    | < 10ms p99 para 100 candidatos |
| **Custo**       | Grátis (local)                 |

## Tabela Comparativa

| Componente                      | Local | Swappável | Custo           | Latência            |
| ------------------------------- | ----- | --------- | --------------- | ------------------- |
| **LLM (Claude / GPT / Gemini)** | Não   | Sim       | Por token       | 1-5s                |
| **Embeddings (VoyageAI)**       | Não   | Não (MVP) | $0.10/2M tokens | ~200ms / <1ms cache |
| **Reranking (XLM-RoBERTa)**     | Sim   | Não (MVP) | Grátis          | < 10ms              |

## Configuração Rápida

```bash
# LLM: escolha um dos três
vectora config set anthropic_api_key sk-ant-xxx   # Claude
vectora config set openai_api_key sk-xxx          # GPT-4o
vectora config set google_api_key AIza-xxx        # Gemini

# Embeddings: sempre necessário
vectora config set voyage_api_key sk-voyage-xxx

# Definir qual LLM usar
vectora config set llm_provider anthropic   # ou: openai, google
vectora config set llm_model claude-sonnet-4-6
```

## External Linking

| Conceito        | Recurso                                    | Link                                                                         |
| --------------- | ------------------------------------------ | ---------------------------------------------------------------------------- |
| **VoyageAI**    | Embeddings de alta performance para código | [voyageai.com](https://www.voyageai.com/)                                    |
| **XLM-RoBERTa** | Modelo multilíngue de código aberto        | [huggingface.co/xlm-roberta-small](https://huggingface.co/xlm-roberta-small) |
| **LangChain**   | Framework de orquestração LLM              | [python.langchain.com](https://python.langchain.com/)                        |
| **Anthropic**   | Claude API documentation                   | [docs.anthropic.com](https://docs.anthropic.com/)                            |
| **OpenAI**      | GPT API documentation                      | [platform.openai.com/docs](https://platform.openai.com/docs/)                |
