import re


def extract_entities(query):

    entities = []

    matches = re.findall(
        r"\b[A-Z][a-z]+\b",
        query
    )

    entities.extend(matches)

    return list(set(entities))
