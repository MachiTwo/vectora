# Vectora Documentation Coverage Plan

**Status:** In Progress (May 2026)
**Stack:** FastAPI + LangChain + Deep Agents + PostgreSQL + Redis + LanceDB + PyTorch + React 19

## Critical Update: Stack Transition

The documentation currently reflects an **outdated architecture** (Go, MongoDB, Gemini, Voyage). This document tracks the systematic update to reflect the **current stack**.

### What Changed

| Component             | Old              | New                                | Status             |
| --------------------- | ---------------- | ---------------------------------- | ------------------ |
| **Backend**           | Go binary        | FastAPI (Python)                   | 🔴 Docs outdated   |
| **Database**          | MongoDB Atlas    | PostgreSQL + Redis + LanceDB       | 🔴 Docs outdated   |
| **LLM Orchestration** | Direct LLM calls | LangChain + Deep Agents            | 🔴 Docs missing    |
| **Cognitive Runtime** | SmolLM2          | XLM-RoBERTa-small + LoRA (PyTorch) | 🔴 Docs outdated   |
| **APIs**              | MCP-only         | REST + MCP + JSON-RPC              | 🔴 Docs incomplete |
| **Frontend**          | Unclear          | React 19 + TypeScript              | 🔴 Docs missing    |
| **CLI**               | Unclear          | Python CLI + TUI + tray            | 🔴 Docs missing    |
| **DevOps**            | Unclear          | Jenkins + Docker                   | 🔴 Docs missing    |

## Documentation Sections (Priority Order)

### Tier 1: Critical (Architecture Foundations)

#### Core Concepts (needs rewrite)

- [ ] **`/core/_index.pt.md`** - Update to FastAPI + LangChain foundation
- [ ] **`/core/agentic-framework.pt.md`** - Update to Deep Agents framework
- [ ] **`/core/context-engine.pt.md`** - Update to LanceDB + VoyageAI integration

#### Getting Started (needs rewrite)

- [ ] **`/getting-started/_index.pt.md`** - Update to FastAPI + Python stack
- [ ] **`/getting-started/installation.pt.md`** - Python setup (uv sync, CLI)
- [ ] **`/getting-started/local-deployment.pt.md`** - Docker + PostgreSQL + Redis
- [ ] **`/getting-started/first-integration.pt.md`** - MCP/REST/JSON-RPC examples

#### Models (needs rewrite)

- [ ] **`/models/_index.pt.md`** - Update to FastAPI + LangChain + VCR
- [ ] **`/models/vectora-cognitive-runtime.pt.md`** - Update to PyTorch + XLM-RoBERTa
- [ ] Delete: `/models/gemini.pt.md`, `/models/voyage/_index.pt.md` (old stack)

### Tier 2: Essential (Integration & Features)

#### LangChain Integration (expand from current)

- [x] **`/langchain/_index.pt.md`** - Core concepts (mostly current)
- [x] **`/langchain/core-concepts.pt.md`** (mostly current)
- [x] **`/langchain/deep-agents/_index.pt.md`** (mostly current)
- [x] **`/langchain/deep-agents/acp-deployment.pt.md`** (current)
- [x] **`/langchain/langgraph/memory-strategies.pt.md`** (current)
- [ ] **NEW: `/langchain/fastapi-integration.pt.md`** - How FastAPI calls LangChain
- [ ] **NEW: `/langchain/rag-pipeline-orchestration.pt.md`** - Full RAG cycle

#### Search & RAG (update for LanceDB)

- [ ] **`/search/_index.pt.md`** - Update to LanceDB + VoyageAI
- [ ] **`/search/vector-search.pt.md`** - LanceDB setup and queries
- [ ] **`/search/embeddings.pt.md`** - VoyageAI API usage
- [ ] **`/search/reranker.pt.md`** - Local XLM-RoBERTa reranking

#### Protocols (add REST + JSON-RPC)

- [ ] **`/protocols/_index.pt.md`** - Update to REST + MCP + JSON-RPC
- [x] **`/protocols/mcp.pt.md`** (mostly current)
- [x] **`/protocols/acp.pt.md`** (mostly current)
- [ ] **NEW: `/protocols/rest-api.pt.md`** - FastAPI REST endpoints
- [ ] **NEW: `/protocols/json-rpc.pt.md`** - JSON-RPC 2.0 specification

#### Architecture & Patterns (update)

- [ ] **`/patterns/_index.pt.md`** - Update to modern patterns
- [ ] **`/patterns/rag.pt.md`** - RAG with LanceDB + VoyageAI
- [x] **`/patterns/sub-agents.pt.md`** (mostly current)
- [ ] **`/patterns/trace.pt.md`** - Monitoring + observability (Prometheus)

### Tier 3: Supporting (Operations & Advanced)

#### Infrastructure & Database

- [ ] **NEW: `/backend/_index.pt.md`** - Database architecture overview
- [ ] **NEW: `/backend/postgresql.pt.md`** - PostgreSQL setup (pg8000)
- [ ] **NEW: `/backend/redis.pt.md`** - Redis setup (cache, sessions)
- [ ] **NEW: `/backend/lancedb.pt.md`** - LanceDB setup and management
- [ ] **NEW: `/devops/_index.pt.md`** - Jenkins CI/CD, Docker, deployment

#### Authentication & Security

- [ ] **NEW: `/auth/_index.pt.md`** - JWT auth, RBAC overview
- [ ] **NEW: `/auth/jwt-setup.pt.md`** - Token generation, validation, refresh
- [ ] **NEW: `/auth/rbac.pt.md`** - 5-level role hierarchy, 15 permissions
- [ ] **NEW: `/security/data-privacy.pt.md`** - Encryption, GDPR compliance
- [ ] **NEW: `/security/injection-prevention.pt.md`** - SQL injection, XSS prevention

