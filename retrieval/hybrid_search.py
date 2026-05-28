import pickle
import chromadb
import numpy as np

from sentence_transformers import SentenceTransformer

from retrieval.reranker import rerank


TOP_K = 25

EMBED_MODEL = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)


# -------------------------
# LOAD BM25
# -------------------------

with open("retrieval/bm25_index.pkl", "rb") as f:

    data = pickle.load(f)

bm25 = data["bm25"]

bm25_chunks = data["chunks"]


# -------------------------
# LOAD CHROMA
# -------------------------

client = chromadb.PersistentClient(
    path="vector_db/chroma_store"
)

collection = client.get_collection(
    name="constitution_rag"
)


# -------------------------
# BM25 SEARCH
# -------------------------

def bm25_search(query, top_k=TOP_K):

    tokens = query.lower().split()

    scores = bm25.get_scores(tokens)

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for rank, idx in enumerate(top_indices):

        chunk = bm25_chunks[idx]

        results.append({
            "chunk": chunk,
            "score": scores[idx],
            "rank": rank + 1
        })

    return results


# -------------------------
# VECTOR SEARCH
# -------------------------

def vector_search(query, top_k=TOP_K):

    embedding = EMBED_MODEL.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    output = []

    for i in range(len(results["ids"][0])):

        output.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
            "rank": i + 1
        })

    return output


# -------------------------
# RRF FUSION
# -------------------------

def reciprocal_rank_fusion(bm25_results, vector_results, k=60):

    fused_scores = {}


    # BM25

    for item in bm25_results:

        chunk_id = item["chunk"]["chunk_id"]

        rank = item["rank"]

        fused_scores.setdefault(chunk_id, 0)

        fused_scores[chunk_id] += 1 / (k + rank)


    # VECTOR

    for item in vector_results:

        chunk_id = item["chunk_id"]

        rank = item["rank"]

        fused_scores.setdefault(chunk_id, 0)

        fused_scores[chunk_id] += 1 / (k + rank)


    ranked = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked


# -------------------------
# MAIN SEARCH
# -------------------------

def hybrid_search(query):

    bm25_results = bm25_search(query)

    vector_results = vector_search(query)

    fused = reciprocal_rank_fusion(
        bm25_results,
        vector_results
    )

    final_results = []

    for chunk_id, score in fused[:10]:

        found = None

        # search BM25 results
        for item in bm25_results:

            if item["chunk"]["chunk_id"] == chunk_id:

                found = {
                    "chunk_id": chunk_id,
                    "text": item["chunk"]["text"],
                    "score": score,
                    "source": "bm25"
                }

                break

        # search vector results
        if not found:

            for item in vector_results:

                if item["chunk_id"] == chunk_id:

                    found = {
                        "chunk_id": chunk_id,
                        "text": item["text"],
                        "score": score,
                        "source": "vector"
                    }

                    break

        if found:
            final_results.append(found)

    return final_results    



if __name__ == "__main__":

    query = "what did ambedkar say about untouchability"

    results = hybrid_search(query)

    documents = [
    r["text"]
    for r in results
    ]

    reranked = rerank(
        query,
        documents,
        top_k=5
    )

    print(reranked)