---
title: Backend Engineer - Weekly Routine
role: Backend Engineer
focus: FastAPI REST/MCP/JSON-RPC APIs, auth (JWT + RBAC), database integration
---

# Backend Engineer Routine

## Weekly Cadence

### Monday

- Review assigned API work (REST endpoints, MCP, JSON-RPC).
- Check auth/RBAC priorities with Security.
- Confirm test expectations with QA-Engineer.
- Sync with Backend-LLM on shared context and state management.

### Wednesday

- Implement and refine FastAPI endpoints.
- Validate Pydantic models for type safety.
- Keep code small, testable, and performant (<100ms p99).
- Test database connections (PostgreSQL, Redis, LanceDB).
- Escalate architecture questions to CTO.

### Friday

- Complete unit and integration tests (pytest).
- Verify auth/RBAC enforcement.
- Performance profiling if latency regressions detected.
- Confirm backend ready for QA and DevOps.
- Note docs work for CDO (API changes, endpoint additions).
- Coordinate with Backend-LLM on any state changes.

---

## Key Meetings

- **CTO sync**: Architecture decisions, protocol choices, performance targets.
- **Backend-LLM sync**: Shared state, context passing, tool registry.
- **QA sync**: Test coverage, regression scenarios, integration test requirements.
- **Security sync**: Auth enforcement, RBAC validation, JWT token rotation.
- **DevOps sync**: Database schema changes, migrations, infrastructure needs.

---

## Success Signals

- FastAPI server runs stably with all 3 protocols (REST, MCP, JSON-RPC).
- All endpoints return <100ms p99 latency.
- JWT auth and RBAC enforced consistently.
- Tests cover important API flows (unit + integration).
- Code remains readable, type-safe (Pydantic), and in English.
- Database connections are pooled and resilient.
- No regressions in existing endpoints.
