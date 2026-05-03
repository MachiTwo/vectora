import os
import re
import sys

# Mapeamento de termos-chave (regex ou string) para Links Externos
# Formato: Termo -> (Concept, Resource, Link)
LINK_KNOWLEDGE_BASE = {
    r"\bOAuth( 2\.0)?\b": (
        "OAuth 2.0",
        "RFC 6749: The OAuth 2.0 Authorization Framework",
        "https://datatracker.ietf.org/doc/html/rfc6749",
    ),
    r"\bJWT\b|\bJSON Web Token\b": (
        "JWT",
        "RFC 7519: JSON Web Token Standard",
        "https://datatracker.ietf.org/doc/html/rfc7519",
    ),
    r"\bOIDC\b|\bOpenID Connect\b": (
        "OpenID Connect",
        "OIDC Core 1.0 Specification",
        "https://openid.net/specs/openid-connect-core-1_0.html",
    ),
    r"\bWebAuthn\b": (
        "WebAuthn",
        "Web Authentication: Public Key Credentials",
        "https://www.w3.org/TR/webauthn-2/",
    ),
    r"\bRBAC\b": (
        "RBAC",
        "NIST Role-Based Access Control Standard",
        "https://csrc.nist.gov/projects/rbac",
    ),
    r"\bOWASP\b": (
        "Secure Coding",
        "OWASP Secure Coding Practices",
        "https://owasp.org/www-project-secure-coding-practices/",
    ),
    r"\bZero Trust\b": (
        "Zero Trust",
        "NIST SP 800-207 Zero Trust Architecture",
        "https://csrc.nist.gov/publications/detail/sp/800-207/final",
    ),
    r"\bRAG\b": (
        "RAG",
        "Retrieval-Augmented Generation for Knowledge-Intensive NLP",
        "https://arxiv.org/abs/2005.11401",
    ),
    r"\bHNSW\b": (
        "HNSW",
        "Efficient and robust approximate nearest neighbor search",
        "https://arxiv.org/abs/1603.09320",
    ),
    r"\bAST\b|\btree-sitter\b": (
        "AST Parsing",
        "Tree-sitter Official Documentation",
        "https://tree-sitter.github.io/tree-sitter/",
    ),
    r"\bFlash Attention\b": (
        "Flash Attention",
        "Fast and Memory-Efficient Exact Attention",
        "https://arxiv.org/abs/2205.14135",
    ),
    r"\bTransformer\b|\bKV Cache\b": (
        "Transformer Architecture",
        "Attention Is All You Need",
        "https://arxiv.org/abs/1706.03762",
    ),
    r"\bMongoDB\b|\bAtlas\b": (
        "MongoDB Atlas",
        "Atlas Vector Search Documentation",
        "https://www.mongodb.com/docs/atlas/atlas-vector-search/",
    ),
    r"\bBSON\b": ("BSON Spec", "Binary JSON Specification", "https://bsonspec.org/"),
    r"\bQdrant\b": (
        "Qdrant",
        "Vector Database Documentation",
        "https://qdrant.tech/documentation/",
    ),
    r"\bSupabase\b": (
        "Supabase",
        "Open Source Firebase Alternative",
        "https://supabase.com/docs",
    ),
    r"\bVercel\b": (
        "Vercel",
        "Vercel Platform Documentation",
        "https://vercel.com/docs",
    ),
    r"\bMCP\b|\bModel Context Protocol\b": [
        (
            "MCP",
            "Model Context Protocol Specification",
            "https://modelcontextprotocol.io/specification",
        ),
        (
            "MCP Go SDK",
            "Go SDK for MCP (mark3labs)",
            "https://github.com/mark3labs/mcp-go",
        ),
    ],
    r"\bAxios\b": (
        "HTTP Client",
        "Axios Documentation",
        "https://axios-http.com/",
    ),
    r"\bTypeScript\b": (
        "TypeScript",
        "Official TypeScript Handbook",
        "https://www.typescriptlang.org/docs/",
    ),
    r"\bREST( API)?\b": (
        "REST API Design",
        "RESTful API Best Practices",
        "https://restfulapi.net/",
    ),
    r"\bExponential Backoff\b": (
        "Exponential Backoff",
        "AWS Retry Strategy Guide",
        "https://docs.aws.amazon.com/general/latest/gr/api-retries.html",
    ),
    r"\bGemini( AI)?\b": (
        "Gemini AI",
        "Google DeepMind Gemini Models",
        "https://deepmind.google/technologies/gemini/",
    ),
    r"\bVoyage( AI)?\b": (
        "Voyage AI",
        "High-performance embeddings for RAG",
        "https://www.voyageai.com/",
    ),
    r"\bHTTP Status Codes\b": (
        "HTTP Status Codes",
        "Standard HTTP status code reference",
        "https://httpwg.org/specs/rfc9110.html#status.codes",
    ),
    r"\bVSCode Extension API\b": (
        "VSCode Extension API",
        "Official VSCode extension documentation",
        "https://code.visualstudio.com/api",
    ),
    r"\bWebView Panel\b": (
        "WebView Panel Guide",
        "Creating UI panels in VSCode",
        "https://code.visualstudio.com/api/extension-guides/webview",
    ),
    r"\bCommands API\b": (
        "Commands API",
        "Implementing custom commands in VSCode",
        "https://code.visualstudio.com/api/extension-guides/command",
    ),
    r"\bJSON-RPC\b": (
        "JSON-RPC",
        "JSON-RPC 2.0 Specification",
        "https://www.jsonrpc.org/specification",
    ),
    r"\bOpenAPI\b": (
        "OpenAPI",
        "OpenAPI Specification",
        "https://swagger.io/specification/",
    ),
    r"\bGemini\b": (
        "Gemini API",
        "Google AI Studio Documentation",
        "https://ai.google.dev/docs",
    ),
    r"\bVoyage\b": [
        (
            "Voyage Embeddings",
            "Voyage Embeddings Documentation",
            "https://docs.voyageai.com/docs/embeddings",
        ),
        (
            "Voyage Reranker",
            "Voyage Reranker API",
            "https://docs.voyageai.com/docs/reranker",
        ),
    ],
    r"\bClaude( 3)?\b|\bAnthropic\b": (
        "Anthropic Claude",
        "Claude Documentation",
        "https://docs.anthropic.com/",
    ),
    r"\bGPT-4o?\b|\bOpenAI\b": (
        "OpenAI",
        "OpenAI API Documentation",
        "https://platform.openai.com/docs/",
    ),
    r"\bLlama( 2| 3)?\b": ("Llama", "Meta Llama Models", "https://llama.meta.com/"),
    r"\bDocker\b": ("Docker", "Docker Documentation", "https://docs.docker.com/"),
    r"\bKubernetes\b|\bK8s\b": (
        "Kubernetes",
        "Kubernetes Official Documentation",
        "https://kubernetes.io/docs/",
    ),
    r"\bZod\b": ("Zod", "TypeScript-first schema validation", "https://zod.dev/"),
    r"\bCobra\b": (
        "Cobra",
        "A Commander for modern Go CLI interactions",
        "https://cobra.dev/",
    ),
    r"\bFyne\b": (
        "Fyne",
        "Cross platform GUI in Go inspired by Material Design",
        "https://fyne.io/",
    ),
    r"\bGitHub Actions\b|\bCI/CD\b": (
        "GitHub Actions",
        "Automate your workflow from idea to production",
        "https://docs.github.com/en/actions",
    ),
    r"\bTrace\b|\bTracing\b": (
        "Trace",
        "Distributed Tracing Concepts (OpenTelemetry)",
        "https://opentelemetry.io/docs/concepts/signals/traces/",
    ),
    r"\bObservabilidade\b|\bObservability\b": (
        "Observability",
        "Control Theory and System Observability",
        "https://en.wikipedia.org/wiki/Observability",
    ),
    r"\bONNX Runtime Go\b": (
        "ONNX Runtime Go",
        "Official Go runtime for ONNX inference",
        "https://github.com/yalue/onnxruntime-go",
    ),
    r"\bStructured Decision Patterns\b": (
        "Structured Decision Patterns",
        "Decision engine patterns for distributed systems",
        "https://martinfowler.com/articles/decision-engine.html",
    ),
    r"\bFaithfulness Evaluation\b": (
        "Faithfulness Evaluation",
        "Metrics for evaluating context-faithful LLM responses",
        "https://arxiv.org/abs/2305.11747",
    ),
    # Vectora Stack Components
    r"\bFastAPI\b": (
        "FastAPI",
        "Modern Python web framework for building APIs",
        "https://fastapi.tiangolo.com/",
    ),
    r"\bLangChain\b": [
        (
            "LangChain Official",
            "LangChain Framework and Documentation",
            "https://www.langchain.com/",
        ),
        (
            "LangChain Docs",
            "LangChain Official Documentation",
            "https://docs.langchain.com/",
        ),
    ],
    r"\bLangGraph\b": [
        (
            "LangGraph",
            "Agent Orchestration Framework for Reliable AI Agents",
            "https://www.langchain.com/langgraph",
        ),
        (
            "LangGraph Docs",
            "LangGraph Official Documentation",
            "https://docs.langchain.com/oss/python/langgraph/",
        ),
    ],
    r"\bLangSmith\b": (
        "LangSmith",
        "AI Agent & LLM Observability Platform",
        "https://www.langchain.com/langsmith/observability",
    ),
    r"\bDeep Agents\b": [
        (
            "Deep Agents",
            "Deep Agents: Build Agents for Complex, Multi-Step Tasks",
            "https://www.langchain.com/deep-agents",
        ),
        (
            "Deep Agents Docs",
            "Deep Agents Overview Documentation",
            "https://docs.langchain.com/oss/python/deepagents/overview",
        ),
    ],
    r"\bPostgreSQL\b|\bPostgres\b": (
        "PostgreSQL",
        "PostgreSQL Official Documentation",
        "https://www.postgresql.org/docs/",
    ),
    r"\bpg8000\b": (
        "pg8000",
        "Pure-Python PostgreSQL Driver",
        "https://pybrary.net/pg8000/",
    ),
    r"\bRedis\b": [
        (
            "Redis Official",
            "Redis Official Documentation",
            "https://redis.io/docs/",
        ),
        (
            "redis-py",
            "Redis Python Client Documentation",
            "https://redis.io/docs/latest/develop/clients/redis-py/",
        ),
    ],
    r"\bLanceDB\b": [
        (
            "LanceDB Docs",
            "LanceDB Official Documentation",
            "https://docs.lancedb.com/",
        ),
        (
            "LanceDB GitHub",
            "LanceDB Open Source Repository",
            "https://github.com/lancedb/lancedb",
        ),
    ],
    r"\bVoyage Embeddings\b": (
        "Voyage Embeddings",
        "Text Embeddings API Reference",
        "https://docs.voyageai.com/reference/embeddings-api",
    ),
    r"\bVoyage Reranker\b": (
        "Voyage Reranker",
        "Reranker API Reference",
        "https://docs.voyageai.com/reference/reranker-api",
    ),
    r"\bJenkins\b": [
        (
            "Jenkins Official",
            "Jenkins Continuous Integration Server",
            "https://www.jenkins.io/",
        ),
        (
            "Jenkins Pipeline",
            "Jenkins Pipeline as Code",
            "https://www.jenkins.io/doc/book/pipeline/",
        ),
    ],
    r"\bGitHub Actions\b": (
        "GitHub Actions",
        "GitHub Actions Workflows Documentation",
        "https://docs.github.com/en/actions",
    ),
    r"\bDocker Compose\b": (
        "Docker Compose",
        "Docker Compose Documentation",
        "https://docs.docker.com/compose/",
    ),
    r"\bVCR\b|\bVectora Cognitive Runtime\b": (
        "VCR",
        "Vectora Cognitive Runtime (XLM-RoBERTa + LoRA)",
        "https://github.com/vectora/vectora/docs/vcr",
    ),
    r"\bXLM-RoBERTa\b": (
        "XLM-RoBERTa",
        "Facebook's XLM-RoBERTa Multilingual Model",
        "https://huggingface.co/FacebookAI/xlm-roberta-base",
    ),
    r"\bLoRA\b|\bLow-Rank Adaptation\b": (
        "LoRA",
        "LoRA: Low-Rank Adaptation of Large Language Models",
        "https://arxiv.org/abs/2106.09685",
    ),
    r"\bPaperclip\b": (
        "Paperclip",
        "Paperclip Agent Company Framework",
        "https://paperclip.ing/",
    ),
    r"\bACP\b|\bAgent Client Protocol\b": (
        "ACP",
        "Agent Client Protocol Specification",
        "https://agentclientprotocol.com/",
    ),
    r"\bJWT\b|\bJSON Web Token\b": (
        "JWT",
        "RFC 7519: JSON Web Token Standard",
        "https://datatracker.ietf.org/doc/html/rfc7519",
    ),
    r"\bRBAC\b|\bRole-Based Access Control\b": (
        "RBAC",
        "NIST Role-Based Access Control Standard",
        "https://csrc.nist.gov/projects/rbac",
    ),
    r"\bVectora Asset Library\b|\bVAL\b": (
        "VAL",
        "Vectora Asset Library - Registry de Datasets",
        "https://github.com/vectora/vectora-asset-library",
    ),
    r"\bVectora Integrations\b": (
        "Vectora Integrations",
        "@vectora-integrations TypeScript Monorepo",
        "https://github.com/vectora/vectora-integrations",
    ),
    r"\bClaude Code\b": (
        "Claude Code",
        "Claude Code IDE Integration",
        "https://claude.ai/code",
    ),
    r"\bCursor\b": (
        "Cursor",
        "The AI Code Editor",
        "https://www.cursor.com/",
    ),
    r"\bAnthropicAI\b|\bAnthropic\b": (
        "Anthropic",
        "Anthropic Official Website",
        "https://www.anthropic.com/",
    ),
    r"\bTurborepo\b": (
        "Turborepo",
        "Monorepo build system",
        "https://turbo.build/repo",
    ),
    r"\bpnpm\b": (
        "pnpm",
        "Fast, disk space efficient package manager",
        "https://pnpm.io/",
    ),
    r"\bnpm\b|\bNode Package Manager\b": (
        "npm",
        "Node Package Manager Official",
        "https://www.npmjs.com/",
    ),
    r"\bPyTest\b": (
        "Pytest",
        "The pytest Testing Framework",
        "https://docs.pytest.org/",
    ),
    r"\bOpenTelemetry\b": (
        "OpenTelemetry",
        "OpenTelemetry Observability Framework",
        "https://opentelemetry.io/",
    ),
    r"\bPrometheus\b": (
        "Prometheus",
        "Prometheus Monitoring System",
        "https://prometheus.io/docs/introduction/overview/",
    ),
}


