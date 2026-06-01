# agents/tools.py

from retrieval.hybrid_search import hybrid_search
from graph_db.graph_retriever import graph_retrieve


# =========================================
# DOCUMENT TOOL
# =========================================

def document_tool(query):

    results = hybrid_search(query)

    return results


# =========================================
# GRAPH TOOL
# =========================================

def graph_tool(query):

    results = graph_retrieve(query)

    return results