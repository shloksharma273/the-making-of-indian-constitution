# agents/state.py

from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict, total=False):

    # user query
    query: str

    # vector + bm25 retrieval results
    retrieved_docs: List[Dict[str, Any]]

    # neo4j retrieval results
    graph_results: List[Dict[str, Any]]

    # reranked chunks
    reranked_docs: List[Dict[str, Any]]

    # final answer
    answer: str

    # debug information
    metadata: Dict[str, Any]