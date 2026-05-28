from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank
from generation.answer_generator import generate_answer


query = input("Ask question: ")


# -------------------------
# RETRIEVAL
# -------------------------

results = hybrid_search(query)

print(f"Retrieved {len(results)} documents")
# -------------------------
# RERANKING
# -------------------------

documents = [
    r["text"]
    for r in results
]

print(documents)
reranked_docs = rerank(
    query,
    documents,
    top_k=8
)


print(reranked_docs)
# -------------------------
# MAP BACK TO CHUNKS
# -------------------------

final_chunks = []

for doc_text, rerank_score in reranked_docs:

    for r in results:

        if r["text"] == doc_text:

            r["rerank_score"] = float(rerank_score)

            final_chunks.append(r)

            break

print(final_chunks)
# -------------------------
# ANSWER GENERATION
# -------------------------

answer = generate_answer(
    query,
    final_chunks
)


print("\n===== ANSWER =====\n")

print(answer)