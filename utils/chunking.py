import re
from typing import List, Dict


def parse_debate_sections(text: str) -> List[Dict]:

    pattern = r"(\d+\.\d+\.\d+)"

    splits = re.split(pattern, text)

    sections = []

    for i in range(1, len(splits), 2):

        section_id = splits[i].strip()

        content = splits[i + 1].strip()

        if len(content) < 50:
            continue

        speaker = extract_speaker(content)

        sections.append({
            "section_id": section_id,
            "speaker": speaker,
            "text": content
        })

    return sections


def extract_speaker(text: str):

    lines = text.split("\n")

    for line in lines[:10]:

        cleaned = line.strip()

        if (
            len(cleaned) < 50
            and cleaned.isupper() == False
            and len(cleaned.split()) <= 6
        ):
            return cleaned

    return None



def parse_constitution_sections(text: str) -> List[Dict]:

    legal_pattern = r"([A-Z]{2,10}\.\d+|ARTICLE\s+\d+|Article\s+\d+|Section\s+\d+)"

    splits = re.split(legal_pattern, text)

    sections = []

    current_condition = None
    current_heading = None

    for i in range(1, len(splits), 2):

        section_id = splits[i].strip()

        content = splits[i + 1].strip()

        if len(content) < 80:
            continue

        condition = extract_condition(content)

        heading = extract_heading(content)

        if condition:
            current_condition = condition

        if heading:
            current_heading = heading

        sections.append({

            "section_id": section_id,

            "condition": current_condition,

            "section_title": current_heading,

            "text": content

        })

    return sections



def extract_condition(text: str):

    match = re.search(
        r"(Condition No\.\s*[IVX0-9]+)",
        text
    )

    if match:
        return match.group(1)

    return None


def extract_heading(text: str):

    lines = text.split("\n")

    for line in lines[:10]:

        cleaned = line.strip()

        if (
            cleaned.isupper()
            and 3 < len(cleaned) < 80
        ):
            return cleaned

    return None



from typing import List, Dict
import re


def semantic_book_chunker(
    text: str,
    window_size: int = 4,
    overlap: int = 2
) -> List[Dict]:

    paragraphs = split_paragraphs(text)

    chunks = []

    step = window_size - overlap

    for i in range(0, len(paragraphs), step):

        window = paragraphs[i:i + window_size]

        if len(window) == 0:
            continue

        chunk_text = "\n\n".join(window)

        if len(chunk_text.split()) < 120:
            continue

        chunks.append({

            "chunk_index": i,

            "text": chunk_text

        })

    # print(chunks[:20])

    return chunks




def split_paragraphs(text: str):

    text = text.replace("\r", "\n")

    raw_paragraphs = re.split(r"\n\s*\n", text)

    paragraphs = []

    for para in raw_paragraphs:

        cleaned = para.strip()

        if len(cleaned) < 40:
            continue

        paragraphs.append(cleaned)

    return paragraphs