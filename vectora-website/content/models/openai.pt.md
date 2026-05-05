---
title: "OpenAI (GPT): LLM Alternativo"
slug: openai
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - gpt
  - langchain
  - llm
  - models
  - openai
  - vectora
draft: false
---

{{< lang-toggle >}}

O Vectora suporta OpenAI GPT como alternativa ao Claude. A troca de provedor é feita por configuração, sem alterar código — o LangChain abstrai a diferença de API.

## Modelos Suportados

| Modelo          | ID            | Uso Recomendado                               |
| --------------- | ------------- | --------------------------------------------- |
| **GPT-4o**      | `gpt-4o`      | Uso geral, melhor custo/performance da OpenAI |
| **GPT-4o mini** | `gpt-4o-mini` | Respostas rápidas, menor custo                |
| **GPT-4 Turbo** | `gpt-4-turbo` | Alternativa legada, contexto de 128K          |

## Configuração

```bash
vectora config set openai_api_key sk-...
vectora config set llm_provider openai
vectora config set llm_model gpt-4o
```

Variáveis de ambiente:

```bash
export OPENAI_API_KEY=sk-...
export VECTORA_LLM_PROVIDER=openai
export VECTORA_LLM_MODEL=gpt-4o
```

## Uso via LangChain

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)
```

O restante do pipeline (busca, reranking, contexto) permanece idêntico ao uso com Claude — apenas o LLM muda.

## API Compatível com OpenAI

O Vectora também suporta qualquer provedor com API compatível com OpenAI, como Ollama (local), Together AI, Groq, ou Azure OpenAI:

```bash
vectora config set llm_provider openai_compatible
vectora config set llm_base_url http://localhost:11434/v1  # Ollama
vectora config set llm_model llama3.2
vectora config set openai_api_key ollama  # valor dummy para Ollama
```

Isso possibilita uso 100% offline com modelos locais.

## Comparativo: Claude vs GPT-4o

|                    | Claude sonnet-4-6    | GPT-4o           |
| ------------------ | -------------------- | ---------------- |
| **Contexto**       | 200K tokens          | 128K tokens      |
| **Tool use**       | Nativo               | Nativo           |
| **Código**         | Excelente            | Excelente        |
| **Instrução**      | Alta fidelidade      | Alta fidelidade  |
| **Integração MCP** | Nativa (Claude Code) | Via servidor MCP |

Para a maioria dos casos, a diferença de qualidade é pequena. A escolha geralmente depende de preferência de custo ou da IDE que você usa.

## External Linking

| Conceito             | Recurso                               | Link                                                                                                              |
| -------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **OpenAI API**       | API reference                         | [platform.openai.com/docs](https://platform.openai.com/docs/)                                                     |
| **GPT-4o**           | Model details and pricing             | [platform.openai.com/docs/models/gpt-4o](https://platform.openai.com/docs/models/gpt-4o)                          |
| **LangChain OpenAI** | ChatOpenAI integration                | [python.langchain.com/docs/integrations/chat/openai](https://python.langchain.com/docs/integrations/chat/openai/) |
| **Ollama**           | Local LLM runtime (OpenAI-compatible) | [ollama.com](https://ollama.com/)                                                                                 |
