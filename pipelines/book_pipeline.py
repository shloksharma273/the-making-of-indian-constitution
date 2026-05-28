import os
import json

from uuid import uuid4

from utils.cleaners import clean_text
from utils.chunking import semantic_book_chunker
from utils.embedding import generate_embedding

from models.schemas import ChunkSchema
import hashlib

INPUT_DIR = "data/books"
OUTPUT_DIR = "processed/books"

os.makedirs(OUTPUT_DIR, exist_ok=True)



def process_file(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # cleaned = clean_text(raw_text)

    document_id = hashlib.md5(os.path.basename(filepath).encode()).hexdigest()

    chunks = semantic_book_chunker(raw_text)

    all_chunks = []

    for chunk in chunks:

        chunk_text = chunk["text"]

        embedding = generate_embedding(chunk_text)

        chunk_obj = ChunkSchema(

            chunk_id=str(uuid4()),

            document_type="book",

            source_file=os.path.basename(filepath),

            text=chunk_text,

            tokens=len(chunk_text.split()),

            embedding=embedding,

            metadata={
                    "chunk_index": chunk["chunk_index"], 
                    "document_id": document_id
                    },
        )

        all_chunks.append(
            chunk_obj.model_dump()
        )

    output_path = os.path.join(
        OUTPUT_DIR,
        os.path.basename(filepath).replace(".txt", ".json")
    )

    with open(output_path, "w", encoding="utf-8") as f:

        json.dump(
            all_chunks,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"Processed: {filepath}")


def run():

    files = [
        os.path.join(INPUT_DIR, f)
        for f in os.listdir(INPUT_DIR)
        if f.endswith(".txt")
    ]

    for file in files:
        process_file(file)


if __name__ == "__main__":
    run()




# import os
# import json
# import re

# from uuid import uuid4

# from models.schemas import ChunkSchema
# from utils.cleaners import clean_text
# from utils.embedding import generate_embedding
# from utils.chunking import semantic_book_chunker


# INPUT_DIR = "data/books"
# OUTPUT_DIR = "processed/books"

# os.makedirs(OUTPUT_DIR, exist_ok=True)


# # -----------------------------------------
# # Extract chapter / section metadata
# # -----------------------------------------

# def extract_book_metadata(text):

#     metadata = {}

#     # CHAPTER 1
#     chapter_match = re.search(
#         r"(CHAPTER\s+[A-Z0-9IVX]+)",
#         text,
#         re.IGNORECASE
#     )

#     if chapter_match:
#         metadata["chapter"] = chapter_match.group(1)

#     # PART I
#     part_match = re.search(
#         r"(PART\s+[A-Z0-9IVX]+)",
#         text,
#         re.IGNORECASE
#     )

#     if part_match:
#         metadata["part"] = part_match.group(1)

#     # Article 14
#     article_match = re.search(
#         r"(Article\s+\d+[A-Z\-]*)",
#         text,
#         re.IGNORECASE
#     )

#     if article_match:
#         metadata["article"] = article_match.group(1)

#     return metadata


# # -----------------------------------------
# # Process single book
# # -----------------------------------------

# def process_file(filepath):

#     print(f"\nProcessing: {filepath}")

#     with open(filepath, "r", encoding="utf-8") as f:
#         raw_text = f.read()

#     # Clean OCR noise
#     cleaned_text = clean_text(raw_text)

#     # Semantic chunking
#     chunks = semantic_book_chunker(cleaned_text)

#     all_chunks = []

#     for idx, chunk_text in enumerate(chunks):

#         chunk_text = chunk_text.strip()

#         if len(chunk_text) < 100:
#             continue

#         metadata = extract_book_metadata(chunk_text)

#         embedding = generate_embedding(chunk_text)

#         chunk_obj = ChunkSchema(
#             chunk_id=str(uuid4()),
#             document_type="book",
#             source_file=os.path.basename(filepath),
#             title=os.path.basename(filepath).replace(".txt", ""),
#             speaker=None,
#             date=None,
#             text=chunk_text,
#             tokens=len(chunk_text.split()),
#             keywords=[],
#             metadata=metadata,
#             embedding=embedding
#         )

#         all_chunks.append(
#             chunk_obj.model_dump()
#         )

#         print(f"Chunked: {idx + 1}", end="\r")

#     # Save JSON
#     output_path = os.path.join(
#         OUTPUT_DIR,
#         os.path.basename(filepath).replace(".txt", ".json")
#     )

#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(
#             all_chunks,
#             f,
#             ensure_ascii=False,
#             indent=2
#         )

#     print(f"\nSaved {len(all_chunks)} chunks -> {output_path}")


# # -----------------------------------------
# # Run pipeline
# # -----------------------------------------

# def run():

#     files = [
#         os.path.join(INPUT_DIR, f)
#         for f in os.listdir(INPUT_DIR)
#         if f.endswith(".txt")
#     ]

#     print(f"Found {len(files)} books")

#     for filepath in files:

#         try:
#             process_file(filepath)

#         except Exception as e:

#             print(f"\nERROR in {filepath}")
#             print(str(e))


# if __name__ == "__main__":
#     run()