#### Frontend & CLI

- [ ] **NEW: `/frontend/_index.pt.md`** - React 19 + TypeScript architecture
- [ ] **NEW: `/frontend/real-time-updates.pt.md`** - WebSocket/SSE integration
- [ ] **NEW: `/cli/_index.pt.md`** - Python CLI + TUI + system tray
- [ ] **NEW: `/cli/commands.pt.md`** - All CLI commands reference

#### Testing & Quality

- [ ] **NEW: `/testing/_index.pt.md`** - pytest, E2E, performance testing
- [ ] **NEW: `/testing/unit-tests.pt.md`** - Unit test patterns (pytest)
- [ ] **NEW: `/testing/integration-tests.pt.md`** - Integration test scenarios
- [ ] **NEW: `/testing/e2e-tests.pt.md`** - E2E testing with Playwright
- [ ] **NEW: `/testing/performance-benchmarks.pt.md`** - Latency targets

### Tier 4: Reference & Appendix

#### Reference (update)

- [ ] **`/reference/_index.pt.md`** - Update tool references
- [ ] **`/reference/mcp-tools.pt.md`** - MCP tool registry (update)
- [ ] **NEW: `/reference/rest-api-reference.pt.md`** - All REST endpoints
- [ ] **NEW: `/reference/json-rpc-reference.pt.md`** - JSON-RPC methods

#### Troubleshooting & FAQ

- [ ] **NEW: `/troubleshooting/_index.pt.md`** - Common issues
- [ ] **NEW: `/faq/_index.pt.md`** - FAQ

#### Contribution & Roadmap

- [ ] **NEW: `/contributing/guidelines.pt.md`** - Contribution guidelines
- [ ] **NEW: `/contributing/roadmap.pt.md`** - Public roadmap

## Documentation Rules (from AGENTS.md)

1. **Canonical:** PT-BR only (source of truth)
2. **Translations:** EN mirrors PT-BR (100% parity)
3. **Heading Hierarchy:** H1 → Paragraph → H2 (never stack)
4. **Emojis:** Absolutely prohibited
5. **External Links:** Required (3-5 quality sources per page)
6. **Frontmatter:** title, slug, description, tags, date, breadcrumbs
7. **Shortcodes:** `{{< lang-toggle >}}`, `{{< section-toggle >}}` (mandatory)

## Translation Strategy

For each NEW page:

1. Write PT-BR version (`.pt.md`) first
2. Immediately create EN version (`.en.md`) with same content
3. Both versions must stay in sync
4. Use git commits to track both versions together

Example:

```
/backend/postgresql.pt.md  (Portuguese, canonical)
/backend/postgresql.en.md  (English, translated)
```

## Timeline

| Tier                    | Expected           | Status         |
| ----------------------- | ------------------ | -------------- |
| **Tier 1 (Critical)**   | Week 1-2           | 🟡 In Progress |
| **Tier 2 (Essential)**  | Week 3-4           | ⚪ Pending     |
| **Tier 3 (Supporting)** | Week 5-6           | ⚪ Pending     |
| **Tier 4 (Reference)**  | Week 7-8           | ⚪ Pending     |
| **Translation (EN)**    | Ongoing (parallel) | ⚪ Pending     |

## Files to Delete (Old Stack)

These files are outdated and should be removed once replacements are in place:

- ❌ `/models/gemini.pt.md` (Gemini-specific, old stack)
- ❌ `/models/voyage/_index.pt.md` (Voyage-specific embedding doc, superseded)
- ❌ `/backend/mongodb-atlas.pt.md` (old stack)

## Quick Reference: Old vs New

| Old Path                       | New Path                                                                      | Status         |
| ------------------------------ | ----------------------------------------------------------------------------- | -------------- |
| `/models/gemini.pt.md`         | Merged into `/langchain/_index.pt.md`                                         | 🟡 TBD         |
| `/backend/mongodb-atlas.pt.md` | `/backend/postgresql.pt.md`, `/backend/redis.pt.md`, `/backend/lancedb.pt.md` | ⚪ Not started |
| (missing)                      | `/protocols/rest-api.pt.md`                                                   | ⚪ Not started |
| (missing)                      | `/protocols/json-rpc.pt.md`                                                   | ⚪ Not started |
| (missing)                      | `/frontend/_index.pt.md`                                                      | ⚪ Not started |
| (missing)                      | `/cli/_index.pt.md`                                                           | ⚪ Not started |
| (missing)                      | `/devops/_index.pt.md`                                                        | ⚪ Not started |

## Next Steps

1. **Update Tier 1 (Critical)** - This week

   - Rewrite core concepts to FastAPI + LangChain
   - Update getting started (installation, local deployment)
   - Rewrite models section (VCR, FastAPI stack)

2. **Expand Tier 2 (Essential)** - Next week

   - Add REST + JSON-RPC protocol docs
   - Update search section (LanceDB instead of MongoDB)
   - Add RAG pipeline orchestration docs

3. **Create Tier 3 (Supporting)** - Weeks 3-4

   - New infrastructure docs (PostgreSQL, Redis, LanceDB)
   - New auth/security docs (JWT, RBAC)
   - New frontend/CLI docs

4. **Translations** - Parallel with all tiers
   - EN versions created alongside PT-BR
   - 100% parity check before publishing

---

**Owner:** CDO (Chief Documentation Officer)
**Last Updated:** 2026-05-03
