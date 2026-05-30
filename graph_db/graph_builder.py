import os
import json

from neo4j_loader import run_query
from entity_extractor import (
    extract_speaker,
    extract_articles,
    extract_topics
)


DATA_DIRS = [
    "processed/debates",
    "processed/books",
    "processed/constitutions"
]


# -------------------------
# CREATE CONSTRAINTS
# -------------------------

def create_constraints():

    queries = [

        "CREATE CONSTRAINT speaker_name IF NOT EXISTS FOR (s:Speaker) REQUIRE s.name IS UNIQUE",

        "CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",

        "CREATE CONSTRAINT article_name IF NOT EXISTS FOR (a:Article) REQUIRE a.name IS UNIQUE",

        "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.chunk_id IS UNIQUE"
    ]

    for query in queries:

        run_query(query)

    print("Constraints created")


# -------------------------
# INSERT CHUNK
# -------------------------

def insert_chunk(chunk):

    chunk_id = chunk["chunk_id"]

    text = chunk["text"]

    metadata = chunk.get("metadata", {})

    speaker = extract_speaker(text)

    topics = extract_topics(text)

    articles = extract_articles(text)


    # -------------------------
    # CREATE CHUNK NODE
    # -------------------------

    chunk_query = """
    MERGE (c:Chunk {chunk_id: $chunk_id})

    SET c.text = $text
    """

    run_query(chunk_query, {
        "chunk_id": chunk_id,
        "text": text
    })


    # -------------------------
    # SPEAKER
    # -------------------------

    if speaker:

        speaker_query = """
        MERGE (s:Speaker {name: $speaker})

        WITH s

        MATCH (c:Chunk {chunk_id: $chunk_id})

        MERGE (s)-[:SPOKE_IN]->(c)
        """

        run_query(speaker_query, {
            "speaker": speaker,
            "chunk_id": chunk_id
        })


    # -------------------------
    # TOPICS
    # -------------------------

    for topic in topics:

        topic_query = """
        MERGE (t:Topic {name: $topic})

        WITH t

        MATCH (c:Chunk {chunk_id: $chunk_id})

        MERGE (c)-[:MENTIONS]->(t)
        """

        run_query(topic_query, {
            "topic": topic,
            "chunk_id": chunk_id
        })


    # -------------------------
    # ARTICLES
    # -------------------------

    for article in articles:

        article_query = """
        MERGE (a:Article {name: $article})

        WITH a

        MATCH (c:Chunk {chunk_id: $chunk_id})

        MERGE (c)-[:REFERS_TO]->(a)
        """

        run_query(article_query, {
            "article": article,
            "chunk_id": chunk_id
        })


# -------------------------
# PROCESS FILE
# -------------------------

def process_file(filepath):

    with open(filepath, "r", encoding="utf-8") as f:

        chunks = json.load(f)

    print(f"Processing {filepath}")

    for chunk in chunks[:5]:

        insert_chunk(chunk)

    print(f"Inserted {len(chunks)} chunks")


# -------------------------
# MAIN
# -------------------------

def run():

    create_constraints()

    for directory in DATA_DIRS:

        if not os.path.exists(directory):
            continue

        files = [

            os.path.join(directory, f)

            for f in os.listdir(directory)

            if f.endswith(".json")
        ]

        for file in files:

            process_file(file)


if __name__ == "__main__":

    run()