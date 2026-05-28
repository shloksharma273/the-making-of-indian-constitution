import os
import json
import chromadb

from chromadb.config import Settings


CHROMA_PATH = "vector_db/chroma_store"

DATA_DIRS = [
    "processed/debates",
    "processed/constitutions",
    "processed/books"
]


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name="constitution_rag"
)


def load_json_file(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def insert_chunks(chunks, batch_size=4000):

    total = len(chunks)

    for start in range(0, total, batch_size):

        end = start + batch_size

        batch = chunks[start:end]

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for chunk in batch:

            ids.append(chunk["chunk_id"])

            documents.append(chunk["text"])

            embeddings.append(chunk["embedding"])

            metadata = {
                "document_type": chunk["document_type"],
                "source_file": chunk["source_file"]
            }

            if "metadatas" in chunk:

                for key, value in chunk["metadata"].items():

                    if isinstance(value, (str, int, float, bool)) or value is None:
                        metadata[key] = value

                    else:
                        metadata[key] = str(value)

            metadatas.append(metadata)
        
        if len(ids) == 0:
            print("Skipping empty batch")
            continue
        
        assert len(ids) == len(documents) == len(embeddings) == len(metadatas)
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        print(f"Inserted batch {start} -> {end}")
    

def run():

    total = 0

    for directory in DATA_DIRS:

        files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.endswith(".json")
        ]

        for file in files:

            chunks = load_json_file(file)

            if not chunks:
                print(f"Skipping empty file: {file}")
                continue

            print(f"Loaded {len(chunks)} chunks from {file}")

            insert_chunks(chunks)

            total += len(chunks)

            print(f"Inserted {len(chunks)} chunks from {file}")

    print(f"\nTotal inserted chunks: {total}")


if __name__ == "__main__":
    run()