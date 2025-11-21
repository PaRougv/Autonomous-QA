from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
import json


def parse_support_document(filename: str, content: str) -> str:
    """
    For .md, .txt: return as-is.
    For .json: pretty-print.
    You can extend this for PDF, etc.
    """
    lower = filename.lower()
    if lower.endswith(".json"):
        try:
            obj = json.loads(content)
            return json.dumps(obj, indent=2)
        except Exception:
            return content
    else:
        # .md, .txt, others – treat as plain text
        return content


def parse_checkout_html(content: str) -> Tuple[str, str]:
    """
    Returns:
      - full_html (original)
      - extracted_text (for KB)
    """
    full_html = content
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text(separator="\n")
    return full_html, text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Simple character-based chunking.
    """
    text = text.replace("\r", "")
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
        if start < 0:
            start = 0
        if start >= len(text):
            break
    # Filter out empty chunks
    return [c for c in chunks if c]
