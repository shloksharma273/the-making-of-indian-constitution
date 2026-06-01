# agents/graph_builder.py

from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.router import router
from agents.nodes import (
    document_node,
    graph_node,
    answer_node
)


def build_graph():

    builder = StateGraph(
        AgentState
    )

    builder.add_node(
        "documents",
        document_node
    )

    builder.add_node(
        "graph",
        graph_node
    )

    builder.add_node(
        "answer",
        answer_node
    )

    builder.set_conditional_entry_point(
        router,
        {
            "documents": "documents",
            "graph": "graph"
        }
    )

    builder.add_edge(
        "documents",
        "answer"
    )

    builder.add_edge(
        "graph",
        "answer"
    )

    builder.add_edge(
        "answer",
        END
    )

    return builder.compile()