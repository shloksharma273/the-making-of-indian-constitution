# agents/nodes.py

from agents.tools import (
    document_tool,
    graph_tool
)

from generation.answer_generator import generate_answer


def document_node(state):

    docs = document_tool(
        state["query"]
    )

    state["retrieved_docs"] = docs

    return state


def graph_node(state):

    graph_results = graph_tool(
        state["query"]
    )

    state["graph_results"] = graph_results

    return state


def answer_node(state):

    chunks = []

    if state.get("retrieved_docs"):

        chunks.extend(
            state["retrieved_docs"]
        )

    if state.get("graph_results"):

        chunks.extend(
            state["graph_results"]
        )

    answer = generate_answer(
        state["query"],
        chunks
    )

    state["answer"] = answer

    return state