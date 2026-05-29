# GraphRAG for Constitutional Intelligence

A hybrid GraphRAG system built on the Constituent Assembly Debates, historical constitutions, and constitutional books.

The system combines:

* BM25 keyword retrieval
* Dense vector retrieval using ChromaDB
* Reciprocal Rank Fusion (RRF)
* Cross-Encoder reranking
* Local LLM generation (Ollama)
* Neo4j knowledge graph retrieval

to answer constitutional and legal questions with grounded evidence.

---

# Features

### Hybrid Retrieval

Combines:

* BM25 lexical search
* Semantic vector search

using Reciprocal Rank Fusion (RRF).

### Cross Encoder Re-ranking

Improves retrieval quality by reranking retrieved chunks according to query relevance.

### Local LLM Inference

Runs completely offline using:

* Ollama
* Qwen2.5-Coder 7B

No external API dependency.

### GraphRAG

Uses Neo4j to build a context graph consisting of:

* People
* Articles
* Concepts
* Organizations
* Events

and their relationships.

### Multi-source Corpus

Supports:

* Constituent Assembly Debates
* Historical Constitutions
* Constitutional Books

---

# Architecture

```text
                    USER QUERY
                         │
                         ▼
               Hybrid Retrieval Layer
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
      BM25                         Chroma Vector DB
 (Keyword Search)              (Semantic Retrieval)
        │                                 │
        └────────────┬────────────────────┘
                     ▼
                  RRF Fusion
                     ▼
         Cross Encoder Re-ranking
                     ▼
             Top Relevant Chunks
                     ▼
                 Graph Expansion
                     ▼
                  Neo4j Graph
                     ▼
                Context Fusion
                     ▼
                 Ollama LLM
                     ▼
                  Response
```

---

# Project Structure

```text
graphRAG/

├── data/
│   ├── debates/
│   ├── constitutions/
│   └── books/
│
├── processed/
│   ├── debates/
│   ├── constitutions/
│   └── books/
│
├── pipelines/
│   ├── debates_pipeline.py
│   ├── constitutions_pipeline.py
│   └── books_pipeline.py
│
├── retrieval/
│   ├── bm25_index.pkl
│   ├── build_bm25.py
│   ├── hybrid_search.py
│   └── reranker.py
│
├── vector_db/
│   ├── chroma_store/
│   └── load_chroma.py
│
├── graph_db/
│   ├── extract_entities.py
│   ├── load_neo4j.py
│   ├── graph_retriever.py
│   └── extracted_entities/
│
├── generation/
│   └── generator.py
│
├── utils/
│
├── .env
├── requirements.txt
└── README.md
```

---

# Retrieval Pipeline

## BM25

Keyword based retrieval using:

```python
rank_bm25
```

Useful for:

* Article references
* Exact names
* Legal terminology

---

## Vector Search

Embedding model:

```text
BAAI/bge-base-en-v1.5
```

Storage:

```text
ChromaDB
```

Retrieval method:

```text
HNSW Approximate Nearest Neighbour Search
```

---

## Reciprocal Rank Fusion

Combines BM25 and vector rankings:

```text
RRF Score = Σ 1 / (k + rank)
```

This improves retrieval robustness.

---

## Cross Encoder

Model:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

Used to rerank retrieved chunks before generation.

---

# GraphRAG Pipeline

## Entity Extraction

Each chunk is processed by an LLM.

Extracted:

* Entities
* Concepts
* Relationships

Example:

```json
{
  "entities": [
    {
      "name": "B. R. Ambedkar",
      "type": "PERSON"
    }
  ],
  "relationships": [
    {
      "source": "B. R. Ambedkar",
      "target": "Untouchability",
      "relation": "DISCUSSED"
    }
  ]
}
```

---

## Neo4j Graph

Nodes:

* Entity
* Chunk

Relationships:

* MENTIONED_IN
* DISCUSSED
* DRAFTED
* OPPOSED
* SUPPORTED

etc.

---

# Local LLM

Using Ollama.

Example model:

```bash
ollama pull qwen2.5-coder:7b
```

Configured through:

```python
ChatOllama(
    model="qwen2.5-coder:7b"
)
```

---

# Installation

Clone repository:

```bash
git clone https://github.com/shloksharma273/graphRAG.git

cd graphRAG
```

Create environment:

```bash
python -m venv .venv

source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create:

```bash
.env
```

Example:

```env
NEO4J_URI=bolt://localhost:7687

NEO4J_USERNAME=neo4j

NEO4J_PASSWORD=password
```

---

# Running the Pipeline

## Step 1

Process Debates

```bash
python pipelines/debates_pipeline.py
```

---

## Step 2

Process Constitutions

```bash
python pipelines/constitutions_pipeline.py
```

---

## Step 3

Process Books

```bash
python pipelines/books_pipeline.py
```

---

## Step 4

Load ChromaDB

```bash
python vector_db/load_chroma.py
```

---

## Step 5

Build BM25 Index

```bash
python retrieval/build_bm25.py
```

---

## Step 6

Extract Entities

```bash
python graph_db/extract_entities.py
```

---

## Step 7

Load Neo4j Graph

```bash
python graph_db/load_neo4j.py
```

---

## Step 8

Run Hybrid Retrieval

```bash
python retrieval/hybrid_search.py
```

---

# Example Queries

```text
What did Ambedkar say about untouchability?

Who supported reservations for Scheduled Castes?

How was Article 17 debated?

What were the arguments against separate electorates?

Which members discussed social equality?
```

---

# Future Improvements

* Community detection on graph
* Graph embeddings
* Query decomposition
* Agentic retrieval
* Citation generation
* Constitutional timeline visualization
* Multi-hop reasoning over Neo4j

---

# Tech Stack

* Python
* ChromaDB
* Neo4j
* Ollama
* Qwen2.5
* Sentence Transformers
* BM25
* Cross Encoders
* LangChain
* tqdm

---

# License

MIT License
