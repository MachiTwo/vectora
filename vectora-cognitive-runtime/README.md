# Vectora Cognitive Runtime

Vectora Cognitive Runtime é o **pre-thinking layer** da aplicação. Funciona como um sistema de análise contextual que intercepta queries do usuário, enriquece com chunks de LanceDB, memória estruturada, e contexto relevante, preparando uma base sólida para o Agent com thinking ativo processar melhor. Usa XLM-RoBERTa-small como base pré-treinada multilíngue, fine-tuned com LoRA para enriquecimento contextual profundo. Não é um router de estratégias — é um **thinking auxiliar que otimiza o que o Agent vai pensar**. Integrado ao backend Python via subprocess (Phase 1) ou gRPC (Phase 4+).

## Stack

VCR usa PyTorch para inferência local, Hugging Face Transformers para carregar modelos, PEFT com LoRA para fine-tuning eficiente (apenas ~2M params adicionais sem duplicar pesos). Modelo base é XLM-RoBERTa-small (24M parâmetros, 101 idiomas), fine-tuned com dados sintéticos (Phase 1) e traces reais de produção (Phase 2+). XLM-RoBERTa é ideal para essa tarefa porque: (1) roda localmente sem API, (2) suporta 101 idiomas nativamente, (3) 24M params é pequeno o suficiente para latência baixa, (4) fine-tuning com LoRA é rápido e reproducível.

- **Framework:** PyTorch 2.1+ (training + inference Phase 1)
- **Model Base:** XLM-RoBERTa-small (24M params, 101 langs)
- **Fine-Tuning:** PEFT with LoRA (r=8, alpha=16) — apenas ~2M params adicionais
- **Deployment Phase 1:** PyTorch native (transformers library)
- **Deployment Phase 4+:** ONNX Runtime (opcional, para edge/mobile)
- **Training Data:** Synthetic (Phase 1) → Real production traces (Phase 2+)
- **Target Metrics:** Decision accuracy >= 85%, confidence calibration reliable, fallback rate < 5%

## Mapa Mental

VCR roda como **pre-thinking** antes do Agent LangChain processar. Pipeline: query bruta → enriquecimento (chunks relevantes + memória) → XLM-RoBERTa-small analisa contexto → retorna contexto estruturado + análise de confiança. Agent depois recebe tudo pré-processado e pode fazer seu próprio thinking ativo com base sólida.

```
User Query (bruta, multilíngue)
    |
    V
[VCR: PRE-THINKING LAYER]
    |
    +-- Search LanceDB: chunks relevantes
    +-- Query memory: contexto histórico
    +-- XLM-RoBERTa encoder: análise profunda
    |
    V
Output: {
    "enriched_context": [...],
    "relevant_chunks": [...],
    "memory_context": {...},
    "confidence": 0.92,
    "analysis": {...}
}
    |
    V
[AGENT COM THINKING ATIVO - LangChain]
    |
    +-- Recebe contexto pré-enriquecido
    +-- Pensa melhor (reformula, analisa, sintetiza)
    +-- Gera resposta otimizada
    |
    V
Response ao usuário
```

**O que VCR Entrega:**

- `enriched_context`: Contexto estruturado e analisado
- `confidence`: Confiabilidade da análise VCR
- `relevant_chunks`: Top-K chunks de LanceDB rankeados por relevância
- `memory_context`: Memória estruturada relevante para a query
- `analysis`: Análise contextual profunda (tokens, entidades, similaridades)

## Estrutura

Subdiretório `vectora/vectora-cognitive-runtime/` com scripts para training, source code para runtime e inference, data para datasets sintéticos e reais, models para checkpoints durante training.

