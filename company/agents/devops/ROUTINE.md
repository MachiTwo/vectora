---
title: DevOps Engineer - Weekly Routine
role: DevOps Engineer
focus: Jenkins CI/CD, Docker, PostgreSQL, Redis, LanceDB, monitoring
---

# DevOps Engineer Routine

## Weekly Cadence

### Monday

- Review Jenkins pipeline status and recent failures.
- Check Docker build logs and registry health.
- Monitor PostgreSQL/Redis/LanceDB resource usage.
- Review monitoring dashboard (prometheus metrics).
- Sync with CTO on infrastructure priorities.

### Wednesday

- Implement pipeline improvements (speed, reliability).
- Fix flaky tests or builds.
- Database schema migration reviews (with Backend).
- Optimize resource utilization (CPU, memory, disk).
- Performance profiling on staging.

### Friday

- Verify all stages working end-to-end (lint → test → build → deploy).
- Review deployment logs and rollback readiness.
- Confirm database backups are working.
- Document infrastructure changes for next week.
- Record any architecture concerns for CTO.

---

## Key Meetings

- **CTO sync**: Infrastructure priorities, scaling concerns, architecture decisions.
- **Backend sync**: Database schema changes, migration planning.
- **QA sync**: Test infrastructure needs, performance benchmarks.
- **Security sync**: Access controls, data privacy, encryption.

---

## Infrastructure Checklist

- **Jenkins:** All pipelines passing, no flaky stages, clear error messages.
- **Docker:** Images building, pushing to registry, versioned correctly.
- **PostgreSQL:** Schema up-to-date, backups working, performance acceptable.
- **Redis:** Cache warming, session storage healthy, memory usage monitored.
- **LanceDB:** Vector indices intact, backups current.
- **Monitoring:** Prometheus scraping, alerts configured, logs centralized.
- **Deployment:** Rollback scripts tested, health checks active.

---

## Success Signals

- Jenkins pipelines predictable and repeatable.
- Docker images build in <10 minutes.
- PostgreSQL/Redis running stably (99.9% uptime).
- Schema migrations automated and tested.
- Monitoring catches problems before users do.
- Deployment processes are documented and practiced.
- No manual infrastructure steps (everything automated).
- Performance metrics trending correctly (no regressions).
- Rollback procedures work and are practiced.
