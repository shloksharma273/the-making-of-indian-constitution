import os
import json
from uuid import uuid4
import hashlib
from torch import chunk
from utils.cleaners import clean_text
from utils.chunking import parse_debate_sections
from utils.embedding import generate_embedding

from models.schemas import ChunkSchema


INPUT_DIR = "data/debates"
OUTPUT_DIR = "processed/debates"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def process_file(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned = clean_text(raw_text)

    sections = parse_debate_sections(cleaned)

    document_id = hashlib.md5(
    os.path.basename(filepath).encode()
).hexdigest()

    all_chunks = []

    for idx, chunk_data in enumerate(sections):

        chunk_text = chunk_data["text"]

        if len(chunk_text.strip()) < 50:
            continue

        embedding = generate_embedding(chunk_text)

        chunk_obj = ChunkSchema(

        chunk_id=str(uuid4()),

        document_type="debate",

        source_file=os.path.basename(filepath),

        title=None,

        text=chunk_text,

        tokens=len(chunk_text.split()),

        metadata={
            "speaker": chunk_data["speaker"],
            "document_id": document_id
        },

        embedding=embedding
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
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned = clean_text(raw_text)

    sections = parse_debate_sections(cleaned)

    all_chunks = []

    for idx, chunk_data in enumerate(sections):

        chunk_text = chunk_data["text"]

        # skip tiny chunks
        if len(chunk_text.strip()) < 50:
            continue

        embedding = generate_embedding(chunk_text)

        chunk_obj = ChunkSchema(
            chunk_id=str(uuid4()),
            document_type="debate",
            source_file=os.path.basename(filepath),

            speaker=chunk_data["speaker"],

            text=chunk_text,

            tokens=len(chunk_text.split()),

            embedding=embedding
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
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned = clean_text(raw_text)

    sections = parse_debate_sections(cleaned)

    all_chunks = []


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