import re



def clean_text(text):

    text = re.sub(r'-\s*\n\s*', '', text)

    text = re.sub(r'¬\s*', '', text)

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def remove_preface(text: str):

    patterns = [
        r"AUNDH STATE CONSTITUTION ACT",
        r"WHEREAS",
        r"ARTICLE\s+1",
        r"[A-Z]{2,10}\.\d+"
    ]

    positions = []

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            positions.append(match.start())

    if positions:

        start = min(positions)

        return text[start:]

    return text