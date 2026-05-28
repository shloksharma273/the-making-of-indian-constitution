import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_PATH = "vector_db/chroma_store"

COLLECTION_NAME = "constitution_rag"


# SAME embedding model used during ingestion
EMBED_MODEL = "BAAI/bge-base-en-v1.5"


# -----------------------------------
# Load embedding model
# -----------------------------------

model = SentenceTransformer(EMBED_MODEL)


# -----------------------------------
# Connect Chroma
# -----------------------------------

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


# -----------------------------------
# Query function
# -----------------------------------

def search(query, top_k=5):

    print("\nQUERY:")
    print(query)

    print("\nGenerating embedding...\n")

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("=" * 80)

    for idx, (doc, meta, dist) in enumerate(
        zip(documents, metadatas, distances)
    ):

        print(f"\nRESULT #{idx+1}")
        print("-" * 80)

        print(f"Distance: {dist}")

        print("\nMetadata:")
        print(meta)

        print("\nText:")
        print(doc[:1500])

        print("\n" + "=" * 80)


# -----------------------------------
# Main
# -----------------------------------

if __name__ == "__main__":

    while True:

        query = input("\nEnter query (or 'exit'): ")

        if query.lower() == "exit":
            break

        search(query)