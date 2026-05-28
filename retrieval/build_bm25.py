import os
import json
import pickle

from rank_bm25 import BM25Okapi


DATA_DIRS = [
    "processed/debates",
    "processed/constitutions",
    "processed/books"
]

all_chunks = []
tokenized_corpus = []


def tokenize(text):

    return text.lower().split()


for directory in DATA_DIRS:

    for file in os.listdir(directory):

        if not file.endswith(".json"):
            continue

        filepath = os.path.join(directory, file)

        with open(filepath, "r", encoding="utf-8") as f:

            chunks = json.load(f)

        for chunk in chunks:

            text = chunk["text"]

            all_chunks.append(chunk)

            tokenized_corpus.append(
                tokenize(text)
            )


bm25 = BM25Okapi(tokenized_corpus)


with open("retrieval/bm25_index.pkl", "wb") as f:

    pickle.dump(
        {
            "bm25": bm25,
            "chunks": all_chunks
        },
        f
    )

print(f"BM25 indexed {len(all_chunks)} chunks")