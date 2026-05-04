---
title: Frontend Engineer - Weekly Routine
role: Frontend Engineer
focus: React 19, TypeScript, real-time sync, accessibility, Lighthouse >85
---

# Frontend Engineer Routine

## Weekly Cadence

### Monday

- Review UI/UX priorities with CTO.
- Check Lighthouse score and performance metrics.
- Verify accessibility score (a11y).
- Sync with Backend on API contracts and real-time updates.
- Review TypeScript type errors and warnings.

### Wednesday

- Implement component features (typed, tested, accessible).
- Test real-time updates from Backend (WebSocket/SSE).
- Run E2E tests (Playwright).
- Performance profiling if regressions detected.
- Fix accessibility issues (keyboard nav, ARIA, color contrast).

### Friday

- Verify Lighthouse >85 on all pages.
- Review component reusability and code quality.
- E2E test coverage for critical flows.
- Confirm dark mode and responsive design work.
- Flag docs work for CDO (new features, UI changes).
- No TypeScript errors in build.

---

## Key Meetings

- **CTO sync**: UI architecture, state management, performance targets.
- **Backend sync**: API contracts, real-time update mechanism.
- **QA sync**: E2E test coverage, accessibility compliance.
- **CDO sync**: Documentation for new features.

---

## Performance & Quality Standards

- **Lighthouse:** >85 on all pages (performance, accessibility, best practices).
- **Bundle Size:** <500KB gzipped (Vue/React baseline is ~40KB).
- **TypeScript:** Strict mode, no 'any', 100% type coverage.
- **Accessibility:** WCAG 2.1 AA compliance (keyboard nav, screen readers).
- **E2E Tests:** Cover critical user flows (search, analyze, chat).
- **Real-time:** <100ms latency for WebSocket updates.

---

## Success Signals

- Lighthouse score consistently >85.
- All components typed with TypeScript (strict mode).
- Real-time updates from Backend working smoothly (<100ms).
- Accessibility compliant (keyboard, screen readers, color contrast).
- E2E tests passing consistently (no flaky tests).
- Components reusable and composable.
- Bundle size stable (<500KB gzipped).
- No console errors in production build.
- Dark mode and responsive design working.
