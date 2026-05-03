vectora-website/content/
├── _index.pt.md                          (Visão geral)
│
├── getting-started/
│   ├── _index.pt.md
│   ├── installation.pt.md
│   ├── first-integration.pt.md
│   └── local-deployment.pt.md
│
├── architecture/
│   ├── _index.pt.md
│   ├── single-app-model.pt.md
│   ├── agent-complete.pt.md
│   └── data-flow.pt.md
│
├── langchain/                            [Core framework + Deep Agents]
│   ├── _index.pt.md                     (LangChain overview)
│   ├── core-concepts.pt.md
│   │   ├── runnables.pt.md              (Chains, runnables)
│   │   ├── tools.pt.md                  (Tool definition + use)
│   │   ├── memory.pt.md                 (Memory systems)
│   │   └── retrieval.pt.md              (RAG via LangChain)
│   │
│   ├── langgraph/
│   │   ├── _index.pt.md                 (What is LangGraph)
│   │   ├── graph-basics.pt.md           (Nodes, edges, state)
│   │   ├── agent-loop.pt.md             (Agent decision loop)
│   │   ├── error-handling.pt.md         (Recovery, retries)
│   │   └── vectora-agent-example.pt.md  (How Vectora uses LangGraph)
│   │
│   ├── langsmith/
│   │   ├── _index.pt.md                 (Tracing & debugging)
│   │   ├── setup.pt.md                  (Enable LangSmith)
│   │   ├── trace-queries.pt.md          (Trace agent decisions)
│   │   └── performance-monitoring.pt.md (Monitor latency, tokens)
│   │
│   ├── deep-agents/                     [Deep Agents framework]
│   │   ├── _index.pt.md                 (Deep Agents overview)
│   │   ├── cli.pt.md                    (Deep Agents CLI - init, config, start, stop, logs)
│   │   ├── providers.pt.md              (LLM Providers setup)
│   │   ├── memory.pt.md                 (Memory management & persistence)
│   │   ├── streaming.pt.md              (Streaming responses)
│   │   ├── data-locations.pt.md         (Data storage locations)
│   │   └── tui.pt.md                    (Terminal UI usage)
│   │
│   └── integration-patterns.pt.md
│       ├── pre-thinking-vcr.pt.md       (VCR → LangChain flow)
│       ├── multi-llm-routing.pt.md      (LLM selection)
│       └── tool-composition.pt.md       (Complex tool chains)
│
├── models/                               [LLM options + embeddings + VCR]
│   ├── _index.pt.md                     (Models overview)
│   │
│   ├── llms/
│   │   ├── claude-anthropic.pt.md       (Primary)
│   │   ├── gemini-google.pt.md
│   │   └── openai-gpt.pt.md
│   │
│   ├── voyage/                          [100% Voyage - embeddings, reranking, vector search]
│   │   ├── _index.pt.md                 (Voyage overview)
│   │   ├── embeddings.pt.md             (Embedding generation)
│   │   ├── reranking.pt.md              (Reranking - remote & local files)
│   │   └── vector-search.pt.md          (Vector search integration)
│   │
│   └── vcr/                             [Vectora Cognitive Runtime]
│       ├── _index.pt.md                 (What is VCR)
│       ├── architecture.pt.md           (XLM-RoBERTa + LoRA)
│       ├── training.pt.md               (Synthetic → Real traces)
│       ├── integration.pt.md            (VCR → LangChain flow)
│       └── fine-tuning.pt.md            (Phase 2+ optimization)
│
├── patterns/
│   ├── _index.pt.md
│   ├── rag-with-langchain.pt.md         (Vector search pattern)
│   ├── agent-workflow.pt.md             (LangGraph patterns)
│   ├── tool-use.pt.md                   (LangChain tools)
│   ├── multi-llm-routing.pt.md
│   ├── sub-agents.pt.md
│   └── trace-analysis.pt.md
│
├── storage/
│   ├── _index.pt.md
│   ├── postgresql.pt.md
│   ├── redis-memory.pt.md
│   └── lancedb-vectors.pt.md
│
├── protocols/
│   ├── _index.pt.md
│   ├── mcp-protocol.pt.md
│   ├── json-rpc.pt.md
│   ├── rest-api.pt.md
│   ├── websocket.pt.md
│   ├── acp.pt.md                        (Agent Client Protocol)
│   └── deep-agents-acp.pt.md            (Deep Agents ACP implementation)
│
├── backend/
│   ├── _index.pt.md
│   ├── fastapi-structure.pt.md          (Project layout)
│   ├── langchain-setup.pt.md
│   │   ├── chains.pt.md
│   │   ├── agents.pt.md
│   │   └── memory-integration.pt.md
│   ├── database-layer.pt.md
│   └── middleware-stack.pt.md
│
├── deployment/
│   ├── _index.pt.md
│   ├── docker.pt.md
│   ├── pip-installation.pt.md
│   ├── pipx-installation.pt.md
│   └── vps-deployment.pt.md
│
├── devops/                              [CI/CD, Containerization, Security]
│   ├── _index.pt.md                     (DevOps overview)
│   │
│   ├── docker/
│   │   ├── _index.pt.md                 (Docker setup for Vectora)
│   │   ├── dockerfile.pt.md             (Building images)
│   │   ├── compose.pt.md                (Docker Compose setup)
│   │   └── vps-deployment.pt.md         (Single-user VPS deployment)
│   │
│   ├── ci-cd/
│   │   ├── _index.pt.md                 (CI/CD overview)
│   │   ├── github-actions.pt.md         (GitHub Actions workflows)
│   │   ├── jenkins.pt.md                (Jenkins pipelines)
│   │   └── automated-testing.pt.md      (Test automation)
│   │
│   ├── security/
│   │   ├── _index.pt.md                 (Security overview)
│   │   ├── secrets-management.pt.md     (Env vars, API keys)
│   │   ├── hardening.pt.md              (Container/app hardening)
│   │   ├── ssl-tls.pt.md                (SSL/TLS certificates for VPS)
│   │   └── access-control.pt.md         (Network security, firewall)
│   │
│   └── multi-user/                      [Multi-user VPS setup & Paperclip integration]
│       ├── _index.pt.md                 (Multi-user overview)
│       ├── authentication.pt.md         (JWT token system, login flow)
│       ├── user-management.pt.md        (Creating users, token generation)
│       ├── session-management.pt.md     (JWT refresh, session validation)
│       ├── buckets-permissions.pt.md    (Public/private buckets per user)
│       ├── paperclip-integration.pt.md  (Paperclip agents → Vectora authentication)
│       └── vps-multi-tenant.pt.md       (VPS with multiple users/agents)
│
├── observability/                       [Monitoring, Logging, Metrics]
│   ├── _index.pt.md                     (Observability overview)
│   ├── logging.pt.md                    (Structured logging)
│   ├── metrics.pt.md                    (Prometheus, metrics collection)
│   ├── tracing.pt.md                    (Distributed tracing)
│   ├── langsmith-integration.pt.md      (LangSmith setup & usage)
│   └── alerting.pt.md                   (Alert rules & notifications)
│
├── testing/                             [Unit, Integration, E2E Tests]
│   ├── _index.pt.md                     (Testing overview)
│   ├── unit-tests.pt.md                 (Pytest, unit testing)
│   ├── integration-tests.pt.md          (API, database integration tests)
│   ├── e2e-tests.pt.md                  (End-to-end test scenarios)
│   ├── mocking.pt.md                    (Mocks, fixtures, test data)
│   └── performance-testing.pt.md        (Load, stress, benchmark tests)
│
├── asset-library/                       [VAL - Vectora Asset Library (Dataset Registry)]
│   ├── _index.pt.md                     (What is VAL, registry overview)
│   ├── datasets-overview.pt.md          (Dataset packages structure)
│   ├── downloading-datasets.pt.md       (CLI: vectora val download <dataset-name>)
│   ├── dataset-metadata.pt.md           (metadata.json format & standards)
│   ├── agent-system-prompts.pt.md       (AGENTS.md for dataset-specific prompts)
│   ├── vector-format.pt.md              (LanceDB vectors.lance format)
│   ├── examples-documentation.pt.md     (Writing examples for datasets)
│   ├── contributing/
│   │   ├── _index.pt.md                 (Contributing to VAL)
│   │   ├── dataset-creation.pt.md       (How to create a dataset)
│   │   ├── validation-process.pt.md     (CI validation, checksums, structure)
│   │   ├── github-workflow.pt.md        (Fork, PR, merge, release process)
│   │   └── testing-datasets.pt.md       (Local testing before submission)
│   │
│   ├── registry-api.pt.md               (REST API for registry access)
│   ├── community-ratings.pt.md          (GitHub reactions, dataset popularity)
│   └── publishing-releases.pt.md        (GitHub releases, version management)
│
├── integrations/                        [SDKs, IDE Plugins, MCP Servers, External Tools]
│   ├── _index.pt.md                     (Integrations overview & @vectora-integrations monorepo)
│   │
│   ├── sdks/                            [@vectora-integrations Turborepo Packages]
│   │   ├── _index.pt.md                 (SDKs overview - @vectora/sdk-*)
│   │   ├── installing-sdks.pt.md        (npm install @vectora/sdk-claude-code, etc)
│   │   ├── shared-package.pt.md         (@vectora/shared - types, auth, HTTP client)
│   │   │
│   │   ├── sdk-claude-code.pt.md        (@vectora/sdk-claude-code - MCP protocol)
│   │   ├── sdk-gemini-cli.pt.md         (@vectora/sdk-gemini-cli - REST adapter)
│   │   ├── sdk-paperclip.pt.md          (@vectora/sdk-paperclip - Plugin + MCP/REST bridges)
│   │   ├── sdk-hermes.pt.md             (@vectora/sdk-hermes - REST adapter)
│   │   └── sdk-custom-template.pt.md    (Custom agent SDK template)
│   │
│   ├── ide-extensions/
│   │   ├── _index.pt.md                 (IDE extensions overview)
│   │   ├── vscode-extension.pt.md       (Claude Code / VSCode via @vectora/sdk-claude-code)
│   │   ├── jetbrains-extension.pt.md    (JetBrains IDEs integration)
│   │   ├── cursor-integration.pt.md     (Cursor editor setup)
│   │   └── vim-neovim.pt.md             (Vim/Neovim integration)
│   │
│   ├── mcp-servers/
│   │   ├── _index.pt.md                 (MCP servers overview)
│   │   ├── building-mcp-server.pt.md    (Custom MCP server development)
│   │   ├── vectora-mcp-tools.pt.md      (Vectora as MCP server)
│   │   ├── mcp-tool-discovery.pt.md     (Discovering MCP tools)
│   │   └── popular-mcp-servers.pt.md    (Integration with npm, github, slack MCPs)
│   │
│   ├── external-services/
│   │   ├── _index.pt.md                 (External service integrations)
│   │   ├── slack-integration.pt.md      (Slack bot via Vectora)
│   │   ├── github-integration.pt.md     (GitHub Actions + Vectora)
│   │   ├── webhooks-http.pt.md          (HTTP callbacks & webhooks)
│   │   └── rest-api-clients.pt.md       (Direct REST API usage)
│   │
│   ├── agent-protocols/
│   │   ├── _index.pt.md                 (Agent-to-agent communication)
│   │   ├── acp-server-mode.pt.md        (Running Vectora as ACP server)
│   │   ├── sub-agent-pattern.pt.md      (Vectora as sub-agent in Paperclip)
│   │   ├── multi-agent-workflows.pt.md  (Multiple agents collaborating via Vectora)
│   │   └── token-based-auth.pt.md       (JWT tokens for agent authentication)
│   │
│   └── asset-library-integration.pt.md  (Using VAL datasets in custom agents)
│
├── reference/
│   ├── _index.pt.md
│   ├── api-endpoints.pt.md
│   ├── cli-reference.pt.md              (Deep Agents CLI reference)
│   └── configuration.pt.md
│
└── concepts/
    ├── _index.pt.md
    ├── agent-complete.pt.md
    ├── context-enrichment.pt.md
    ├── local-first.pt.md
    └── specialized-vs-generalist.pt.md
