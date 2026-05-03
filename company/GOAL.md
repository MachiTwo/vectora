# Vectora: Hub de Conhecimento Local-First para Ecossistemas de Agentes

## O que é o Vectora

Vectora é um **Hub de Conhecimento e Agente Especialista** local-first, projetado para servir como a camada de inteligência e memória para desenvolvedores e outros agentes de IA. Ele opera como um aplicativo de binário único (Go) que combina busca vetorial de alta performance, gerenciamento de dados estruturados e uma camada de pré-processamento cognitivo (VCR).

O Vectora é o "cérebro local" que permite que ferramentas como Claude Code, Cursor, Gemini e sistemas multi-agentes baseados em Paperclip operem com contexto profundo, sem alucinações e com total privacidade de dados.

Vectora combina três pilares fundamentais:

1. **Contexto Governado** - Recuperação semântica ultraveloz via LanceDB + Voyage AI, com reranking local.
2. **Pré-Pensamento (VCR)** - Camada cognitiva especializada (XLM-RoBERTa + LoRA) que analisa a intenção e enriquece o contexto antes da execução.
3. **Memória Persistente** - Sistema de armazenamento multi-camada (PostgreSQL + Redis) para histórico de sessões, aprendizado contínuo e isolamento por agente.

## Objetivo

O objetivo do Vectora é descentralizar a inteligência artificial, fornecendo uma infraestrutura de decisão fundamentada em contexto real e governada por políticas locais. Queremos eliminar a dependência de RAGs genéricos na nuvem e o risco de vazamento de segredos comerciais, transformando LLMs em agentes especialistas capazes de operar em repositórios complexos com precisão cirúrgica e segurança absoluta.

---

## O Ecossistema Vectora

### Backend (Go)

O núcleo do sistema, construído em Go para máxima performance e baixa latência. Responsável por:
- Daemon de alta concorrência e binário único.
- Servidor MCP (Model Context Protocol) nativo para integração com agentes.
- Orquestração de pipelines RAG e integração com LLMs (Claude, OpenAI, Gemini).
- Gerenciamento de bancos de dados embedded e roteamento de APIs.

### Vectora Cognitive Runtime (VCR)

O motor de decisão tática, operando em Python para aproveitar bibliotecas de ML de última geração:
- Execução de modelos XLM-RoBERTa-small fine-tuned para análise de contexto.
- Pre-thinking layer que otimiza queries e seleciona ferramentas antes do agente principal agir.
- Interface via JSON-RPC/Subprocess para latência mínima de inferência (4-8ms).

### Storage & Memory Layer

Persistência local-first em três dimensões:
- **LanceDB**: Armazenamento vetorial nativo em formato .lance para busca semântica.
- **PostgreSQL (Embedded)**: Gerenciamento de metadados, usuários, permissões (RBAC) e histórico.
- **Redis (Embedded)**: Cache de alta velocidade, gerenciamento de sessões e filas de background jobs.

### Integrations (@vectora-integrations)

Uma suíte de SDKs e adaptadores que tornam o Vectora universal:
- **MCP Bridge**: Conecta o Vectora ao Claude Code e outros clientes MCP.
- **Paperclip Plugin**: Integração nativa para orquestração em empresas de agentes.
- **Shared SDK**: Tipagem e clientes HTTP/RPC compartilhados para desenvolvimento de novos adaptadores.

### VAL (Vectora Asset Library)

O registry comunitário e governado de conhecimento:
- Distribuição de datasets vetorizados e prontos para uso (documentação, padrões de código).
- CLI commands para download e sincronização instantânea de conhecimento especializado.

### Multi-Agent Orchestration

Suporte nativo para hierarquias de agentes:
- Isolamento de dados por bucket privado para cada agente (CEO, CTO, Backend, etc).
- Buckets públicos e organizacionais para compartilhamento controlado de conhecimento.
- Autenticação robusta baseada em chaves de API derivadas para automação segura.

## Estratégia de Documentação

O Vectora mantém uma base de conhecimento rigorosa e multi-idioma (PT-BR canônico) em `vectora-website/`, utilizando Hugo e Hextra para fornecer guias técnicos, padrões de arquitetura e documentação de API para a comunidade global.
