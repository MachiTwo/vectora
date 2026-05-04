# Phase 1: Foundation & Deep Agents Integration

**Objetivo**: Estabelecer a base do Vectora com FastAPI, integrar o framework Deep Agents e configurar a camada de persistência.

**Status**: Análise inicial
**Duração estimada**: 2-3 semanas

## Objectives

1. Configurar projeto FastAPI com estrutura modular (internal/ com tiers)
2. Integrar Deep Agents como framework base
3. Implementar camada de armazenamento (PostgreSQL + Redis + LanceDB)
4. CLI scaffolding com UV
5. Testes e CI/CD básicos

## Key Tasks

### 1.1 FastAPI Project Setup

- [ ] Criar estrutura de diretórios (internal/, tests/, vectora-website/)
- [ ] Configurar pyproject.toml com dependências principais
- [ ] Setup de UV para package management
- [ ] Configurar estrutura de tiers (config, platform, storage, llm, core, tools, api, shared)
- [ ] Pre-commit hooks (ruff, prettier, markdownlint)

### 1.2 Deep Agents Integration

- [ ] Clone/integração do Deep Agents monorepo
- [ ] Setup de Agent harness base
- [ ] Configurar Planning Engine
- [ ] Implementar Tool Executor base

### 1.3 Storage Layer (PostgreSQL + Redis + LanceDB)

- [ ] PostgreSQL embedded via pg8000
- [ ] Redis embedded para cache/sessions
- [ ] LanceDB para vector storage
- [ ] Migrations system para schemas
- [ ] Connection pooling e health checks

### 1.4 CLI Foundation

- [ ] CLI entry point via UV
- [ ] Comandos básicos (init, start, status)
- [ ] Integration com tray module (Windows system tray)
- [ ] Logging e error handling

### 1.5 Testing & CI

- [ ] Setup pytest com fixtures
- [ ] Unit tests para storage layer
- [ ] Integration tests para Deep Agents harness
- [ ] GitHub Actions workflow básico

## Dependencies

- FastAPI 0.100+
- Deep Agents (LangChain monorepo)
- Pydantic v2 (type safety)
- SQLAlchemy + pg8000 (PostgreSQL embedded)
- Redis (embedded ou local)
- LanceDB
- pytest
- ruff

## Acceptance Criteria

- ✅ FastAPI server inicia sem erros
- ✅ Deep Agents harness integrado e funcional
- ✅ PostgreSQL/Redis/LanceDB conectados e testados
- ✅ CLI commands (init, start, status) funcionam
- ✅ Testes passam (pytest)
- ✅ Ruff lint/format passam
- ✅ Git hooks validam commits

## Notes

- Usar Python 3.10+ (type hints)
- Código em inglês; documentação em PT-BR (Hugo/Hextra)
- Priorizar estrutura modular para escalabilidade futura
- Tray module é CRÍTICO para Windows local mode (não remover)