```
vectora/vectora-cognitive-runtime/
├── scripts/
│   ├── download_base.py               (Download XLM-RoBERTa-small)
│   ├── build_dataset.py               (Synthetic Phase 1 | Real Phase 2+)
│   ├── train.py                       (Fine-tune com LoRA)
│   ├── eval.py                        (Evaluate accuracy, confidence calibration)
│   └── export_onnx.py                 (Export to ONNX — Phase 4+ optional)
├── src/
│   ├── model.py                       (XLM-RoBERTa-small encoder + analysis head)
│   ├── enrichment.py                  (Context enrichment logic)
│   ├── analysis.py                    (Contextual analysis: relevância, confiança, etc)
│   ├── inference.py                   (Inference loop — Phase 1)
│   ├── server.py                      (gRPC server — Phase 4+)
│   └── __init__.py
├── data/
│   ├── raw/
│   │   ├── synthetic_queries.jsonl    (Phase 1: synthetic training data)
│   │   └── production_traces.jsonl    (Phase 2+: real traces from production)
│   └── processed/
│       ├── train_set.jsonl            (Tokenized, ready for training)
│       ├── val_set.jsonl              (Validation set)
│       └── test_set.jsonl             (Test set for evaluation)
├── models/
│   ├── checkpoints/
│   │   ├── lora_r8_a16_epoch1/        (LoRA checkpoint após epoch 1)
│   │   ├── lora_r8_a16_epoch3/        (LoRA checkpoint após epoch 3)
│   │   └── lora_r8_a16_final/         (Final LoRA weights)
│   └── exports/
│       └── vcr-policy-v1.onnx         (Phase 4+: ONNX quantized)
├── evaluation/
│   ├── golden_queries.jsonl           (Hand-curated test cases)
│   ├── metrics.py                     (Calculate accuracy, precision, recall, F1)
│   └── test_production_readiness.py   (Benchmark antes de deploy)
├── config.yaml                        (Model hyperparameters, paths)
├── requirements.txt                   (Python dependencies)
├── .env.example                       (Environment variables template)
├── Makefile                           (Build targets: train, eval, export)
└── README.md
```

---

## Workflow: Development → Training → Inference

### Setup Inicial

```bash
cd vectora/vectora-cognitive-runtime

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download base model (one-time)
python scripts/download_base.py
```

### Phase 1: Synthetic Data Training

Treina VCR com dados sintéticos gerados (queries simuladas + decisões esperadas).

```bash
# 1. Build synthetic dataset
python scripts/build_dataset.py --synthetic --output data/processed/

# 2. Train com LoRA (r=8, alpha=16)
#    - Fine-tunes apenas ~2M additional params
#    - Salva checkpoints a cada epoch
python scripts/train.py \
  --model FacebookAI/xlm-roberta-small \
  --dataset data/processed/train_set.jsonl \
  --val_dataset data/processed/val_set.jsonl \
  --epochs 3 \
  --batch_size 32 \
  --lora_r 8 \
  --lora_alpha 16

# 3. Evaluate no test set
python scripts/eval.py \
  --model models/checkpoints/lora_r8_a16_final/ \
  --test_dataset data/processed/test_set.jsonl

# 4. Ready for Phase 2
```

### Phase 2+: Real Production Data

Quando backend está rodando em produção, coletar traces reais.

```bash
# 1. Collect production traces
#    (Backend logs: query, context, ground_truth_decision)

# 2. Build dataset from real traces
python scripts/build_dataset.py \
  --real \
  --traces data/raw/production_traces.jsonl \
  --output data/processed/

# 3. Fine-tune com real data (continua do Phase 1)
python scripts/train.py \
  --model FacebookAI/xlm-roberta-small \
  --lora_checkpoint models/checkpoints/lora_r8_a16_final/ \
  --dataset data/processed/train_set.jsonl \
  --val_dataset data/processed/val_set.jsonl \
  --epochs 5 \
  --batch_size 16 \
  --learning_rate 1e-4

# 4. Evaluate e deploy se accuracy OK
python scripts/eval.py --model models/checkpoints/lora_r8_a16_final/
```

---

## Inference: Backend Integration

VCR roda como subprocess que enriquece contexto. Backend Python chama VCR e integra output no LangChain RAG handler.

### Phase 1: Python Subprocess

