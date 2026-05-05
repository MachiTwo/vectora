---
title: Deployment
slug: deployment
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - deployment
  - docker
  - installation
  - production
  - vps
  - vectora
---

{{< lang-toggle >}}

O Vectora oferece múltiplas opções de deployment dependendo do seu caso de uso: **local development**, **single-user VPS**, ou **multi-tenant web application**.

## Opções de Deployment

| Modo               | Infraestrutura           | Usuários | Custo               | Setup  |
| ------------------ | ------------------------ | -------- | ------------------- | ------ |
| **pip/pipx**       | Sua máquina              | 1 (você) | Grátis (cloud APIs) | 5 min  |
| **Docker**         | Seu servidor             | 1+       | Baixo (VPS)         | 10 min |
| **Docker Compose** | VPS + PostgreSQL + Redis | 10+      | Médio               | 20 min |
| **Kubernetes**     | Cloud (AWS/GCP/Azure)    | 100+     | Alto                | 1h     |

## Checklist Pre-Deployment

Antes de fazer deploy em produção:

- [ ] Chave Anthropic (Claude) ou OpenAI (GPT) configurada
- [ ] Chave VoyageAI configurada (embeddings obrigatório)
- [ ] PostgreSQL 15+ rodando (local ou remoto)
- [ ] Redis 7+ rodando (local ou remoto)
- [ ] Certificado SSL/TLS se usar HTTPS (recomendado)
- [ ] Firewall configurado (bloquear acesso não autorizado)
- [ ] Backups agendados (PostgreSQL + Redis)

## Próximas Etapas

1. **[Instalação via pip/pipx](./pip-installation.md)** — Para development local
2. **[Docker & Compose](./docker.md)** — Para VPS com containerização
3. **[VPS Deployment](./vps-deployment.md)** — Single-user ou multi-user em um servidor

## External Linking

| Conceito           | Recurso                       | Link                                                                                        |
| ------------------ | ----------------------------- | ------------------------------------------------------------------------------------------- |
| **Docker**         | Container platform            | [docker.com/docs](https://docs.docker.com/)                                                 |
| **Docker Compose** | Multi-container orchestration | [docker.com/compose](https://docs.docker.com/compose/)                                      |
| **systemd**        | Linux service management      | [freedesktop.org/wiki/Software/systemd](https://www.freedesktop.org/wiki/Software/systemd/) |
| **Nginx**          | Web server and reverse proxy  | [nginx.org/docs](https://nginx.org/en/docs/)                                                |
| **PostgreSQL**     | Database management system    | [postgresql.org](https://www.postgresql.org/)                                               |
