---
title: QA Engineer - Weekly Routine
role: QA Engineer
focus: pytest coverage >80%, E2E tests, performance, security testing
---

# QA Engineer Routine

## Weekly Cadence

### Monday

- Review incoming PRs and identify test gaps.
- Check CI test results and flaky test patterns.
- Sync with Backend on testability concerns.
- Review coverage metrics (pytest, E2E).

### Wednesday

- Write/refine pytest unit tests (>80% coverage).
- Write/refine E2E tests (critical flows).
- Performance profiling (latency, throughput benchmarks).
- Security testing (OWASP, JWT, RBAC, injection).
- Investigate and fix flaky tests immediately.

### Friday

- Review quality metrics (coverage, performance, security).
- Validate release readiness from QA perspective.
- Document test gaps and risks.
- Record anything blocking a release.
- Performance regression analysis.

---

## Key Meetings

- **CTO sync**: Test strategy, coverage targets, release blockers.
- **Backend sync**: API testability, integration test scenarios.
- **Frontend sync**: E2E test coverage, accessibility testing.
- **DevOps sync**: CI pipeline, test infrastructure, Jenkins stages.
- **Security sync**: Security test coverage, OWASP compliance.

---

## Quality Standards

- **Unit Test Coverage:** >80% (pytest).
- **Integration Tests:** Critical paths (API endpoints, RAG pipeline).
- **E2E Tests:** Main user workflows (search, analyze, chat).
- **Performance:** API latency <100ms (p99), throughput 1000 req/s.
- **Security:** JWT validation, RBAC enforcement, no SQL injection.
- **Accessibility:** WCAG 2.1 AA compliance.
- **No Flaky Tests:** Zero tolerance, investigate immediately.

---

## Success Signals

- pytest coverage >80% (unit tests protect logic).
- E2E tests cover main workflows (no regressions).
- Performance benchmarks stable (no latency regressions).
- Security tests catch common vulnerabilities.
- CI is trustworthy (low false positives).
- Flaky tests eliminated immediately.
- No critical regressions escape to production.
- Team confident in shipping.
