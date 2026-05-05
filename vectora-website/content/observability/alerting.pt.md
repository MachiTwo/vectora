---
title: Alertas e Notificações
slug: alerting
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - alerting
  - notifications
  - slo
  - observability
  - vectora
---

{{< lang-toggle >}}

**Alertas** em Vectora notificam sobre violações de SLO (Service Level Objectives) e falhas críticas. Alertas são definidos em Prometheus e enviados para múltiplos canais: Slack, email, PagerDuty.

## SLOs do Vectora

Service Level Objectives padrão:

| Métrica         | SLO     | Alerta se violar   |
| --------------- | ------- | ------------------ |
| Disponibilidade | 99.9%   | 2+ erros 5xx em 5m |
| Latência P99    | < 500ms | P99 > 500ms por 5m |
| Taxa de erro    | < 0.1%  | Taxa > 0.1% por 2m |
| Cache hit ratio | > 80%   | < 50% por 10m      |
| Conexão BD      | OK      | Falha por 1m       |

## Regras de Alerta Prometheus

Arquivo `prometheus-alerts.yml`:

```yaml
groups:
  - name: vectora_slo
    interval: 30s

    rules:
      # Alerta 1: Alta latência
      - alert: VectoraHighLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
          service: vectora
        annotations:
          summary: "Latência P99 acima de 500ms"
          description: "P99 latência é {{ $value | humanizeDuration }}"

      # Alerta 2: Taxa de erro alta
      - alert: VectoraHighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.001
        for: 2m
        labels:
          severity: critical
          service: vectora
        annotations:
          summary: "Taxa de erro acima de 0.1%"
          description: "Taxa de erro atual: {{ $value | humanizePercentage }}"

      # Alerta 3: Banco de dados offline
      - alert: VectoraDatabaseDown
        expr: up{job="postgresql"} == 0
        for: 1m
        labels:
          severity: critical
          service: vectora
        annotations:
          summary: "PostgreSQL offline"

      # Alerta 4: Cache hit ratio baixo
      - alert: VectoraLowCacheHitRatio
        expr: |
          (vectora_cache_hits_total / (vectora_cache_hits_total + vectora_cache_misses_total))
          < 0.5
        for: 10m
        labels:
          severity: warning
          service: vectora
        annotations:
          summary: "Cache hit ratio baixo"
          description: "Hit ratio: {{ $value | humanizePercentage }}"

      # Alerta 5: Índice corrompido
      - alert: VectoraIndexCorrupted
        expr: vectora_index_error_total > 10
        for: 5m
        labels:
          severity: critical
          service: vectora
        annotations:
          summary: "Erros de índice detectados"
```

## Configuração do AlertManager

Arquivo `alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m
  slack_api_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

route:
  receiver: "vectora-team"
  group_by: ["alertname", "service"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h

  routes:
    # Alertas críticos → PagerDuty
    - match:
        severity: critical
      receiver: pagerduty
      continue: true

    # Alertas warning → Slack
    - match:
        severity: warning
      receiver: slack-warnings

receivers:
  - name: "vectora-team"
    slack_configs:
      - channel: "#vectora-alerts"
        title: "Alerta: {{ .GroupLabels.alertname }}"
        text: "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"

  - name: "slack-warnings"
    slack_configs:
      - channel: "#vectora-warnings"
        title: "Aviso: {{ .GroupLabels.alertname }}"

  - name: "pagerduty"
    pagerduty_configs:
      - service_key: "YOUR-PAGERDUTY-KEY"
        description: "{{ .GroupLabels.alertname }}: {{ .Alerts.Firing | len }} alertas"
```

## Notificações Slack

### Setup

