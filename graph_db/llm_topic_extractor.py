import json
import time

from langchain_ollama import ChatOllama


# -------------------------
# LLM
# -------------------------

llm = ChatOllama(
    model="qwen2.5-coder:7b",
    base_url="http://127.0.0.1:11434",
    temperature=0.9,
)


# -------------------------
# PROMPT
# -------------------------

SYSTEM_PROMPT = """
You are an expert legal and constitutional entity extractor.

Your task is to extract ONLY meaningful constitutional and legal topics.

RULES:
1. Return ONLY valid JSON.
2. Do NOT explain anything.
3. Do NOT return markdown.
4. Keep topics concise.
5. Extract broad constitutional concepts.

Good examples:
- equality
- untouchability
- federalism
- reservation
- social justice
- democracy
- freedom of speech
- minority rights
- citizenship
- secularism

Bad examples:
- meeting
- discussion
- member spoke
- article said

Return format:

{
    "topics": [
        "topic1",
        "topic2"
    ]
}
"""


# -------------------------
# EXTRACT TOPICS
# -------------------------

def extract_topics_llm(text):

    prompt = f"""
    {SYSTEM_PROMPT}

    TEXT:
    {text[:3000]}
    """

    try:

        response = llm.invoke(prompt)

        content = response.content.strip()

        # remove markdown if model adds it
        content = content.replace("```json", "")
        content = content.replace("```", "")

        parsed = json.loads(content)

        topics = parsed.get("topics", [])

        cleaned = []

        for topic in topics:

            if isinstance(topic, str):

                topic = topic.strip().lower()

                if len(topic) > 2:

                    cleaned.append(topic)

        return list(set(cleaned))

    except Exception as e:

        print("LLM extraction error:", e)

        return []


# -------------------------
# TEST
# -------------------------

if __name__ == "__main__":

    sample = """
    B. R. Ambedkar argued that untouchability must be abolished
    and equality before law must be guaranteed through the Constitution.
    He also discussed fundamental rights and social justice.
    """

    topics = extract_topics_llm(sample)

    print("\nExtracted Topics:\n")

    print(topics)