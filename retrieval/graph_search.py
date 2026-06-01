from neo4j import GraphDatabase
from dotenv import load_dotenv

import os

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USERNAME"),
        os.getenv("NEO4J_PASSWORD")
    )
)


def get_chunks_for_entity(
    entity_name,
    limit=20
):

    query = """
    MATCH (e:Entity)-[:MENTIONED_IN]->(c:Chunk)

    WHERE toLower(e.name)
          CONTAINS toLower($entity)

    RETURN
        c.chunk_id AS chunk_id,
        c.text AS text,
        c.source_file AS source_file

    LIMIT $limit
    """

    with driver.session() as session:

        result = session.run(
            query,
            entity=entity_name,
            limit=limit
        )

        return [dict(r) for r in result]


def get_neighbor_chunks(
    entity_name,
    hops=1,
    limit=50
):

    query = """
    MATCH (e:Entity)

    WHERE toLower(e.name)
          CONTAINS toLower($entity)

    MATCH path=(e)-[*1..2]-(other:Entity)

    MATCH (other)-[:MENTIONED_IN]->(c:Chunk)

    RETURN DISTINCT
        c.chunk_id AS chunk_id,
        c.text AS text,
        c.source_file AS source_file

    LIMIT $limit
    """

    with driver.session() as session:

        result = session.run(
            query,
            entity=entity_name,
            limit=limit
        )

        return [dict(r) for r in result]