---
title: "Gemini (Google): LLM Alternativo"
slug: gemini
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - gemini
  - google
  - langchain
  - llm
  - models
  - vectora
draft: false
---

{{< lang-toggle >}}

O Vectora suporta Gemini como alternativa de LLM. Gemini não é usado para embeddings — essa função é exclusiva do VoyageAI. Gemini atua apenas como o "cérebro de raciocínio" que interpreta queries e gera respostas com base no contexto recuperado pelo Vectora.

## Modelos Suportados

| Modelo               | ID                 | Uso Recomendado                             |
| -------------------- | ------------------ | ------------------------------------------- |
| **Gemini 2.0 Flash** | `gemini-2.0-flash` | Melhor custo/performance, respostas rápidas |
| **Gemini 2.5 Pro**   | `gemini-2.5-pro`   | Raciocínio mais profundo, contexto longo    |
| **Gemini 1.5 Flash** | `gemini-1.5-flash` | Alternativa mais barata                     |

## Configuração

```bash
vectora config set google_api_key AIza...
vectora config set llm_provider google
vectora config set llm_model gemini-2.0-flash
```

Variáveis de ambiente:

```bash
export GOOGLE_API_KEY=AIza...
export VECTORA_LLM_PROVIDER=google
export VECTORA_LLM_MODEL=gemini-2.0-flash
```

## Uso via LangChain

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)
```

O restante do pipeline do Vectora (busca VoyageAI + LanceDB, reranking XLM-RoBERTa, compactação de contexto) permanece idêntico — apenas o LLM muda.

## Gemini e Embeddings

É importante notar que o Vectora **não usa** a API de embeddings do Google (text-embedding-004 ou Gemini Embedding). Os embeddings são sempre gerados pelo VoyageAI voyage-4, independentemente de qual LLM está configurado.

Isso garante consistência do índice LanceDB: todos os vetores usam o mesmo modelo, independente da troca de LLM.

## Comparativo: Claude vs GPT-4o vs Gemini

|                    | Claude sonnet-4-6    | GPT-4o      | Gemini 2.0 Flash |
| ------------------ | -------------------- | ----------- | ---------------- |
| **Contexto**       | 200K tokens          | 128K tokens | 1M tokens        |
| **Tool use**       | Nativo               | Nativo      | Nativo           |
| **Código**         | Excelente            | Excelente   | Bom              |
| **Velocidade**     | Rápido               | Rápido      | Muito rápido     |
| **Integração MCP** | Nativa (Claude Code) | Via MCP     | Via MCP          |
| **Preço**          | Médio                | Médio       | Baixo            |

Gemini 2.0 Flash é uma boa escolha para workflows de alto volume onde custo é crítico. Para qualidade máxima em análise de código, Claude ou GPT-4o tendem a ser superiores.

## External Linking

| Conceito             | Recurso                            | Link                                                                                                                                          |
| -------------------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Gemini API**       | Google AI API documentation        | [ai.google.dev/docs](https://ai.google.dev/docs)                                                                                              |
| **Gemini Models**    | Model overview and pricing         | [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)                                                          |
| **LangChain Google** | ChatGoogleGenerativeAI integration | [python.langchain.com/docs/integrations/chat/google_generative_ai](https://python.langchain.com/docs/integrations/chat/google_generative_ai/) |
| **Google AI Studio** | Testar Gemini no browser           | [aistudio.google.com](https://aistudio.google.com/)                                                                                           |
