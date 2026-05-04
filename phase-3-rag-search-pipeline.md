# Phase 3: RAG & Search Pipeline

**Objetivo**: Implementar pipelines de Retrieval-Augmented Generation com LanceDB, VoyageAI embeddings e reranking local.

**Status**: Análise inicial
**Duração estimada**: 3-4 semanas

## Objectives

1. Integrar LanceDB para vector storage
2. Embeddings via VoyageAI API
3. Semantic search com relevância alta
4. Local reranking (sem chamadas externas)
5. Otimizar para conversas longas (memory strategies)

## Key Tasks

### 3.1 LanceDB Integration

- [ ] Setup LanceDB storage em internal/storage/vectordb
- [ ] Schema para documents (chunk, embedding, metadata)
- [ ] Index creation e optimization
- [ ] Connection pooling e health checks
- [ ] Migration system para schema updates

### 3.2 VoyageAI Embeddings

- [ ] Configurar cliente VoyageAI API
- [ ] Implementar batch embedding (eficiência)
- [ ] Caching de embeddings em Redis
- [ ] Fallback para embeddings locais (se necessário)
- [ ] Validar dimensionalidade e normalization

### 3.3 Semantic Search Engine

- [ ] Query expansion (gerar variações de query)
- [ ] Vector similarity search (cosine, L2)
- [ ] Hybrid search (keyword + vector)
- [ ] Filtering por metadados (filetype, date, owner)
- [ ] Pagination e result ranking

### 3.4 Local Reranking

- [ ] Implementar cross-encoder local (XLM-RoBERTa via VCR)
- [ ] Score relevância em relação à query
- [ ] Diversidade de results (evitar duplicatas semânticas)
- [ ] Top-K selection e threshold filtering

### 3.5 Memory Strategies for Long Conversations

- [ ] Truncate: manter últimas N mensagens
- [ ] Delete: remover mensagens triviais
- [ ] Summarize: compactar com resumo inteligente
- [ ] Hybrid strategy (combinar as 3)
- [ ] Integração com LangGraph state management

### 3.6 Document Ingestion Pipeline

- [ ] Parser para múltiplos formatos (markdown, code, PDFs)
- [ ] Chunking strategy (semantic, sliding window)
- [ ] Metadata extraction (title, date, author)
- [ ] Deduplication (hashes)
- [ ] Batch processing com worker pools

### 3.7 Testing & Benchmarks

- [ ] Unit tests para search accuracy
- [ ] Benchmark query latency (target: <200ms)
- [ ] Evaluate reranker precision
- [ ] Integration tests com RAG pipeline completa

## Dependencies

- LanceDB
- VoyageAI SDK
- numpy (vector math)
- pandas (data handling)
- langchain (RAG utilities)

## Acceptance Criteria

- ✅ LanceDB setup e funcional
- ✅ VoyageAI embeddings integrados
- ✅ Search latency <200ms (p99)
- ✅ Reranking local sem chamadas externas
- ✅ Memory strategies testadas (truncate, delete, summarize)
- ✅ Document ingestion pipeline funcional
- ✅ Testes passam com >80% coverage

## Notes

- RAG é core do Vectora (contexto governado)
- Reranking local é crítico para privacidade (sem data leakage)
- Estratégias de memória previnem context explosion
- Benchmark query latency regularmente (não regressionar)
