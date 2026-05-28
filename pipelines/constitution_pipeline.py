import os
import json

from uuid import uuid4

from utils.cleaners import clean_text
from utils.chunking import parse_constitution_sections
from utils.embedding import generate_embedding

from models.schemas import ChunkSchema


INPUT_DIR = "data/constitutions"
OUTPUT_DIR = "processed/constitutions"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def process_file(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned = clean_text(raw_text)

    sections = parse_constitution_sections(cleaned)

    all_chunks = []

    for section in sections:

        chunk_text = section["text"]

        if len(chunk_text.strip()) < 80:
            continue

        embedding = generate_embedding(chunk_text)

        chunk_obj = ChunkSchema(

            chunk_id=str(uuid4()),

            document_type="constitution",

            source_file=os.path.basename(filepath),

            title=section["section_title"],

            text=chunk_text,

            tokens=len(chunk_text.split()),

            metadata={
                "section_id": section["section_id"],
                "condition": section["condition"]
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