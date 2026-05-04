---
title: "FastAPI + LangChain: Integração no Backend Vectora"
slug: fastapi-integration
date: "2026-05-03T14:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - fastapi
  - langchain
  - backend
  - integration
  - python
  - rest-api
  - deep-agents
  - vectora
  - architecture
---

{{< lang-toggle >}}

{{< section-toggle >}}

O backend do Vectora usa FastAPI como camada de API REST e LangChain como motor de orquestração de agentes. FastAPI expõe endpoints HTTP; LangChain gerencia chains, tools e memória dos agentes. Esta página explica como os dois se integram no backend do Vectora.

## Arquitetura de Integração

```text
Cliente (REST / MCP / JSON-RPC)
    |
    +-> FastAPI Router
        |
        +-> Pydantic Validation (request/response)
        |
        +-> LangChain Agent Executor
            |
            +-> Tool Registry (ferramentas disponíveis)
            |
            +-> Context Engine (busca LanceDB)
            |
            +-> VCR (validação PyTorch)
            |
            +-> LLM externo (opcional)
            |
            +-> Response
```

FastAPI gerencia HTTP, autenticação e serialização. LangChain gerencia a lógica de agente, ferramentas e memória.

## Estrutura do Projeto

```text
vectora/
  api/
    main.py          — FastAPI app principal
    routers/
      agent.py       — Endpoints do agente
      search.py      — Endpoints de busca
      vcr.py         — Endpoints do VCR
  agents/
    executor.py      — LangChain AgentExecutor
    tools.py         — Tool definitions (LangChain tools)
    memory.py        — Memory strategies
  chains/
    rag_chain.py     — RAG pipeline chain
    planning.py      — Planning chain (Deep Agents)
```

## FastAPI App Principal

```python
# vectora/api/main.py
from fastapi import FastAPI
from vectora.api.routers import agent, search, vcr
from vectora.agents.executor import VectoraAgentExecutor

app = FastAPI(
    title="Vectora API",
    version="0.1.0",
    description="Hub de Conhecimento Local-First"
)

app.include_router(agent.router, prefix="/api/v1/agent", tags=["agent"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(vcr.router, prefix="/vcr", tags=["vcr"])

@app.get("/health")
async def health() -> dict:
    return {"status": "healthy"}
```

## Endpoint de Agente com LangChain

```python
# vectora/api/routers/agent.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from vectora.agents.executor import VectoraAgentExecutor
from vectora.api.auth import get_current_user

router = APIRouter()

class AgentRequest(BaseModel):
    query: str
    context_strategy: str = "auto"
    max_iterations: int = 5

class AgentResponse(BaseModel):
    result: str
    steps: list[dict]
    metadata: dict

@router.post("/run", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    user = Depends(get_current_user),
    executor: VectoraAgentExecutor = Depends(),
) -> AgentResponse:
    result = await executor.arun(
        query=request.query,
        context_strategy=request.context_strategy,
        max_iterations=request.max_iterations,
    )
    return AgentResponse(**result)
```

## AgentExecutor com LangChain

```python
# vectora/agents/executor.py
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate
from vectora.agents.tools import get_vectora_tools
from vectora.agents.memory import get_memory_strategy

class VectoraAgentExecutor:

    def __init__(self, llm, vcr, context_engine):
        self.llm = llm
        self.vcr = vcr
        self.context_engine = context_engine
        self.tools = get_vectora_tools(context_engine)

    async def arun(self, query: str, **kwargs) -> dict:
        # 1. VCR valida a query antes de planejar
        vcr_decision = await self.vcr.validate_plan(query=query)
        if vcr_decision["confidence"] < 0.5:
            return {"result": "Query inválida", "steps": [], "metadata": vcr_decision}

        # 2. LangChain cria e executa o agente
        prompt = ChatPromptTemplate.from_template(
            "Você é um assistente especialista. Responda: {query}"
        )
        agent = create_structured_chat_agent(self.llm, self.tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            max_iterations=kwargs.get("max_iterations", 5),
            verbose=True,
        )

        # 3. Executar com memória de sessão
        memory = get_memory_strategy(strategy="summarize")
        result = await executor.ainvoke(
            {"query": query, "chat_history": memory.load_memory_variables({})["history"]}
        )

        # 4. VCR valida a resposta
        validation = await self.vcr.validate_response(
            response=result["output"],
            context=result.get("intermediate_steps", []),
        )

        return {
            "result": result["output"],
            "steps": result.get("intermediate_steps", []),
            "metadata": {"vcr_validation": validation}
        }
```

