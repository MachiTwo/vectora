---
title: Observabilidade
slug: observability
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - observability
  - logging
  - metrics
  - tracing
  - monitoring
  - vectora
---

{{< lang-toggle >}}

**Observabilidade** em Vectora envolve entender e monitorar o comportamento do sistema através de **logs estruturados**, **métricas de performance** e **rastreamento distribuído**.

A pilha de observabilidade do Vectora inclui:

- **Logging**: Estruturado com `structlog`, cada operação registra contexto (query, bucket, latência)
- **Métricas**: Prometheus-compatible, coletadas via middleware (latência HTTP, taxa de erro)
- **Rastreamento**: Distributed tracing com Jaeger/Zipkin, integração com LangSmith
- **Alertas**: Regras baseadas em SLO (Service Level Objectives)

## Componentes Principais

| Componente    | Propósito                     | Quando Usar         |
| ------------- | ----------------------------- | ------------------- |
| **Logging**   | Registrar eventos e erros     | Sempre (structured) |
| **Métricas**  | Monitorar latência/throughput | Produção            |
| **Tracing**   | Rastrear requisições          | Produção + Debug    |
| **LangSmith** | Debug de agentes              | Desenvolvimento     |
| **Alertas**   | Notificar falhas              | Produção            |

## Fluxo de Observabilidade

```text
1. Aplicação executa requisição
    │
    ├─ Log estruturado (contexto)
    ├─ Métrica (latência)
    └─ Span (rastreamento)
         │
         ├─→ Prometheus (métricas)
         ├─→ Jaeger (traces)
         └─→ LangSmith (agent debugging)
         │
    2. Dashboard (Grafana) + Alertas
```

## Próximas Seções

1. [Logging](logging.pt.md) — Estrutura de logs, níveis, exportação
2. [Métricas](metrics.pt.md) — Prometheus setup, métricas customizadas
3. [Rastreamento Distribuído](tracing.pt.md) — Jaeger/Zipkin, propagação de contexto
4. [LangSmith Integration](langsmith-integration.pt.md) — Debug de agents, tracing de LLM
5. [Alertas](alerting.pt.md) — Regras SLO, notificações

## External Linking

| Conceito               | Recurso                  | Link                                                            |
| ---------------------- | ------------------------ | --------------------------------------------------------------- |
| **Observability**      | O11y definition          | [observability.engineering](https://observability.engineering/) |
| **OpenTelemetry**      | Instrumentation standard | [opentelemetry.io](https://opentelemetry.io/)                   |
| **Prometheus**         | Metrics collection       | [prometheus.io](https://prometheus.io/)                         |
| **Jaeger**             | Distributed tracing      | [www.jaegertracing.io](https://www.jaegertracing.io/)           |
| **Structured Logging** | Best practices           | [12factor.net/logs](https://12factor.net/logs)                  |
