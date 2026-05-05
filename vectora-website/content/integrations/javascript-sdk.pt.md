---
title: JavaScript SDK
slug: javascript-sdk
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - sdk
  - javascript
  - client
  - node
  - vectora
---

{{< lang-toggle >}}

O **Vectora JavaScript SDK** (`vectora-js`) fornece suporte completo para Node.js e browsers, com async/await nativo, TypeScript types e streaming integrado.

## Instalação

```bash
# Via npm
npm install vectora

# Via yarn
yarn add vectora

# Via pnpm
pnpm add vectora
```

## Setup Básico

```javascript
import { VectoraClient } from "vectora";

const client = new VectoraClient({
  apiKey: "vec_your_api_key_here",
  baseUrl: "https://api.vectora.dev",
  timeout: 30000, // ms
});
```

## Buscas Simples

```javascript
// Busca simples
const results = await client.search({
  query: "como autenticar com JWT?",
  bucketId: "docs",
  topK: 5,
});

results.forEach((result) => {
  console.log(`Score: ${result.score}`);
  console.log(`Content: ${result.content.substring(0, 200)}...`);
  console.log(`File: ${result.metadata.file}`);
});
```

## Buscas Avançadas

```javascript
// Busca com filtros
const results = await client.search({
  query: "token validation",
  bucketId: "docs",
  topK: 10,
  filters: {
    fileType: "javascript",
    language: "en",
  },
  minScore: 0.7,
});
```

## Gerenciamento de Buckets

```javascript
// Criar bucket
const bucket = await client.buckets.create({
  name: "my-docs",
  isPublic: false,
  description: "Documentação interna",
});

// Listar buckets
const buckets = await client.buckets.list();
buckets.forEach((bucket) => {
  console.log(`ID: ${bucket.id}, Name: ${bucket.name}`);
});

// Obter bucket específico
const bucket = await client.buckets.get("docs");

// Deletar bucket
await client.buckets.delete("docs");
```

## Indexação de Documentos

```javascript
// Indexar documentos
const documents = [
  {
    id: "doc-1",
    content: "function verifyToken(token) { ... }",
    metadata: { file: "auth.js", line: 10 },
  },
  {
    id: "doc-2",
    content: "function refreshToken(oldToken) { ... }",
    metadata: { file: "auth.js", line: 25 },
  },
];

await client.documents.index({
  bucketId: "docs",
  documents,
});

// Deletar documento
await client.documents.delete({
  bucketId: "docs",
  documentId: "doc-1",
});

// Atualizar documento
await client.documents.update({
  bucketId: "docs",
  documentId: "doc-2",
  content: "novo conteúdo",
});
```

## Streaming de Respostas

```javascript
// Streaming para buscas
const stream = await client.searchStream({
  query: "autenticação",
  bucketId: "docs",
});

for await (const chunk of stream) {
  console.log(`Score: ${chunk.score}`);
  console.log(`Content: ${chunk.content}`);
}
```

## Retry Logic

```javascript
const client = new VectoraClient({
  apiKey: "...",
  retryConfig: {
    maxRetries: 3,
    initialDelayMs: 1000,
    backoffFactor: 2.0,
    maxDelayMs: 60000,
  },
});
```

## Error Handling

```javascript
import { VectoraError, NotFoundError, UnauthorizedError } from "vectora";

try {
  const results = await client.search({
    query: "test",
    bucketId: "nonexistent",
  });
} catch (error) {
  if (error instanceof NotFoundError) {
    console.log("Bucket não encontrado");
  } else if (error instanceof UnauthorizedError) {
    console.log("API key inválida");
  } else if (error instanceof VectoraError) {
    console.log(`Erro na API: ${error.message}`);
  }
}
```

## TypeScript Support

```typescript
import { VectoraClient, SearchResult, Bucket } from "vectora";

const client = new VectoraClient({ apiKey: "..." });

const results: SearchResult[] = await client.search({
  query: "autenticação",
  bucketId: "docs",
  topK: 5,
});

const buckets: Bucket[] = await client.buckets.list();
```

## Batch Operations

```javascript
// Buscar múltiplas queries
const queries = ["JWT validation", "password hashing", "token refresh"];

const results = await client.searchBatch({
  queries,
  bucketId: "docs",
  topK: 5,
});

// results[i] contém resultados para queries[i]
```

## Rate Limiting

```javascript
const client = new VectoraClient({
  apiKey: "...",
  rateLimiter: {
    requestsPerSecond: 10,
  },
});
```

## Exemplos Completos

### Busca Interativa

```javascript
import { VectoraClient } from "vectora";
import readline from "readline";

const client = new VectoraClient({ apiKey: "vec_..." });

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

async function searchInteractive() {
  rl.question("Buscar: ", async (query) => {
    const results = await client.search({
      query,
      bucketId: "docs",
      topK: 3,
    });

    console.log("\nResultados:");
    results.forEach((result, i) => {
      console.log(`${i + 1}. Score: ${(result.score * 100).toFixed(1)}%`);
      console.log(`   ${result.content.substring(0, 100)}...`);
    });

    rl.close();
  });
}

searchInteractive();
```

### Indexação de Código

```javascript
import { VectoraClient } from "vectora";
import fs from "fs/promises";
import path from "path";

async function indexCodeRepository(dirPath, bucketId) {
  const client = new VectoraClient({ apiKey: "vec_..." });
  const documents = [];

  async function walkDir(dir) {
    const entries = await fs.readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        await walkDir(fullPath);
      } else if (entry.name.endsWith(".js") || entry.name.endsWith(".ts")) {
        const content = await fs.readFile(fullPath, "utf-8");
        documents.push({
          id: fullPath,
          content,
          metadata: { file: fullPath, size: content.length },
        });
      }
    }
  }

  await walkDir(dirPath);

  await client.documents.index({
    bucketId,
    documents,
  });

  console.log(`Indexados ${documents.length} arquivos`);
}

indexCodeRepository("./src", "my-codebase");
```

### API REST com Express

```javascript
import { VectoraClient } from "vectora";
import express from "express";

const app = express();
const client = new VectoraClient({ apiKey: "vec_..." });

// Endpoint de busca
app.post("/api/search", async (req, res) => {
  try {
    const { query, bucketId, topK = 5 } = req.body;

    const results = await client.search({
      query,
      bucketId,
      topK,
    });

    res.json({ results });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log("Servidor rodando na porta 3000");
});
```

## Browser Support

```html
<!-- Via CDN -->
<script src="https://cdn.vectora.io/vectora.min.js"></script>
<script>
  const client = new Vectora.VectoraClient({ apiKey: "..." });

  document.getElementById("search-btn").addEventListener("click", async () => {
    const query = document.getElementById("query").value;
    const results = await client.search({
      query,
      bucketId: "docs",
      topK: 5,
    });

    console.log(results);
  });
</script>
```

## External Linking

| Conceito             | Recurso                | Link                                                                                                                                     |
| -------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Vectora JS SDK**   | GitHub Repository      | [github.com/vectora-io/vectora-js](https://github.com/vectora-io/vectora-js)                                                             |
| **npm Package**      | Package Registry       | [npmjs.com/package/vectora](https://npmjs.com/package/vectora)                                                                           |
| **TypeScript Guide** | Official documentation | [typescriptlang.org/docs](https://www.typescriptlang.org/docs/)                                                                          |
| **Async/Await**      | MDN Web Docs           | [developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous) |
| **Node.js Streams**  | Node.js documentation  | [nodejs.org/api/stream.html](https://nodejs.org/api/stream.html)                                                                         |
