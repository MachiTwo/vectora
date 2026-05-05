---
title: Go SDK
slug: go-sdk
date: "2026-05-04T12:00:00-03:00"
type: docs
sidebar:
  open: true
tags:
  - sdk
  - go
  - client
  - microservices
  - vectora
---

{{< lang-toggle >}}

O **Vectora Go SDK** (`vectora-go`) fornece um cliente de baixa latência, type-safe e otimizado para microserviços e aplicações high-performance.

## Instalação

```bash
# Via go get
go get github.com/vectora-io/vectora-go

# Em go.mod
go get github.com/vectora-io/vectora-go@latest
```

## Setup Básico

```go
package main

import (
 "github.com/vectora-io/vectora-go"
)

func main() {
 client, err := vectora.NewClient(&vectora.Config{
  APIKey:  "vec_your_api_key_here",
  BaseURL: "https://api.vectora.dev",
  Timeout: 30 * time.Second,
 })
 if err != nil {
  panic(err)
 }
 defer client.Close()
}
```

## Buscas Simples

```go
package main

import (
 "context"
 "fmt"
 "github.com/vectora-io/vectora-go"
)

func main() {
 client, _ := vectora.NewClient(&vectora.Config{
  APIKey: "vec_...",
 })
 defer client.Close()

 ctx := context.Background()
 results, err := client.Search(ctx, &vectora.SearchRequest{
  Query:    "como autenticar com JWT?",
  BucketID: "docs",
  TopK:     5,
 })
 if err != nil {
  panic(err)
 }

 for i, result := range results {
  fmt.Printf("%d. Score: %.2f%%\n", i+1, result.Score*100)
  fmt.Printf("   Content: %s...\n", result.Content[:100])
  fmt.Printf("   File: %s\n\n", result.Metadata["file"])
 }
}
```

## Buscas Avançadas com Filtros

```go
results, err := client.Search(ctx, &vectora.SearchRequest{
 Query:    "token validation",
 BucketID: "docs",
 TopK:     10,
 Filters: map[string]interface{}{
  "fileType": "go",
  "language": "en",
 },
 MinScore: 0.7,
})
```

## Gerenciamento de Buckets

```go
// Criar bucket
bucket, err := client.Buckets.Create(ctx, &vectora.CreateBucketRequest{
 Name:        "my-docs",
 IsPublic:    false,
 Description: "Documentação interna",
})

// Listar buckets
buckets, err := client.Buckets.List(ctx)
for _, bucket := range buckets {
 fmt.Printf("ID: %s, Name: %s\n", bucket.ID, bucket.Name)
}

// Obter bucket específico
bucket, err := client.Buckets.Get(ctx, "docs")

// Deletar bucket
err := client.Buckets.Delete(ctx, "docs")
```

## Indexação de Documentos

```go
documents := []vectora.Document{
 {
  ID:      "doc-1",
  Content: "func verifyToken(token string) (bool, error) { ... }",
  Metadata: map[string]string{
   "file": "auth.go",
   "line": "10",
  },
 },
 {
  ID:      "doc-2",
  Content: "func refreshToken(oldToken string) (string, error) { ... }",
  Metadata: map[string]string{
   "file": "auth.go",
   "line": "25",
  },
 },
}

err := client.Documents.Index(ctx, &vectora.IndexRequest{
 BucketID:  "docs",
 Documents: documents,
})

// Deletar documento
err := client.Documents.Delete(ctx, "docs", "doc-1")

// Atualizar documento
err := client.Documents.Update(ctx, &vectora.UpdateDocumentRequest{
 BucketID:  "docs",
 DocumentID: "doc-2",
 Content:   "novo conteúdo",
})
```

## Streaming de Respostas

```go
stream, err := client.SearchStream(ctx, &vectora.SearchRequest{
 Query:    "autenticação",
 BucketID: "docs",
})
if err != nil {
 panic(err)
}

for result := range stream {
 if result.Error != nil {
  fmt.Printf("Erro: %v\n", result.Error)
  continue
 }
 fmt.Printf("Score: %.2f, Content: %s\n", result.Score, result.Content[:50])
}
```

## Retry Logic com Backoff

```go
client, _ := vectora.NewClient(&vectora.Config{
 APIKey: "...",
 RetryConfig: &vectora.RetryConfig{
  MaxRetries:      3,
  InitialDelayMs:  1000,
  BackoffFactor:   2.0,
  MaxDelayMs:      60000,
 },
})
```

## Error Handling

```go
import "github.com/vectora-io/vectora-go/errors"

results, err := client.Search(ctx, request)
if err != nil {
 switch err {
 case errors.ErrNotFound:
  fmt.Println("Bucket não encontrado")
 case errors.ErrUnauthorized:
  fmt.Println("API key inválida")
 default:
  fmt.Printf("Erro na API: %v\n", err)
 }
}
```

## Context e Timeouts

