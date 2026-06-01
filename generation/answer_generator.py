# from langchain_ollama import ChatOllama


# llm = ChatOllama(
#     model="qwen2.5-coder:7b",
#     base_url="http://127.0.0.1:11434",
#     temperature=0.2,
# )


# SYSTEM_PROMPT = """
# You are an expert constitutional historian and legal assistant.

# Answer ONLY from the provided context.

# If the answer is not present in the context, say:
# 'I could not find sufficient information in the retrieved documents.'

# Always cite:
# - speaker names
# - constitution names
# - debate references
# when available.
# """


# # -------------------------
# # BUILD CONTEXT
# # -------------------------

# def build_context(results):

#     context = ""

#     for i, item in enumerate(results):

#         context += f"\n\nDOCUMENT {i+1}\n"

#         context += item["text"]

#     # print(f"Built context from {len(results)} documents")
#     return context


# # -------------------------
# # GENERATE ANSWER
# # -------------------------

# def generate_answer(query, retrieved_chunks):

#     context = build_context(retrieved_chunks)

#     prompt = f"""
#         QUESTION:
#         {query}

#         CONTEXT:
#         {context}

#         ANSWER:
#         """

#     full_prompt = f"""
#         {SYSTEM_PROMPT}

#         {prompt}
#         """

#     response = llm.invoke(full_prompt)

#     return response.content





from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen2.5-coder:7b",
    base_url="http://127.0.0.1:11434",
    temperature=0.2,
)


SYSTEM_PROMPT = """
You are an expert constitutional historian.

Answer ONLY from the provided context.

Rules:
1. Quote speakers whenever possible.
2. Mention the source document whenever available.
3. Use direct evidence from retrieved documents.
4. If multiple documents disagree, mention the disagreement.
5. Do not make assumptions beyond the context.
6. Prefer factual extraction over summarization.
"""


# -------------------------
# FILTER BAD CHUNKS
# -------------------------

def filter_chunks(chunks, threshold=0.001):

    filtered = []

    for chunk in chunks:

        rerank_score = chunk.get("rerank_score", 0)

        text = chunk.get("text", "").strip()

        # skip tiny/noisy chunks
        if len(text) < 80:
            continue

        # skip weak rerank matches
        if rerank_score < threshold:
            continue

        filtered.append(chunk)

    return filtered


# -------------------------
# BUILD CONTEXT
# -------------------------

def build_context(results):

    context = ""

    for i, item in enumerate(results):

        context += f"\n\n===== DOCUMENT {i+1} =====\n\n"

        context += item["text"]

    return context


# -------------------------
# GENERATE ANSWER
# -------------------------

def generate_answer(query, retrieved_chunks):

    # STEP 1: FILTER
    # filtered_chunks = filter_chunks(retrieved_chunks, threshold=0.005)

    # print(f"Filtered chunks: {len(filtered_chunks)}")

    # # STEP 2: HANDLE EMPTY
    # if len(filtered_chunks) == 0:

    #     return "I could not find sufficient information in the retrieved documents."

    # STEP 3: BUILD CONTEXT
    context = build_context(retrieved_chunks)

    # DEBUG
    print("\n===== FINAL CONTEXT =====")
    print(context[:3000])

    # STEP 4: PROMPT
    full_prompt = f"""
    {SYSTEM_PROMPT}

    QUESTION:
    {query}

    CONTEXT:
    {context}

    ANSWER:
    """

    # STEP 5: GENERATE
    response = llm.invoke(full_prompt)

    return response.content