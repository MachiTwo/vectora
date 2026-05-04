---
title: VCR/ML Engineer - Weekly Routine
role: VCR/ML Engineer
focus: XLM-RoBERTa fine-tuning, LoRA, PyTorch inference optimization, latency <10ms p99
---

# VCR/ML Engineer Routine

## Weekly Cadence

### Monday

- Review VCR priorities with CTO.
- Check latency metrics (target: <10ms p99).
- Plan fine-tuning, quantization, or inference experiments.
- Sync with Backend-LLM on integration needs.
- Sync with Backend on embedding caching strategy.

### Wednesday

- Fine-tuning experiments (LoRA adapters, datasets).
- Model quantization (INT8, FP16) evaluation.
- Inference optimization profiling.
- Benchmark runs on CPU-only hardware.
- Validate accuracy metrics on test set.

### Friday

- Summarize benchmark findings (latency, accuracy, memory).
- Validate trade-offs (latency vs accuracy, inference speed vs memory).
- Prepare model checkpoints for deployment.
- Document decisions for CTO and CDO.
- No regressions in latency (if detected, investigate and fix).

---

## Key Meetings

- **CTO sync**: Model architecture decisions, quantization strategy.
- **Backend-LLM sync**: VCR integration latency, pre-thinking placement.
- **Backend sync**: Embedding caching, Redis integration.
- **QA sync**: Model accuracy regression testing.

---

## Benchmarking Standards

- **Latency Target:** <10ms p99 on CPU (no GPU).
- **Accuracy Target:** >80% on intent classification test set.
- **Memory Target:** Model <500MB quantized (fit in memory).
- **All benchmarks reproducible:** same dataset, same hardware profile.

---

## Success Signals

- VCR inference latency <10ms p99 (CPU-only).
- XLM-RoBERTa fine-tuning improves intent classification accuracy.
- LoRA adapters reduce model size without sacrificing accuracy.
- Quantization maintains accuracy within 1-2% of full-precision.
- Model runs on CPU without GPU (deployable locally).
- Embedding caching reduces VoyageAI API calls by 80%+.
- All benchmarks documented and reproducible.
- No latency regressions in production.
