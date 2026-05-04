---
title: "Guardrails em Produção"
slug: "langchain/guardrails"
description: "Validação, segurança e conformidade em agentes"
date: 2026-05-03
type: docs
sidebar:
  open: true
breadcrumbs: true
tags: ["langchain", "guardrails", "security", "validation", "safety"]
---

{{< lang-toggle >}}

Guardrails são mecanismos de segurança que validam e filtram conteúdo em pontos-chave da execução de um agente.

## Por Que Guardrails?

Agentes em produção precisam de proteção contra:
- **Vazamento de dados** - PII, senhas, tokens
- **Injeção de prompts** - Instruções maliciosas
- **Conteúdo prejudicial** - Hate speech, violência
- **Não-conformidade** - Regulações (GDPR, HIPAA)
- **Saídas inválidas** - Dados estruturados malformados

## Dois Tipos de Guardrails

### Guardrails Determinísticos

Baseados em **regras explícitas** - rápidos e econômicos:

```python
import re

# Bloquear tokens de API
def check_api_tokens(text: str) -> bool:
    patterns = [
        r'sk-[A-Za-z0-9]{48}',  # OpenAI
        r'pk_live_[A-Za-z0-9]+',  # Stripe
        r'Bearer\s+[A-Za-z0-9\-._~+/]+=*'  # JWT
    ]
    
    for pattern in patterns:
        if re.search(pattern, text):
            return False
    return True

# Bloquear PII comum
def check_pii(text: str) -> bool:
    pii_patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{16}\b',  # Credit card
        r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'  # Email
    ]
    
    for pattern in pii_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    return True

# Middleware guardrail
def guardrail_deterministic(state: dict) -> dict:
    last_message = state["messages"][-1]
    
    if not check_api_tokens(last_message.content):
        raise ValueError("API token detectado - resposta bloqueada")
    
    if not check_pii(last_message.content):
        raise ValueError("PII detectado - resposta bloqueada")
    
    return state
```

**Vantagens:**
- Execução instantânea
- Sem custo adicional
- Previsível

**Limitações:**
- Não detecta violações sofisticadas
- Requer manutenção de padrões

### Guardrails Baseados em Modelos

Usam **LLMs ou classificadores** para análise semântica:

```python
from langchain.chat_models import ChatAnthropic

async def check_content_safety(text: str) -> dict:
    """Classificar conteúdo com LLM"""
    
    response = await llm.apredict(
        template="""Analise este conteúdo quanto a segurança.
        
        Conteúdo: {text}
        
        Responda em JSON:
        {{
            "is_safe": true/false,
            "category": "pii|injection|harmful|compliant|ok",
            "reason": "explicação",
            "action": "allow|block|review"
        }}""",
        text=text
    )
    
    return json.loads(response)

# Guardrail com modelo
async def guardrail_semantic(state: dict) -> dict:
    last_message = state["messages"][-1]
    
    result = await check_content_safety(last_message.content)
    
    if result["action"] == "block":
        raise ValueError(f"Guardrail: {result['reason']}")
    
    elif result["action"] == "review":
        # Escalar para humano
        state["needs_review"] = True
        state["review_reason"] = result["reason"]
    
    return state
```

**Vantagens:**
- Detecta problemas sutis
- Compreensão semântica
- Adaptável

**Limitações:**
- Mais lento
- Custo maior
- Menos previsível

## Pontos de Aplicação

### Antes do Agente

Validar **entrada do usuário**:

```python
def guardrail_input(state: dict) -> dict:
    user_input = state["messages"][-1].content
    
    # Checar tamanho
    if len(user_input) > 10000:
        raise ValueError("Input muito longo")
    
    # Checar injeção
    if contains_sql_keywords(user_input):
        raise ValueError("Possível SQL injection")
    
    return state
```

### Durante Execução de Tools

Validar **saída de ferramentas**:

```python
def guardrail_tool_output(tool_result: str) -> str:
    # Remover PII da resposta
    if contains_pii(tool_result):
        tool_result = mask_pii(tool_result)
    
    # Validar formato
    if not is_valid_json(tool_result):
        tool_result = json.dumps({"error": "Invalid format"})
    
    return tool_result
```

### Depois do Agente

Validar **resposta final**:

```python
def guardrail_output(state: dict) -> dict:
    response = state["messages"][-1].content
    
    # Checar conformidade
    if not is_compliant_with_policy(response):
        return {"error": "Resposta não está em conformidade"}
    
    # Checar qualidade
    if not meets_quality_threshold(response):
        state["needs_revision"] = True
    
    return state
```

## Padrão Completo em LangGraph

```python
from langgraph.graph import StateGraph, START, END

class GuardrailState(TypedDict):
    messages: list
    needs_review: bool
    blocked: bool

def guardrail_input(state: GuardrailState):
    if is_malicious(state["messages"][-1]):
        state["blocked"] = True
    return state

def agent_node(state: GuardrailState):
    if state["blocked"]:
        return state
    
    response = llm.invoke(state["messages"])
    state["messages"].append(response)
    return state

def guardrail_output(state: GuardrailState):
    if not is_safe(state["messages"][-1]):
        state["needs_review"] = True
    return state

graph = StateGraph(GuardrailState)
graph.add_node("input_guard", guardrail_input)
graph.add_node("agent", agent_node)
graph.add_node("output_guard", guardrail_output)

graph.add_edge(START, "input_guard")
graph.add_edge("input_guard", "agent")
graph.add_edge("agent", "output_guard")
graph.add_edge("output_guard", END)

app = graph.compile()
```

## External Linking

| Conceito | Recurso | Link |
|----------|---------|------|
| Guardrails | Overview | [https://docs.langchain.com/oss/python/langchain/guardrails](https://docs.langchain.com/oss/python/langchain/guardrails) |
| Content Safety | Validation Patterns | [https://docs.langchain.com/oss/python/langchain/guides/safety](https://docs.langchain.com/oss/python/langchain/guides/safety) |
| PII Detection | Regular Expressions | [https://owasp.org/www-community/attacks/PII_Detection](https://owasp.org/www-community/attacks/PII_Detection) |
| Prompt Injection | Defense Patterns | [https://owasp.org/www-community/attacks/Prompt_Injection](https://owasp.org/www-community/attacks/Prompt_Injection) |
| GDPR Compliance | Data Protection | [https://gdpr-info.eu/](https://gdpr-info.eu/) |
