---
title: Backend-LLM Engineer - Weekly Routine
role: Backend-LLM Engineer
focus: LangChain + Deep Agents, planning, RAG orchestration, latency <500ms
---

# Backend-LLM Engineer Routine

## Weekly Cadence

### Monday

- Review LangChain/Deep Agents priorities with CTO.
- Check RAG pipeline performance (search → rerank → context → LLM).
- Sync with Backend on API contracts and shared state.
- Sync with AI-ML on VCR analysis latency.
- Review latency metrics (target: <500ms for full cycle).

### Wednesday

- Implement planning engine improvements.
- Add/refine tool executor flows.
- Test state management and memory strategies.
- Validate RAG pipeline end-to-end (local benchmarks).
- Performance profiling if regressions detected.

### Friday

- Review code quality and test coverage (pytest).
- Verify streaming and async behavior.
- Confirm RAG pipeline stability.
- Note docs work for CDO (API changes, new tools, RAG flows).
- Escalate architecture concerns to CTO.

---

## Key Meetings

- **CTO sync**: Architecture, LangChain choices, performance targets.
- **Backend sync**: API contracts, context passing, shared state.
- **AI-ML sync**: VCR analysis integration, embedding caching.
- **QA sync**: RAG pipeline test coverage, end-to-end scenarios.

---

## Success Signals

- Deep Agents planning engine breaks tasks into subtasks reliably.
- Tool executor routes and executes tools without errors.
- Full RAG cycle completes in <500ms (search + rerank + context + LLM call).
- Conversation state managed correctly (truncate, delete, summarize).
- Streaming responses work end-to-end.
- VCR integration latency <50ms (not blocking).
- Code is testable, maintainable, and in English.
- No regressions in RAG pipeline quality or latency.