## Tool Definitions

LangChain Tools são funções decoradas que o agente pode chamar:

```python
# vectora/agents/tools.py
from langchain.tools import tool
from vectora.search.engine import ContextEngine

def get_vectora_tools(context_engine: ContextEngine) -> list:

    @tool
    async def search_codebase(query: str, top_k: int = 10) -> str:
        """Busca semântica no codebase usando LanceDB e VoyageAI."""
        results = await context_engine.search(query=query, top_k=top_k)
        return "\n".join([f"{r['file']}: {r['content'][:200]}" for r in results])

    @tool
    async def get_file_content(file_path: str) -> str:
        """Retorna o conteúdo completo de um arquivo do codebase."""
        with open(file_path) as f:
            return f.read()

    @tool
    async def find_symbol_usages(symbol: str) -> str:
        """Encontra todos os usos de uma função/classe/variável no codebase."""
        results = await context_engine.find_usages(symbol=symbol)
        return "\n".join([f"{r['file']}:{r['line']}" for r in results])

    return [search_codebase, get_file_content, find_symbol_usages]
```

## Estratégias de Memória

```python
# vectora/agents/memory.py
from langchain.memory import (
    ConversationSummaryMemory,
    ConversationBufferWindowMemory,
    ConversationTokenBufferMemory,
)

def get_memory_strategy(strategy: str, llm=None):
    match strategy:
        case "truncate":
            # Manter apenas últimas N mensagens
            return ConversationBufferWindowMemory(k=10)
        case "summarize":
            # Sumarizar histórico quando ficar grande
            return ConversationSummaryMemory(llm=llm)
        case "token_limit":
            # Truncar por tokens
            return ConversationTokenBufferMemory(llm=llm, max_token_limit=2000)
        case _:
            return ConversationBufferWindowMemory(k=10)
```

## Streaming com FastAPI + LangChain

Para respostas em streaming (SSE):

```python
# vectora/api/routers/agent.py
from fastapi.responses import StreamingResponse
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

@router.post("/run/stream")
async def run_agent_stream(request: AgentRequest):
    async def generate():
        async for chunk in executor.astream(query=request.query):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Dependency Injection

FastAPI usa injeção de dependência para compartilhar instâncias:

```python
# vectora/api/dependencies.py
from functools import lru_cache
from vectora.agents.executor import VectoraAgentExecutor
from vectora.search.engine import ContextEngine
from vectora.vcr.runtime import VCR

@lru_cache(maxsize=1)
def get_vcr() -> VCR:
    return VCR.from_config("models/vcr-xlm-roberta-v1-int8")

@lru_cache(maxsize=1)
def get_context_engine() -> ContextEngine:
    return ContextEngine.from_config()

def get_executor(
    vcr: VCR = Depends(get_vcr),
    context_engine: ContextEngine = Depends(get_context_engine),
) -> VectoraAgentExecutor:
    return VectoraAgentExecutor(vcr=vcr, context_engine=context_engine)
```

## External Linking

| Conceito                    | Recurso                      | Link                                                                                          |
| --------------------------- | ---------------------------- | --------------------------------------------------------------------------------------------- |
| **FastAPI**                 | Modern Python web framework  | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)                                         |
| **LangChain AgentExecutor** | LangChain agent execution    | [python.langchain.com/docs/modules/agents](https://python.langchain.com/docs/modules/agents/) |
| **LangChain Tools**         | Tool definition e binding    | [python.langchain.com/docs/modules/tools](https://python.langchain.com/docs/modules/tools/)   |
| **Pydantic v2**             | Data validation para FastAPI | [docs.pydantic.dev](https://docs.pydantic.dev/)                                               |
| **LangChain Memory**        | Memory strategies            | [python.langchain.com/docs/modules/memory](https://python.langchain.com/docs/modules/memory/) |