```go
// Timeout para requisição específica
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

results, err := client.Search(ctx, request)

// Cancelamento
ctx, cancel := context.WithCancel(context.Background())
// ... fazer operações
cancel() // Cancelar operação
```

## Batch Operations

```go
// Buscar múltiplas queries
queries := []string{
 "JWT validation",
 "password hashing",
 "token refresh",
}

results := make([][]vectora.Result, len(queries))
for i, query := range queries {
 res, err := client.Search(ctx, &vectora.SearchRequest{
  Query:    query,
  BucketID: "docs",
  TopK:     5,
 })
 if err != nil {
  panic(err)
 }
 results[i] = res
}
```

## Exemplos Completos

### Indexação de Repositório

```go
package main

import (
 "context"
 "fmt"
 "io/ioutil"
 "os"
 "path/filepath"
 "github.com/vectora-io/vectora-go"
)

func indexRepository(rootDir, bucketID string, client *vectora.Client) error {
 ctx := context.Background()
 var documents []vectora.Document

 err := filepath.Walk(rootDir, func(path string, info os.FileInfo, err error) error {
  if err != nil {
   return err
  }

  if info.IsDir() || !isSupportedFile(path) {
   return nil
  }

  content, err := ioutil.ReadFile(path)
  if err != nil {
   return err
  }

  documents = append(documents, vectora.Document{
   ID:      path,
   Content: string(content),
   Metadata: map[string]string{
    "file": path,
    "size": fmt.Sprintf("%d", len(content)),
   },
  })

  return nil
 })

 if err != nil {
  return err
 }

 return client.Documents.Index(ctx, &vectora.IndexRequest{
  BucketID:  bucketID,
  Documents: documents,
 })
}

func isSupportedFile(path string) bool {
 ext := filepath.Ext(path)
 return ext == ".go" || ext == ".py" || ext == ".js"
}
```

### HTTP Server com Middleware

```go
package main

import (
 "context"
 "net/http"
 "github.com/vectora-io/vectora-go"
)

func main() {
 client, _ := vectora.NewClient(&vectora.Config{
  APIKey: "vec_...",
 })
 defer client.Close()

 http.HandleFunc("/search", func(w http.ResponseWriter, r *http.Request) {
  ctx := context.Background()
  query := r.URL.Query().Get("q")

  results, err := client.Search(ctx, &vectora.SearchRequest{
   Query:    query,
   BucketID: "docs",
   TopK:     5,
  })
  if err != nil {
   http.Error(w, err.Error(), http.StatusInternalServerError)
   return
  }

  // Marshal to JSON
  w.Header().Set("Content-Type", "application/json")
  // jsonify results...
 })

 http.ListenAndServe(":8080", nil)
}
```

### CLI para Busca

```go
package main

import (
 "bufio"
 "context"
 "fmt"
 "os"
 "github.com/vectora-io/vectora-go"
)

func main() {
 client, _ := vectora.NewClient(&vectora.Config{
  APIKey: "vec_...",
 })
 defer client.Close()

 scanner := bufio.NewScanner(os.Stdin)
 fmt.Print("Buscar: ")

 for scanner.Scan() {
  query := scanner.Text()
  if query == "exit" {
   break
  }

  ctx := context.Background()
  results, err := client.Search(ctx, &vectora.SearchRequest{
   Query:    query,
   BucketID: "docs",
   TopK:     3,
  })

  if err != nil {
   fmt.Printf("Erro: %v\n", err)
   continue
  }

  for i, result := range results {
   fmt.Printf("%d. (%.1f%%) %s\n", i+1, result.Score*100, result.Content[:80])
  }

  fmt.Print("\nBuscar: ")
 }
}
```

## Benchmarking

```go
package main

import (
 "context"
 "testing"
 "github.com/vectora-io/vectora-go"
)

func BenchmarkSearch(b *testing.B) {
 client, _ := vectora.NewClient(&vectora.Config{
  APIKey: "vec_...",
 })
 defer client.Close()

 ctx := context.Background()
 request := &vectora.SearchRequest{
  Query:    "autenticação",
  BucketID: "docs",
  TopK:     5,
 }

 b.ResetTimer()
 for i := 0; i < b.N; i++ {
  client.Search(ctx, request)
 }
}
```

## External Linking

| Conceito            | Recurso             | Link                                                                         |
| ------------------- | ------------------- | ---------------------------------------------------------------------------- |
| **Vectora Go SDK**  | GitHub Repository   | [github.com/vectora-io/vectora-go](https://github.com/vectora-io/vectora-go) |
| **Go Modules**      | Official docs       | [golang.org/ref/mod](https://golang.org/ref/mod)                             |
| **Context Package** | Standard library    | [pkg.go.dev/context](https://pkg.go.dev/context)                             |
| **HTTP Client**     | Go documentation    | [pkg.go.dev/net/http](https://pkg.go.dev/net/http)                           |
| **JSON Encoding**   | Go standard library | [pkg.go.dev/encoding/json](https://pkg.go.dev/encoding/json)                 |
