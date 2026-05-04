---
title: Integrations Engineer - Weekly Routine
role: Integrations Engineer
focus: ACP/JSON-RPC protocols, VS Code/JetBrains/Zed extensions, editor-side sync
---

# Integrations Engineer Routine

## Weekly Cadence

### Monday

- Review editor integration priorities (VS Code, JetBrains, Zed).
- Check protocol changes (ACP, JSON-RPC, MCP).
- Sync with Backend-LLM on tool registry and command mapping.
- Test real-time file sync mechanism.

### Wednesday

- Implement or refine extension features (TypeScript, Kotlin).
- Test ACP protocol communication (stdin/stdout).
- Validate JSON-RPC 2.0 client behavior.
- E2E test in actual editors (VS Code, JetBrains, Zed).
- Verify authentication inheritance from Backend JWT.

### Friday

- Review plugin readiness and compatibility.
- Test plugin distribution (Marketplace, Plugin Repository).
- Verify versioning and semantic versioning.
- Flag docs/release work for CDO and DevOps.

---

## Protocol & Integration Standards

- **ACP:** Agent Client Protocol (stdin/stdout communication).
- **JSON-RPC 2.0:** Synchronous method calls (error handling, batch requests).
- **MCP:** Model Context Protocol (tool discovery, resource access).
- **Versioning:** Semantic versioning (MAJOR.MINOR.PATCH).
- **Compatibility:** Never break existing plugins (backward compatibility sacred).

---

## Editor Integrations Checklist

- **VS Code:** TypeScript extension, ACP client, real-time sync, marketplace distribution.
- **JetBrains:** Kotlin plugin, ACP client, IDE integration, plugin repository.
- **Zed:** Rust/TypeScript extension, ACP client, Zed plugin registry.
- **Authentication:** Inherit JWT from Backend (no separate login in editor).
- **File Sync:** Detect editor changes, sync state bidirectionally.
- **Tool Discovery:** Auto-discover available tools from tool registry.

---

## Success Signals

- ACP protocol communication working in all 3 editors.
- JSON-RPC 2.0 client handling requests correctly.
- Real-time file sync latency <100ms.
- Plugins distributed in all 3 marketplaces.
- Authentication inherited (no separate login needed).
- Backward compatibility maintained (no breaking changes).
- E2E tests passing in all editors.
- User workflow predictable and reliable.
