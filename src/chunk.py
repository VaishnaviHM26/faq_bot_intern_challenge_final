from typing import List, Dict, Any
import re
print("NEW CHUNK.PY LOADED")
print("=" * 50)
print("CHUNK.PY LOADED")
print(__file__)
print("=" * 50)


def chunk_text(
    pages: List[Dict[str, Any]],
    chunk_size: int = 250,
    overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Splits each PDF page into overlapping chunks while preserving page numbers.
    """

    if not pages:
        return []
    print(type(pages))
    print(pages[:1])

    chunks = []
    chunk_id = 1

    step = max(1, chunk_size - overlap)

    for page in pages:

        page_number = page["page"]

        print("=" * 50)
        print("PAGE TYPE:", type(page))
        print("PAGE:", page)
        print("TEXT TYPE:", type(page["text"]))
        print("=" * 50)

        clean_text = str(page["text"])
        print("PAGE =", page)
        print("TYPE OF PAGE =", type(page))
        print("TYPE OF page['text'] =", type(page["text"]))

        clean_text = str(page["text"])
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        print(type(page["text"]))
        print(page["text"])

        if not clean_text:
            continue

        words = clean_text.split()

        # Small page
        if len(words) <= chunk_size:
            chunks.append({
                "id": chunk_id,
                "page": page_number,
                "text": clean_text,
                "word_count": len(words),
                "char_count": len(clean_text)
            })
            chunk_id += 1
            continue

        # Large page
        for start in range(0, len(words), step):

            end = min(start + chunk_size, len(words))

            chunk_words = words[start:end]

            if len(chunk_words) < max(20, overlap // 2):
                break

            chunk_str = " ".join(chunk_words)

            chunks.append({
                "id": chunk_id,
                "page": page_number,
                "text": chunk_str,
                "word_count": len(chunk_words),
                "char_count": len(chunk_str)
            })

            chunk_id += 1

            if end >= len(words):
                break

    return chunks