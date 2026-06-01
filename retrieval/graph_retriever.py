from retrieval.query_entities import extract_entities

from retrieval.graph_search import (
    get_chunks_for_entity,
    get_neighbor_chunks
)


def graph_retrieve(query):

    entities = extract_entities(query)

    results = []

    for entity in entities:

        results.extend(
            get_chunks_for_entity(entity)
        )

        results.extend(
            get_neighbor_chunks(entity)
        )

    unique = {}

    for item in results:

        unique[item["chunk_id"]] = item

    return list(unique.values())