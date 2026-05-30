# graph_db/entity_extractor.py

import os
import json
import uuid
from tqdm import tqdm
from langchain_ollama import ChatOllama


# =========================================
# CONFIG
# =========================================

INPUT_DIRS = [
    # "processed/debates",
    # "processed/books",
    "processed/constitutions"
]

OUTPUT_DIR = "graph_db/extracted_entities"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================
# LLM
# =========================================

llm = ChatOllama(
    model="qwen2.5-coder:7b",
    base_url="http://127.0.0.1:11434",
    temperature=0.1
)


# =========================================
# PROMPT
# =========================================

SYSTEM_PROMPT = """
You are an expert legal and constitutional knowledge graph extractor.

Your task is to extract:

1. PEOPLE
2. ORGANIZATIONS
3. CONSTITUTIONAL CONCEPTS
4. ARTICLES
5. LAWS
6. EVENTS
7. RELATIONSHIPS

from the provided constitutional text chunk.

Return ONLY valid JSON.

Format:

{
  "entities": [
    {
      "name": "...",
      "type": "PERSON"
    }
  ],
  "relationships": [
    {
      "source": "...",
      "target": "...",
      "relation": "MENTIONED"
    }
  ]
}

Rules:
- Keep entity names clean.
- Avoid duplicates.
- Use uppercase relation names.
- No explanations.
- No markdown.
"""


# =========================================
# HELPERS
# =========================================

def safe_json_parse(text):

    try:
        return json.loads(text)

    except Exception:

        # attempt cleanup
        text = text.strip()

        if "```json" in text:
            text = text.split("```json")[1]

        if "```" in text:
            text = text.split("```")[0]

        text = text.strip()

        try:
            return json.loads(text)

        except Exception:
            return None


def build_prompt(chunk_text):

    return f"""
Extract entities and relationships from the following constitutional text.

TEXT:
{chunk_text}

JSON:
"""


# =========================================
# ENTITY EXTRACTION
# =========================================

def extract_from_chunk(chunk):

    text = chunk.get("text", "")

    if not text.strip():
        return None

    prompt = build_prompt(text)

    full_prompt = f"""
{SYSTEM_PROMPT}

{prompt}
"""

    try:

        response = llm.invoke(full_prompt)

        parsed = safe_json_parse(response.content)

        if parsed is None:
            return None

        return {
            "chunk_id": chunk.get("chunk_id"),
            "source_file": chunk.get("source_file"),
            "document_type": chunk.get("document_type"),
            "entities": parsed.get("entities", []),
            "relationships": parsed.get("relationships", [])
        }

    except Exception as e:

        print(f"Error extracting chunk: {e}")

        return None


# =========================================
# PROCESS FILE
# =========================================

def process_file(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    extracted = []

    print(f"\nProcessing: {filepath}")
    print(f"Chunks: {len(chunks)}")

    for chunk in tqdm(chunks):

        result = extract_from_chunk(chunk)

        if result:
            extracted.append(result)

    filename = os.path.basename(filepath)

    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)

    print(f"Saved -> {output_path}")
    print(f"Extracted entries: {len(extracted)}")


# =========================================
# MAIN
# =========================================

def run():

    for directory in INPUT_DIRS:

        if not os.path.exists(directory):
            continue

        files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.endswith(".json")
        ]

        for filepath in files:

            process_file(filepath)


if __name__ == "__main__":

    run()