def generate_linking_section(links):
    if not links:
        return ""

    # We limit to top 6 links to accommodate paired links
    selected_links = list(links)[:6]

    section = "## External Linking\n\n"
    section += "| Concept | Resource | Link |\n"
    section += "|---------|----------|------|\n"
    for concept, resource, link in selected_links:
        section += f"| **{concept}** | {resource} | [{link.replace('https://', '').replace('http://', '')}]({link}) |\n"

    return section


def normalize_text(text):
    # Remove all spaces, newlines, pipes, and hyphens to safely compare table content
    # This prevents Prettier's table padding and separator widths from causing infinite loops
    return re.sub(r"[\s\|\-]+", "", text).lower()


def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "<!-- External Linking omitido: conteúdo temporal -->" in content:
        return False

    # Count occurrences of each pattern to prioritize the most relevant links!
    concept_counts = {}
    for pattern, links in LINK_KNOWLEDGE_BASE.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            if isinstance(links, tuple):
                links = [links]
            for link_data in links:
                concept_counts[link_data] = concept_counts.get(link_data, 0) + len(
                    matches
                )

    if not concept_counts:
        return False

    # Remove old equivalent sections (Full Specification / Especificação Completa)
    content = re.sub(
        r"\n+## Full Specification\n.*?(?=\n\n## |\n\n---|\n\n> |\Z)",
        "",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"\n+## Especificação Completa\n.*?(?=\n\n## |\n\n---|\n\n> |\Z)",
        "",
        content,
        flags=re.DOTALL,
    )

    # Sort links by frequency of appearance in the document
    sorted_links = sorted(
        concept_counts.keys(), key=lambda k: concept_counts[k], reverse=True
    )
    new_section = generate_linking_section(sorted_links)

    existing_section_match = re.search(
        r"## External Linking\n.*?(?=\n\n## |\n\n---|\n\n> \*\*Frase|\Z)",
        content,
        re.DOTALL,
    )

    if existing_section_match:
        existing_content = existing_section_match.group(0)
        if normalize_text(new_section) == normalize_text(existing_content):
            pass
        else:
            content = content.replace(existing_content, new_section.strip())
    else:
        footer_patterns = [
            r"\n---\n+> \*\*Frase",
            r"\n---\n+> \*\*Phrase",
            r"\n> \*\*Frase",
            r"\n> \*\*Phrase",
            r"\n---\n+Parte do ecossistema",
            r"\n---\n+Part of Vectora",
            r"\n_Part of Vectora",
            r"\n_Parte do ecossistema",
        ]

        insertion_point = len(content)
        for pattern in footer_patterns:
            match = re.search(pattern, content)
            if match:
                insertion_point = match.start()
                break

        content = (
            content[:insertion_point].rstrip()
            + "\n\n"
            + new_section.strip()
            + "\n\n"
            + content[insertion_point:].lstrip()
        )

    # Final check if anything actually changed
    with open(filepath, "r", encoding="utf-8") as f:
        original_content = f.read()

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def main():
    modified_any = False
    files_to_check = sys.argv[1:]

    if not files_to_check:
        for root, dirs, files in os.walk("docs"):
            for file in files:
                if file.endswith(".md"):
                    files_to_check.append(os.path.join(root, file))

    for filepath in files_to_check:
        if filepath.endswith(".md"):
            if process_file(filepath):
                print(f"Updated External Links in: {filepath}")
                modified_any = True

    if modified_any:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
