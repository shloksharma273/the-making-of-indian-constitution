# agents/router.py

from agents.state import AgentState


def router(state: AgentState):

    query = state["query"].lower()

    graph_keywords = [
        "relationship",
        "connected",
        "linked",
        "network",
        "entity",
        "speaker",
        "who mentioned",
        "who spoke"
    ]

    for keyword in graph_keywords:

        if keyword in query:

            return "graph"

    return "documents"