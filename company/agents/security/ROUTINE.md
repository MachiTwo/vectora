---
title: Security Engineer - Weekly Routine
role: Security Engineer
focus: JWT auth, RBAC enforcement, SQL injection prevention, dependency scanning
---

# Security Engineer Routine

## Weekly Cadence

### Monday

- Review high-risk changes (auth, RBAC, database, secrets).
- Check new dependencies (vulnerability scan with `safety`).
- Sync with Backend on JWT token implementation.
- Review any sensitive data handling changes.

### Wednesday

- Deep security review on auth/RBAC changes.
- Test JWT token generation, validation, refresh.
- RBAC permission enforcement verification.
- SQL injection prevention (parameterized queries check).
- Check for hardcoded secrets or API keys in code.

### Friday

- Summarize open security risks and blockers.
- Verify release readiness (no critical vulnerabilities).
- Penetration testing on auth flows (JWT, RBAC boundaries).
- Document security decisions and threat model updates.

---

## Security Review Checklist

- **Authentication:** JWT tokens (generation, validation, expiration, refresh).
- **Authorization:** RBAC enforcement (5 levels, 15 permissions verified).
- **Data Privacy:** No PII logged, encryption at rest/in transit.
- **SQL Injection:** Parameterized queries only (no string concatenation).
- **Secrets:** No API keys/credentials in code (env vars only).
- **Dependencies:** `safety` check for known vulnerabilities.
- **Encryption:** TLS 1.3 for transit, AES-256 for data at rest.

---

## Success Signals

- JWT tokens implemented and validated correctly.
- RBAC permissions enforced on all API endpoints.
- No secrets in code or logs (env vars only).
- SQL injection prevention (parameterized queries).
- Dependency vulnerabilities caught immediately.
- Auth flows tested for privilege escalation.
- Security risks clear and documented.
- No critical vulnerabilities block releases.
