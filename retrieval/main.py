from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank


query = "What did Ambedkar say about untouchability?"


# Step 1 — Hybrid Retrieval
results = hybrid_search(query)
# print(results)


# Step 2 — Extract documents
documents = [
    r["text"]
    for r in results
]


# Step 3 — Rerank
reranked = rerank(
    query,
    documents,
    top_k=5
)


# Step 4 — Print final results
for idx, (doc, score) in enumerate(reranked):

    print("\n")
    print("=" * 80)

    print(f"RANK: {idx + 1}")
    print(f"SCORE: {score}")

    print(doc[:1500])