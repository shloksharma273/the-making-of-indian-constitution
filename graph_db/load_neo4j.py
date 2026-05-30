# graph_db/load_neo4j.py

import os
import json

from tqdm import tqdm
from neo4j import GraphDatabase
from dotenv import load_dotenv
import re

load_dotenv()

# =========================================
# CONFIG
# =========================================

EXTRACTED_DIR = "graph_db/extracted_entities"

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")


# =========================================
# VALIDATE ENV
# =========================================

if not URI:
    raise ValueError("NEO4J_URI missing in .env")

if not USERNAME:
    raise ValueError("NEO4J_USERNAME missing in .env")

if not PASSWORD:
    raise ValueError("NEO4J_PASSWORD missing in .env")


# =========================================
# CONNECT
# =========================================

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# =========================================
# CREATE CONSTRAINTS
# =========================================

def create_constraints():

    queries = [

        """
        CREATE CONSTRAINT entity_name_unique IF NOT EXISTS
        FOR (e:Entity)
        REQUIRE e.name IS UNIQUE
        """,

        """
        CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
        FOR (c:Chunk)
        REQUIRE c.chunk_id IS UNIQUE
        """
    ]

    with driver.session() as session:

        for query in queries:

            session.run(query)

    print("Constraints created")


# =========================================
# CREATE ENTITY NODE
# =========================================

def create_entity(tx, entity):

    query = """
    MERGE (e:Entity {
        name: $name
    })

    SET e.type = $type
    """

    tx.run(
        query,
        name=entity.get("name", ""),
        type=entity.get("type", "UNKNOWN")
    )


# =========================================
# CREATE CHUNK NODE
# =========================================

def create_chunk(tx, chunk):

    query = """
    MERGE (c:Chunk {
        chunk_id: $chunk_id
    })

    SET
        c.text = $text,
        c.source_file = $source_file,
        c.document_type = $document_type
    """

    tx.run(
        query,
        chunk_id=chunk.get("chunk_id", ""),
        text=chunk.get("text", ""),
        source_file=chunk.get("source_file", ""),
        document_type=chunk.get("document_type", "")
    )


# =========================================
# LINK ENTITY TO CHUNK
# =========================================

def link_entity_to_chunk(tx, entity_name, chunk_id):

    query = """
    MATCH (e:Entity {
        name: $entity_name
    })

    MATCH (c:Chunk {
        chunk_id: $chunk_id
    })

    MERGE (e)-[:MENTIONED_IN]->(c)
    """

    tx.run(
        query,
        entity_name=entity_name,
        chunk_id=chunk_id
    )


# =========================================
# SANITIZE RELATIONSHIP TYPE
# =========================================

def sanitize_relationship(rel):

    if not rel:
        return "RELATED_TO"

    rel = rel.upper()

    # Convert spaces, hyphens, slashes, dots, etc. to _
    rel = re.sub(r"[^A-Z0-9]+", "_", rel)

    rel = rel.strip("_")

    if not rel:
        rel = "RELATED_TO"

    return rel


# =========================================
# CREATE RELATIONSHIP
# =========================================

def create_relationship(tx, source, target, relation):

    relation = sanitize_relationship(relation)

    query = f"""
    MATCH (a:Entity {{
        name: $source
    }})

    MATCH (b:Entity {{
        name: $target
    }})

    MERGE (a)-[r:{relation}]->(b)
    """

    tx.run(
        query,
        source=source,
        target=target
    )
# =========================================
# PROCESS FILE
# =========================================

def process_file(filepath):

    with open(filepath, "r", encoding="utf-8") as f:

        data = json.load(f)

    print(f"\nProcessing: {filepath}")
    print(f"Entries: {len(data)}")

    with driver.session() as session:

        for item in tqdm(data):

            chunk_id = item.get("chunk_id")

            if not chunk_id:
                continue

            # -------------------------
            # CREATE CHUNK
            # -------------------------

            session.execute_write(
                create_chunk,
                item
            )

            # -------------------------
            # ENTITIES
            # -------------------------

            entities = item.get("entities", [])

            for entity in entities:

                if not isinstance(entity, dict):
                    continue

                if "name" not in entity:
                    continue

                session.execute_write(
                    create_entity,
                    entity
                )

                session.execute_write(
                    link_entity_to_chunk,
                    entity["name"],
                    chunk_id
                )

            # -------------------------
            # RELATIONSHIPS
            # -------------------------

            relationships = item.get("relationships", [])

            for rel in relationships:

                if not isinstance(rel, dict):
                    continue

                if (
                    "source" not in rel or
                    "target" not in rel or
                    "relation" not in rel
                ):
                    continue

                session.execute_write(
                    create_relationship,
                    rel["source"],
                    rel["target"],
                    rel["relation"]
                )

    print(f"Completed: {filepath}")


# =========================================
# MAIN
# =========================================

def run():

    create_constraints()

    # -------------------------
    # FIND FILES
    # -------------------------

    if not os.path.exists(EXTRACTED_DIR):

        print(f"\nDirectory not found: {EXTRACTED_DIR}")
        return

    all_files = [
        os.path.join(EXTRACTED_DIR, f)
        for f in os.listdir(EXTRACTED_DIR)
        if f.endswith(".json")
    ]

    print(f"\nFound {len(all_files)} files")

    if len(all_files) == 0:

        print("\nNo extracted entity files found.")
        return

    # -------------------------
    # PROCESS FILES
    # -------------------------

    for filepath in all_files:

        process_file(filepath)

    print("\nNeo4j loading complete")


# =========================================
# ENTRY
# =========================================

if __name__ == "__main__":

    run()