1. Criar webhook Slack:

   - Ir para [api.slack.com/apps](https://api.slack.com/apps)
   - Criar novo app
   - Ativar "Incoming Webhooks"
   - Copiar URL

2. Adicionar ao AlertManager:

   ```yaml
   slack_api_url: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"
   ```

### Exemplo de Notificação

```text
🚨 Alerta: VectoraHighErrorRate

Descrição: Taxa de erro acima de 0.1%
Valor atual: 0.15%
Service: vectora
Duração: 2 minutos

👉 Ver em Prometheus: http://localhost:9090/alerts
```

## Notificações Email

Configurar SMTP para emails:

```yaml
global:
  smtp_smarthost: "smtp.gmail.com:587"
  smtp_auth_username: "seu-email@gmail.com"
  smtp_auth_password: "sua-senha"
  smtp_require_tls: true

receivers:
  - name: "email-oncall"
    email_configs:
      - to: "oncall@vectora.com"
        from: "alerts@vectora.com"
        headers:
          Subject: "Alerta {{ .GroupLabels.alertname }}"
```

## Notificações PagerDuty

Para escalação de alertas críticos:

```yaml
receivers:
  - name: "pagerduty"
    pagerduty_configs:
      - service_key: "YOUR-SERVICE-KEY"
        severity: '{{ if eq .Status "firing" }}critical{{ else }}resolve{{ end }}'
        client: "Vectora Alerting"
        client_url: "http://alertmanager:9093"
```

## Runbook (Ações Corretivas)

Para cada alerta, documentar ações:

### VectoraHighLatency

**Causa provável**: Índice não otimizado, lentidão de BD

**Ações**:

1. Verificar `HNSW_M` e `HNSW_EF` em config
2. Recriar índice com parâmetros maiores
3. Aumentar `shared_buffers` no PostgreSQL
4. Verificar conexões abertas: `SELECT count(*) FROM pg_stat_activity`

### VectoraDatabaseDown

**Causa provável**: Serviço PostgreSQL parou

**Ações**:

1. Verificar status: `systemctl status postgresql`
2. Reiniciar: `systemctl restart postgresql`
3. Verificar logs: `journalctl -u postgresql -n 100`
4. Verificar espaço em disco: `df -h /var/lib/postgresql`

## Teste de Alertas

### Disparar Alerta Manual

```python
# Script para simular alto latency
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def make_slow_request():
    try:
        requests.get("http://localhost:8000/search",
                    params={"q": "test"*100},
                    timeout=10)
    except:
        pass

# Fazer muitas requisições lentas
with ThreadPoolExecutor(max_workers=50) as executor:
    for _ in range(500):
        executor.submit(make_slow_request)

# Alerta deve disparar após 5m
```

### Testar Notificação Slack

```bash
# Enviar mensagem direta para webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Teste de alerta"}' \
  YOUR_SLACK_WEBHOOK_URL
```

## Dashboard de SLO

Criar painel em Grafana mostrando compliance com SLOs:

```text
┌─────────────────────────────────────┐
│ Availability SLO: 99.9%             │
│ Current: 99.95% ✓                   │
│ Error Budget Remaining: 3.6 hours   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Latency P99 SLO: < 500ms            │
│ Current: 320ms ✓                    │
│ Margin: 180ms                       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Cache Hit Ratio SLO: > 80%          │
│ Current: 85% ✓                      │
│ Margin: +5%                         │
└─────────────────────────────────────┘
```

## Troubleshooting

### Alertas não disparam

```bash
# 1. Verificar AlertManager está rodando
docker ps | grep alertmanager

# 2. Verificar sintaxe das regras
promtool check rules prometheus-alerts.yml

# 3. Verificar webhook Slack
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' YOUR_WEBHOOK_URL
```

### Muitos falsos positivos

```yaml
# Aumentar período de validação
- alert: VectoraHighLatency
  expr: histogram_quantile(0.99, ...) > 0.5
  for: 10m # Aumentar de 5m para 10m
```

### Alerta não resolve

```yaml
# Adicionar regra de resolução explícita
- alert: VectoraDatabaseDown
  expr: up{job="postgresql"} == 0
  for: 1m
# Resolver manualmente em AlertManager
```

## External Linking

| Conceito             | Recurso                    | Link                                                                                                                                            |
| -------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prometheus Rules** | Alert rules documentation  | [prometheus.io/docs/prometheus/latest/configuration/alerting_rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) |
| **AlertManager**     | Alert routing and grouping | [prometheus.io/docs/alerting/latest/overview](https://prometheus.io/docs/alerting/latest/overview/)                                             |
| **SLO Guide**        | Defining SLOs              | [sre.google/sre-book/service-level-objectives](https://sre.google/sre-book/chapters/service-level-objectives/)                                  |
| **PagerDuty API**    | Incident management        | [developer.pagerduty.com](https://developer.pagerduty.com/)                                                                                     |
| **Slack Webhooks**   | Incoming webhooks          | [api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks)                                                                    |
