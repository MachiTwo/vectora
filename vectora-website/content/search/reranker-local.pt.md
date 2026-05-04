---
title: "Reranker Local: XLM-RoBERTa no Vectora"
slug: reranker-local
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
  - fine-tuning
  - int8
  - lora
  - pytorch
  - rag
  - reranker
  - vector-search
  - vectora
  - vcr
  - xlm-roberta
---

{{< lang-toggle >}}

{{< section-toggle >}}

O reranker local do Vectora é XLM-RoBERTa-small com fine-tuning LoRA e quantização INT8. Parte do VCR (Vectora Cognitive Runtime), roda 100% em CPU sem dependência de APIs externas. Latência target: < 10ms para 100 candidatos.

## Especificações

| Aspecto            | Detalhe                 |
| ------------------ | ----------------------- |
| **Modelo base**    | xlm-roberta-small       |
| **Parâmetros**     | 117M                    |
| **Fine-tuning**    | LoRA (r=16, alpha=32)   |
| **Quantização**    | INT8 dinâmica           |
| **Latência (CPU)** | < 10ms p99              |
| **Memória**        | < 500MB RAM             |
| **Idiomas**        | 100+ (incluindo código) |
| **Custo**          | Grátis (local)          |

## Arquitetura: Cross-Encoder

XLM-RoBERTa funciona como cross-encoder: recebe query e documento juntos e calcula um score de relevância único.

```text
Input:  [CLS] query [SEP] trecho_de_codigo [SEP]
        -> Transformer (12 camadas, 384 hidden)
        -> [CLS] representation
        -> Linear(384, 1) + Sigmoid
Output: score de relevância (0.0 a 1.0)
```

A diferença em relação ao bi-encoder (usado na busca vetorial): query e documento são processados simultaneamente. A atenção pode capturar relações diretas entre os tokens da query e os tokens do documento.

## Fine-Tuning com LoRA

LoRA (Low-Rank Adaptation) adiciona matrizes treináveis de baixo rank às camadas de atenção, sem modificar os pesos originais do XLM-RoBERTa.

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForSequenceClassification

base_model = AutoModelForSequenceClassification.from_pretrained(
    "xlm-roberta-small",
    num_labels=1,
)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["query", "value"],
    lora_dropout=0.1,
    bias="none",
    task_type="SEQ_CLS",
)

model = get_peft_model(base_model, lora_config)
```

LoRA reduz parâmetros treináveis de 117M para ~2M, permitindo fine-tuning em hardware modesto com dados de código real.

## Quantização INT8

Após fine-tuning, o modelo é quantizado para INT8, reduzindo tamanho e latência:

```python
import torch

quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8,
)

torch.save(quantized_model.state_dict(), "vcr_reranker_int8.pt")
```

| Precisão | Tamanho | Latência (100 docs) |
| -------- | ------- | ------------------- |
| FP32     | 450MB   | ~25ms               |
| INT8     | 120MB   | ~8ms                |

## Integração no Pipeline de Busca

O reranker recebe os top-100 candidatos da busca HNSW e retorna top-10 com scores.

```python
from transformers import AutoTokenizer
import torch

class LocalReranker:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-small")
        self.model = torch.load(model_path)
        self.model.eval()

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 10,
    ) -> list[dict]:
        scores = []

        for candidate in candidates:
            inputs = self.tokenizer(
                query,
                candidate["content"],
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True,
            )

            with torch.no_grad():
                output = self.model(**inputs)
                score = torch.sigmoid(output.logits).item()

            scores.append((score, candidate))

        scores.sort(key=lambda x: x[0], reverse=True)

        return [
            {**cand, "rerank_score": score}
            for score, cand in scores[:top_k]
        ]
```

### Uso no Pipeline VCR

```python
from vectora.vcr import LocalReranker

reranker = LocalReranker(model_path="models/vcr_reranker_int8.pt")

# Após busca HNSW (top-100 candidatos)
reranked = reranker.rerank(
    query="Como validar tokens JWT?",
    candidates=hnsw_results,  # lista de 100 dicts com "content"
    top_k=10,
)

# reranked: lista de 10 dicts com "rerank_score" adicionado
# ordenados por relevância decrescente
```

## Batching para Performance

Para múltiplas queries simultâneas, use batching para aproveitar paralelismo da CPU:

```python
def rerank_batch(
    self,
    queries: list[str],
    candidates_per_query: list[list[dict]],
    top_k: int = 10,
) -> list[list[dict]]:
    all_inputs = []
    query_indices = []

    for q_idx, (query, candidates) in enumerate(
        zip(queries, candidates_per_query)
    ):
        for candidate in candidates:
            all_inputs.append((query, candidate["content"]))
            query_indices.append(q_idx)

    encoded = self.tokenizer(
        [q for q, _ in all_inputs],
        [d for _, d in all_inputs],
        return_tensors="pt",
        max_length=512,
        truncation=True,
        padding=True,
    )

    with torch.no_grad():
        logits = self.model(**encoded).logits
        scores = torch.sigmoid(logits).squeeze(-1).tolist()

    # Agrupa scores por query e retorna top-k
    results = [[] for _ in queries]
    for idx, (q_idx, score) in enumerate(zip(query_indices, scores)):
        results[q_idx].append((score, candidates_per_query[q_idx][idx]))

    return [
        [
            {**cand, "rerank_score": score}
            for score, cand in sorted(r, reverse=True)[:top_k]
        ]
        for r in results
    ]
```

## Endpoint VCR

O VCR expõe o reranker via FastAPI:

```http
POST /vcr/score-relevance
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "query": "validate JWT token",
  "candidates": [
    { "id": "1", "content": "def validate_token(token: str) -> dict: ..." },
    { "id": "2", "content": "def create_token(user_id: str) -> str: ..." }
  ]
}
```

Resposta:

```json
{
  "results": [
    { "id": "1", "score": 0.94 },
    { "id": "2", "score": 0.31 }
  ],
  "latency_ms": 7.4
}
```

## Métricas e Monitoramento

O reranker registra métricas Prometheus via `/vcr/metrics`:

```text
vcr_reranker_latency_ms{quantile="0.50"} 5.2
vcr_reranker_latency_ms{quantile="0.95"} 8.9
vcr_reranker_latency_ms{quantile="0.99"} 12.1
vcr_reranker_candidates_total 100
vcr_reranker_top_k 10
vcr_reranker_ndcg_at_10 0.83
```

Target de qualidade: NDCG@10 >= 0.80. Alertas são disparados se cair abaixo de 0.75.

## External Linking

| Conceito                 | Recurso                                 | Link                                                                                      |
| ------------------------ | --------------------------------------- | ----------------------------------------------------------------------------------------- |
| **XLM-RoBERTa**          | Multilingual pre-trained model          | [huggingface.co/xlm-roberta-small](https://huggingface.co/xlm-roberta-small)              |
| **LoRA**                 | Low-Rank Adaptation for LLMs            | [arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)                              |
| **PEFT**                 | Parameter-Efficient Fine-Tuning library | [huggingface.co/docs/peft](https://huggingface.co/docs/peft)                              |
| **PyTorch Quantization** | INT8 dynamic quantization               | [pytorch.org/docs/stable/quantization](https://pytorch.org/docs/stable/quantization.html) |
| **Cross-Encoder**        | Sentence Transformers cross-encoders    | [sbert.net/docs/cross_encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) |
