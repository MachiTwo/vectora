---
title: Especializado vs Generalista
slug: specialized-vs-generalist
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - agents
  - architecture
  - llm
  - performance
  - quality
  - specialized
  - vectora
---

{{< lang-toggle >}}

Um agente **generalista** (Claude sonnet-4-6) tenta responder qualquer pergunta; um agente **especializado** é fine-tuned ou constrangido para um domínio específico (ex: "especialista em segurança"). Vectora suporta ambas as abordagens.

## Comparação

| Aspecto           | Generalista           | Especializado                           |
| ----------------- | --------------------- | --------------------------------------- |
| **Modelo**        | Claude/GPT padrão     | Fine-tuned ou constrangido              |
| **Accuracy**      | 80-85%                | 92-97% (no domínio)                     |
| **Latência**      | ~2s                   | ~3s (fine-tuning pequeno)               |
| **Custo**         | Baixo                 | Médio (fine-tuning) + Baixo (inference) |
| **Flexibilidade** | Alta                  | Baixa (especializado)                   |
| **Setup**         | Trivial               | 1-2 semanas                             |
| **Quando Usar**   | Default, prototipagem | Produção crítica                        |

## Generalista: Claude sonnet-4-6

### Abordagem Padrão do Vectora

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-6")

# System prompt genérico
response = llm.invoke(
    "Analyze this authentication code and suggest improvements",
    system="You are a helpful code expert. Provide detailed analysis."
)
```

**Pros:**

- Pronto para usar
- Flexível para qualquer pergunta
- Atualizado com conhecimento recente
- Bom em codebases variados

**Cons:**

- Genérico, não otimizado para domínio
- Às vezes perde detalhes específicos
- Pode ser "verbose"

**Exemplo Response:**

```text
O código usa JWT corretamente. Algumas observações:
1. Verificar expiração ✓
2. Validar assinatura ✓
3. Verificar claims ✓

Sugestão: adicionar rate limiting no endpoint de token.
```

## Especializado: Fine-tuning em Domínio

Para reduzir erros em um domínio específico, usar **fine-tuning** com exemplos reais:

### Setup de Fine-tuning (Anthropic)

```python
import anthropic

client = anthropic.Anthropic()

# 1. Preparar dados de treinamento
training_data = [
    {
        "messages": [
            {
                "role": "user",
                "content": "Review security in this JWT code: def verify_token(...)..."
            },
            {
                "role": "assistant",
                "content": """Security Review:
✓ Uses cryptography library (best practice)
✓ Verifies expiration
✓ Validates signature
⚠️ Missing: rate limiting on /token endpoint
✗ Missing: token revocation mechanism

Recommendation: Implement revocation list in Redis"""
            }
        ]
    },
    # ... 50+ exemplos similares
]

# 2. Upload dataset
dataset = client.messages.beta.files.create(
    file=open("training_data.jsonl", "rb")
)

# 3. Treinar
model = client.messages.beta.fine_tuning.create(
    model="claude-opus-4-7",
    training_file=dataset.id,
    learning_rate=0.01,
    epochs=3,
)

# 4. Usar modelo fine-tuned
response = client.messages.create(
    model=model.id,  # Usar modelo treinado
    messages=[
        {
            "role": "user",
            "content": "Review security in this JWT code: ..."
        }
    ]
)
```

**Latência do Fine-tuning:**

- Setup: 1-2 semanas
- Training: 2-6 horas
- Inference: ~3s (similar ao generalista)

### Especializado: Constraint-based

Abordagem mais rápida usando **prompts especializados** ao invés de fine-tuning:

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

llm = ChatAnthropic(model="claude-sonnet-4-6")

# System prompt especializado para segurança
security_specialist_prompt = ChatPromptTemplate.from_messages([
    ("system", """Você é um especialista em segurança de código.

Ao revisar código, SEMPRE verificar:
1. **Autenticação**: JWT válido? Expiração correta?
2. **Autorização**: Permissões corretas? RBAC implementado?
3. **Criptografia**: Algoritmos seguros (HMAC-SHA256+)?
4. **Injeção**: SQL injection, command injection?
5. **Rate Limiting**: Proteção contra brute force?
6. **Logging**: Eventos sensíveis logados?
7. **Secrets Management**: Sem hardcoded keys?

Forneça score de segurança (0-100) e ações concretas."""),
    ("human", "{code}")
])

specialist_chain = security_specialist_prompt | llm

response = specialist_chain.invoke(code="def verify_token(...)...")
```

