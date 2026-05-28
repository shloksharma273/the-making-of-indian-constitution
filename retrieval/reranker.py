from sentence_transformers import CrossEncoder


model = CrossEncoder(
    "BAAI/bge-reranker-base"
)


def rerank(query, documents, top_k=8):

    pairs = [
        [query, doc]
        for doc in documents
    ]

    scores = model.predict(pairs)

    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]