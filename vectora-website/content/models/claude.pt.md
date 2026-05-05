---
title: "Claude (Anthropic): LLM Principal Recomendado"
slug: claude
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - anthropic
  - claude
  - langchain
  - llm
  - models
  - vectora
draft: false
---

{{< lang-toggle >}}

O Vectora usa um LLM externo como "cérebro de raciocínio" — responsável por interpretar queries, gerar respostas e orquestrar ferramentas. Claude é a escolha recomendada por sua performance em tarefas de código, capacidade de raciocínio longo e integração nativa com Claude Code via MCP.

## Modelos Disponíveis

| Modelo                | ID                          | Uso Recomendado                        | Custo relativo |
| --------------------- | --------------------------- | -------------------------------------- | -------------- |
| **claude-sonnet-4-6** | `claude-sonnet-4-6`         | Uso geral, melhor custo/performance    | Médio          |
| **claude-opus-4-7**   | `claude-opus-4-7`           | Tarefas complexas, raciocínio profundo | Alto           |
| **claude-haiku-4-5**  | `claude-haiku-4-5-20251001` | Respostas rápidas, tarefas simples     | Baixo          |

O padrão do Vectora é `claude-sonnet-4-6` quando a chave Anthropic está configurada.

## Configuração

```bash
vectora config set anthropic_api_key sk-ant-xxx
vectora config set llm_provider anthropic
vectora config set llm_model claude-sonnet-4-6
```

Variáveis de ambiente:

```bash
export ANTHROPIC_API_KEY=sk-ant-xxx
export VECTORA_LLM_PROVIDER=anthropic
export VECTORA_LLM_MODEL=claude-sonnet-4-6
```

## Uso via LangChain

O Vectora instancia Claude via `ChatAnthropic` do LangChain:

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    max_tokens=4096,
    temperature=0,
)

# Uso com contexto do Vectora
messages = [
    SystemMessage(content="Você é um assistente de código. Use o contexto fornecido."),
    HumanMessage(content=f"Contexto:\n{vectora_context}\n\nPergunta: {user_query}"),
]

response = llm.invoke(messages)
```

## Streaming

Claude suporta streaming de resposta, exposto pelo Vectora via SSE:

```python
async for chunk in llm.astream(messages):
    yield chunk.content
```

O endpoint `/api/v1/agent/stream/{id}` usa este mecanismo internamente.

## Por que Claude como Padrão

- **Contexto longo**: Claude processa até 200K tokens — ideal para codebases grandes
- **Instrução precisa**: Segue instruções de sistema com alta fidelidade
- **Claude Code**: Integração nativa via MCP — o próprio Claude Code pode chamar o Vectora como ferramenta
- **Tool use**: Suporte robusto a function calling para orquestração LangGraph

## Comparativo de Modelos Claude

|                 | claude-haiku-4-5  | claude-sonnet-4-6 | claude-opus-4-7  |
| --------------- | ----------------- | ----------------- | ---------------- |
| **Velocidade**  | Mais rápido       | Balanceado        | Mais lento       |
| **Raciocínio**  | Básico            | Avançado          | Máximo           |
| **Contexto**    | 200K tokens       | 200K tokens       | 200K tokens      |
| **Melhor para** | Respostas simples | Uso geral         | Análise complexa |

## External Linking

| Conceito                | Recurso                       | Link                                                                                                                    |
| ----------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Anthropic Docs**      | Claude API documentation      | [docs.anthropic.com](https://docs.anthropic.com/)                                                                       |
| **Claude Models**       | Model comparison and pricing  | [docs.anthropic.com/models](https://docs.anthropic.com/en/docs/about-claude/models/overview)                            |
| **LangChain Anthropic** | ChatAnthropic integration     | [python.langchain.com/docs/integrations/chat/anthropic](https://python.langchain.com/docs/integrations/chat/anthropic/) |
| **Claude Code**         | Claude Code CLI documentation | [docs.anthropic.com/claude-code](https://docs.anthropic.com/en/docs/claude-code/overview)                               |
