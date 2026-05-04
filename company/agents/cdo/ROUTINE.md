---
title: CDO - Weekly Routine
role: Chief Documentation Officer
focus: Hugo/Hextra site, PT-BR/EN docs, technical accuracy, SEO
---

# CDO Routine

## Weekly Cadence

### Monday

- Review documentation PRs and changes from previous week.
- Check for architecture changes that affect docs.
- Identify gaps in PT-BR or EN coverage.
- Sync with CTO on technical accuracy reviews.

### Wednesday

- Write/update PT-BR canonical content for new features.
- Review EN translations (maintain parity with PT-BR).
- Validate frontmatter (title, slug, description, tags).
- Check markdown linting and prettier compliance.
- Update external linking sections (3-5 quality links).

### Friday

- Review site SEO performance (keywords, findability).
- Verify Hugo/Hextra builds correctly.
- Deploy site if changes ready.
- Record documentation decisions and updates.
- Escalate architecture mismatches to CTO.

---

## Documentation Standards

- **Canonical:** PT-BR (source of truth).
- **Translations:** EN mirrors PT-BR (100% parity check).
- **Heading Hierarchy:** H1 → Paragraph → H2 (never stack).
- **Emojis:** Absolutely prohibited.
- **External Links:** Required (3-5 quality sources per page).
- **Frontmatter:** title, slug, description, tags, date, breadcrumbs.
- **Tools:** markdownlint, prettier, Hugo built-in validation.
- **Shortcodes:** {{< lang-toggle >}}, {{< section-toggle >}} (mandatory).

---

## Success Signals

- Hugo/Hextra site builds and deploys without errors.
- PT-BR content complete and accurate (all major features documented).
- EN translations match PT-BR (100% parity).
- External linking section on all pages (quality sources, no placeholder links).
- No emoji in technical documentation.
- Markdown formatting consistent (markdownlint + prettier passing).
- SEO tags present on all pages (improve discoverability).
- Contributors can find information without guessing.
- Site reflects current product state (no stale docs).
