import pickle
import numpy as np


INDEX_PATH = "retrieval/bm25_index.pkl"


with open(INDEX_PATH, "rb") as f:

    data = pickle.load(f)

bm25 = data["bm25"]
chunks = data["chunks"]


def tokenize(text):

    return text.lower().split()


def bm25_search(query, top_k=5):

    query_tokens = tokenize(query)

    scores = bm25.get_scores(query_tokens)

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for idx in top_indices:

        results.append({
            "score": float(scores[idx]),
            "text": chunks[idx]["text"],
            "metadata": chunks[idx]["metadata"]
        })

    return results


if __name__ == "__main__":

    query = "Who opposed separate electorates?"

    results = bm25_search(query)

    for r in results:

        print("\n====================")
        print("Score:", r["score"])
        print(r["metadata"])
        print(r["text"])