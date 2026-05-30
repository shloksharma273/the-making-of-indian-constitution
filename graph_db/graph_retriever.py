# graph_db/graph_retriever.py

import json
import re
from neo4j import GraphDatabase
from langchain_ollama import ChatOllama


# =========================================
# NEO4J CONFIG
# =========================================

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"


# =========================================
# LLM
# =========================================

llm = ChatOllama(
    model="qwen2.5-coder:7b",
    base_url="http://127.0.0.1:11434",
    temperature=0.1,
)


# =========================================
# NEO4J DRIVER
# =========================================

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


# =========================================
# ENTITY EXTRACTION PROMPT
# =========================================

ENTITY_PROMPT = """
Extract important entities from the query.

Focus on:
- PERSON
- CONCEPT
- LAW
- ARTICLE
- ORGANIZATION
- EVENT

Return ONLY JSON.

Format:
{
    "entities": [
        {
            "name": "...",
            "type": "..."
        }
    ]
}
"""


# =========================================
# SAFE JSON PARSER
# =========================================

def safe_json_parse(text):

    try:
        return json.loads(text)

    except Exception:

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


# =========================================
# EXTRACT ENTITIES FROM QUERY
# =========================================

def extract_query_entities(query):

    prompt = f"""
{ENTITY_PROMPT}

QUERY:
{query}

JSON:
"""

    response = llm.invoke(prompt)

    parsed = safe_json_parse(response.content)

    if parsed is None:
        return []

    return parsed.get("entities", [])


# =========================================
# NEO4J SEARCH
# =========================================

def search_entity_connections(entity_name):

    query = """
    MATCH (e)-[r]-(connected)
    WHERE toLower(e.name) CONTAINS toLower($name)

    RETURN
        e.name AS source,
        type(r) AS relation,
        connected.name AS target,
        labels(connected) AS labels

    LIMIT 20
    """

    with driver.session() as session:

        result = session.run(
            query,
            name=entity_name
        )

        return [dict(record) for record in result]


# =========================================
# GRAPH RETRIEVAL
# =========================================

def graph_retrieve(query):

    entities = extract_query_entities(query)

    print("\n===== EXTRACTED ENTITIES =====\n")
    print(entities)

    all_connections = []

    for entity in entities:

        entity_name = entity["name"]

        connections = search_entity_connections(entity_name)

        if connections:

            all_connections.extend(connections)

    return all_connections


# =========================================
# BUILD GRAPH CONTEXT
# =========================================

def build_graph_context(graph_results):

    context = ""

    for item in graph_results:

        line = (
            f"{item['source']} "
            f"--[{item['relation']}]--> "
            f"{item['target']}"
        )

        context += line + "\n"

    return context


# =========================================
# TEST
# =========================================

if __name__ == "__main__":

    query = "What did Ambedkar say about untouchability?"

    results = graph_retrieve(query)

    print("\n===== GRAPH RESULTS =====\n")

    for r in results:

        print(r)

    graph_context = build_graph_context(results)

    print("\n===== GRAPH CONTEXT =====\n")

    print(graph_context)