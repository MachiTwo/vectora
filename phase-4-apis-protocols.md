# Phase 4: APIs & Protocols (REST, MCP, JSON-RPC)

**Objetivo**: Implementar múltiplas camadas de API (REST, MCP, JSON-RPC) com autenticação, autorização e integração com editores.

**Status**: Análise inicial
**Duração estimada**: 4-5 semanas

## Objectives

1. HTTP Server com FastAPI (REST API)
2. MCP (Model Context Protocol) server nativo
3. JSON-RPC 2.0 para chamadas síncronas
4. JWT authentication + RBAC
5. Integração com editores (VS Code, JetBrains, Zed)

## Key Tasks

### 4.1 HTTP Server & REST API

- [ ] Configurar FastAPI com routers modulares
- [ ] Endpoints base (/search, /analyze, /chat, /health)
- [ ] Middleware stack (CORS, logging, error handling)
- [ ] Rate limiting e throttling
- [ ] Request/response validation (Pydantic)
- [ ] OpenAPI/Swagger documentation

### 4.2 Authentication & Authorization

- [ ] JWT token generation e validation
- [ ] Refresh token rotation
- [ ] RBAC com 5 níveis hierárquicos
- [ ] Permissions mapping (15+ permissions)
- [ ] API key derivation para automação
- [ ] Multi-tenant isolation (buckets privados)

### 4.3 MCP Server Implementation

- [ ] MCP protocol implementation (stdin/stdout)
- [ ] Tool registry (VCR analyze, search, execute)
- [ ] Resource handling
- [ ] Streaming responses
- [ ] Error handling e validation

### 4.4 JSON-RPC 2.0 Support

- [ ] JSON-RPC endpoint (POST /rpc)
- [ ] Batch request handling
- [ ] Method routing
- [ ] Error responses (standard JSON-RPC errors)
- [ ] Notification support (async)

### 4.5 Editor Integrations

- [ ] VS Code extension scaffolding
- [ ] JetBrains plugin integration
- [ ] Zed extension support
- [ ] ACP protocol implementation
- [ ] Real-time sync (file changes, selections)

### 4.6 Monitoring & Observability

- [ ] Prometheus metrics (requests, latency, errors)
- [ ] Structured logging (JSON format)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Health check endpoints (/health, /ready)
- [ ] Liveness & readiness probes

### 4.7 Testing & Security

- [ ] Unit tests para endpoints
- [ ] Integration tests com múltiplas clients
- [ ] Security tests (JWT validation, RBAC enforcement)
- [ ] Load testing (target: 1000 req/s)
- [ ] Penetration testing basics

## Dependencies

- FastAPI 0.100+
- pyjwt (JWT handling)
- python-multipart (form parsing)
- httpx (client testing)
- prometheus-client (metrics)
- opentelemetry (tracing)

## Acceptance Criteria

- ✅ REST API endpoints respondendo
- ✅ JWT auth funcionando (tokens válidos/expirados)
- ✅ RBAC enforcement em todos endpoints
- ✅ MCP server integrado (stdin/stdout)
- ✅ JSON-RPC endpoint operacional
- ✅ VS Code extension básico funcional
- ✅ Latency <100ms (p99) para endpoints
- ✅ Testes passam com >80% coverage

## Notes

- Autenticação é crítica (privacidade de dados)
- MCP integration é para editor compatibility
- RBAC deve ser granular (futuros add-ons)
- Monitoring essencial para production readiness
- Não confundir MCP com JSON-RPC (protocolos diferentes)