**Latência:**

- Setup: 1 dia (escrever prompt)
- Inference: ~2s (sem overhead)

## Quando Usar Cada Um

### Use Generalista se

- Query é **variada** (diferentes tópicos)
- Setup rápido é crítico
- Accuracy 80%+ é suficiente
- Orçamento limitado

**Exemplo:**

```text
✓ "Explain how this database connection works"
✓ "Refactor this function for readability"
✓ "What's the difference between these two implementations?"
```

### Use Especializado se

- Domínio é **estreito** (ex: segurança)
- Accuracy >95% é crítico
- Custo operacional importa mais que setup
- Tempo para produção é flexível

**Exemplo:**

```text
✓ "Security review for JWT implementation"
✓ "Performance optimization for this query"
✓ "Compliance check for GDPR requirements"
```

## Hybrid Approach

Combinar ambos para máxima qualidade:

```python
def analyze_code(code: str, aspect: str):
    """
    1. Rodar especialista de segurança
    2. Rodar generalista para contexto
    3. Sintetizar resposta
    """

    # Especialista: segurança
    security_specialist = ChatPromptTemplate.from_messages([
        ("system", SECURITY_PROMPT),
        ("human", "{code}")
    ]) | llm

    security_review = security_specialist.invoke(code=code)

    # Generalista: contexto completo
    generalizer = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente de código."),
        ("human", """
Código:
{code}

Análise de Segurança (especialista):
{security_review}

Forneça análise completa considerando a review de segurança.""")
    ]) | llm

    full_analysis = generalizer.invoke(
        code=code,
        security_review=security_review
    )

    return full_analysis
```

## Performance Benchmark

Teste com seu codebase:

```python
import time
from vectora import search

queries = [
    "JWT authentication bugs",
    "SQL injection risks",
    "Performance bottlenecks",
    # ... 20+ queries
]

results = {
    "generalista": {"time": 0, "errors": 0},
    "especializado": {"time": 0, "errors": 0},
}

# Testar generalista
for query in queries:
    start = time.time()
    response = generalista.invoke(query)
    results["generalista"]["time"] += time.time() - start
    if not validate_response(response):
        results["generalista"]["errors"] += 1

# Testar especializado
for query in queries:
    start = time.time()
    response = especialista.invoke(query)
    results["especializado"]["time"] += time.time() - start
    if not validate_response(response):
        results["especializado"]["errors"] += 1

# Comparar
print(f"Generalista: {results['generalista']['time']/len(queries):.2f}s/query, {results['generalista']['errors']} errors")
print(f"Especializado: {results['especializado']['time']/len(queries):.2f}s/query, {results['especializado']['errors']} errors")
```

## Recomendação

Para **MVP do Vectora**: comece com **generalista** (Claude sonnet-4-6).

Quando pronto para produção:

- Se accuracy 80%+ basta: mantenha generalista
- Se precisa 95%+: considere especializado
- Se quer máxima qualidade: hybrid approach

## External Linking

| Conceito               | Recurso                       | Link                                                                                               |
| ---------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------- |
| **Claude Fine-tuning** | Anthropic documentation       | [docs.anthropic.com/fine-tuning](https://docs.anthropic.com/en/docs/build-a-chatbot)               |
| **Few-shot Learning**  | In-context learning patterns  | [python.langchain.com/docs/guides/evaluation](https://python.langchain.com/docs/guides/evaluation) |
| **Prompt Engineering** | Advanced prompting techniques | [learnprompting.org](https://learnprompting.org/)                                                  |
| **Domain Adaptation**  | ML domain adaptation methods  | [paperswithcode.com/task/domain-adaptation](https://paperswithcode.com/task/domain-adaptation)     |
| **Transfer Learning**  | Pre-training and fine-tuning  | [en.wikipedia.org/wiki/Transfer_learning](https://en.wikipedia.org/wiki/Transfer_learning)         |