```python
# vectora-cognitive-runtime/src/inference.py
import json
import sys
import torch
from transformers import AutoTokenizer, AutoModel
from peft import PeftModel

# Load base model + LoRA weights
model = AutoModel.from_pretrained("FacebookAI/xlm-roberta-small")
model = PeftModel.from_pretrained(model, "models/checkpoints/lora_r8_a16_final/")
tokenizer = AutoTokenizer.from_pretrained("FacebookAI/xlm-roberta-small")
model.eval()

# Read input from stdin (JSON)
input_data = json.loads(sys.stdin.read())
query = input_data["query"]
chunks = input_data["chunks"]  # Pre-fetched from LanceDB
memory = input_data["memory"]   # Estrutured memory context

# Enrich: combine all context
context_text = " ".join([c["text"] for c in chunks])
memory_text = json.dumps(memory, ensure_ascii=False)
combined = f"{query} [SEP] {context_text} [SEP] {memory_text}"

# Tokenize
inputs = tokenizer(
    combined,
    return_tensors="pt",
    padding=True,
    truncation=True,
    max_length=512
)

# Inference: deep contextual analysis
with torch.no_grad():
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state

    # Analysis: relevância, entidades, similaridades
    analysis = {
        "embedding_mean": embeddings.mean(dim=1).tolist(),
        "chunk_scores": compute_relevance_scores(embeddings, chunks),
        "memory_relevance": compute_memory_relevance(embeddings, memory),
    }

    confidence = calculate_confidence(analysis)

# Output: enriched context for Agent
output = {
    "enriched_context": {
        "query": query,
        "chunks": chunks,
        "memory": memory,
        "analysis": analysis,
    },
    "confidence": float(confidence),
    "vcr_embedding": embeddings.mean(dim=1)[0].tolist()
}
print(json.dumps(output))
```

### Backend Python Integration (LangChain)

```python
# backend/core/vcr_service.py
from langchain.callbacks import BaseCallbackHandler
import subprocess
import json

class VCREnrichmentHandler(BaseCallbackHandler):
    """Pre-thinking enrichment before Agent processes"""

    def __init__(self, vcr_subprocess_path):
        self.vcr_path = vcr_subprocess_path

    def enrich_context(self, query: str, chunks: list, memory: dict) -> dict:
        """Call VCR to enrich context"""
        input_data = {
            "query": query,
            "chunks": chunks,
            "memory": memory
        }

        result = subprocess.run(
            ["python", self.vcr_path],
            input=json.dumps(input_data),
            capture_output=True,
            text=True
        )

        return json.loads(result.stdout)

# Use in RAG handler
vcr = VCREnrichmentHandler("vectora-cognitive-runtime/src/inference.py")
enriched = vcr.enrich_context(query, top_chunks, user_memory)

# Pass enriched context to Agent
agent.invoke({
    "query": enriched["enriched_context"]["query"],
    "context": enriched["enriched_context"],
    "confidence": enriched["confidence"]
})
```

### Phase 4+: gRPC Server (Optional)

Para melhor performance em produção, VCR roda como servidor gRPC separado (menos overhead que subprocess).

```bash
python src/server.py --port 50051
```

Backend Python chama via gRPC:

```python
from vcr_pb2 import EnrichmentRequest, EnrichmentResponse
import grpc

channel = grpc.aio.secure_channel("localhost:50051", ...)
stub = VCRServiceStub(channel)

response = await stub.Enrich(EnrichmentRequest(
    query="Como uso React hooks?",
    chunks=[...],  # Pre-fetched chunks
    memory={...}   # Structured memory
))

# response.enriched_context, response.confidence, response.vcr_embedding
```

---

## Multilingual Support

XLM-RoBERTa-small suporta 101 idiomas nativamente. Fine-tuning funciona para qualquer idioma.

**Treinar com dados multilíngues (Phase 2+):**

```bash
python scripts/build_dataset.py \
  --real \
  --traces data/raw/production_traces_multilang.jsonl \
  --languages pt-br,en,es,fr \
  --output data/processed/
```

---

## Deployment Options

### Option A: PyTorch (Phase 1 — Recommended)

Simples, nativo, sem conversão.

**Vantagens:**

- Setup mínimo
- Fine-tuning direto
- Debugging fácil

**Uso:**

```bash
python src/inference.py < input.json > output.json
```

### Option B: ONNX (Phase 4+ — Optional)

Quantizado, para edge/mobile.

**Export:**

```bash
python scripts/export_onnx.py \
  --model models/checkpoints/lora_r8_a16_final/ \
  --quantize int8 \
  --output models/exports/vcr-policy-v1.onnx
```

---

## License

Apache 2.0
