import os
import json
from typing import List, Dict, Any

import numpy as np
from sentence_transformers import SentenceTransformer

from .vector_store import SimpleVectorStore
from .parsers import parse_support_document, parse_checkout_html, chunk_text
from .llm_client import call_llm
from .models import TestCase


# use a lightweight sentence-transformer
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_embedding_model: SentenceTransformer = None
_vector_store = SimpleVectorStore(
    path=os.path.join(os.path.dirname(__file__), "..", "kb_store.pkl")
)


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def build_knowledge_base(documents: List[Dict[str, Any]]) -> int:
    """
    documents: list of dicts: {filename, content, doc_type}
      doc_type: "support" or "html"
    Returns: num_chunks
    """
    model = get_embedding_model()

    all_chunks: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    html_full_content = ""

    # reset store
    _vector_store.reset()

    for doc in documents:
        filename = doc["filename"]
        content = doc["content"]
        doc_type = doc["doc_type"]

        if doc_type == "support":
            parsed_text = parse_support_document(filename, content)
            chunks = chunk_text(parsed_text)
            for c in chunks:
                all_chunks.append(c)
                metadatas.append({"source": filename, "doc_type": "support"})
        elif doc_type == "html":
            full_html, html_text = parse_checkout_html(content)
            html_full_content = full_html
            chunks = chunk_text(html_text)
            for c in chunks:
                all_chunks.append(c)
                metadatas.append({"source": filename, "doc_type": "html"})
        else:
            # fallback treat as support text
            chunks = chunk_text(content)
            for c in chunks:
                all_chunks.append(c)
                metadatas.append({"source": filename, "doc_type": "unknown"})

    if not all_chunks:
        return 0

    embeddings = model.encode(all_chunks, convert_to_numpy=True)
    _vector_store.add_documents(
        embeddings=embeddings,
        texts=all_chunks,
        metadatas=metadatas,
        html_full=html_full_content,
    )

    return len(all_chunks)


def retrieve_context(query: str, top_k: int = 8) -> Dict[str, Any]:
    if _vector_store.is_empty():
        raise RuntimeError("Knowledge base is empty. Build it first.")

    model = get_embedding_model()
    q_emb = model.encode([query], convert_to_numpy=True)[0]
    hits = _vector_store.similarity_search(q_emb, top_k=top_k)

    context_texts = []
    sources = set()
    for h in hits:
        context_texts.append(h["text"])
        sources.add(h["metadata"].get("source", "unknown"))

    return {
        "context_text": "\n\n---\n\n".join(context_texts),
        "sources": list(sources),
        "html_full": _vector_store.html_full,
    }


def generate_test_cases(query: str) -> Dict[str, Any]:
    rag = retrieve_context(query, top_k=10)

    system_prompt = (
        "You are a QA expert generating test cases for a web checkout page. "
        "All reasoning MUST be strictly grounded in the provided context. "
        "Do not invent features that are not in the context. "
        "Return ONLY a JSON array of test cases, no extra text.\n\n"
        "Each test case object must have this exact structure:\n"
        "{\n"
        '  \"id\": \"TC-001\",\n'
        '  \"feature\": \"Discount Code\",\n'
        '  \"scenario\": \"Apply valid SAVE15 discount\",\n'
        '  \"steps\": [\"step 1\", \"step 2\", \"...\"],\n'
        '  \"expected_result\": \"Total is reduced by 15%\",\n'
        '  \"grounded_in\": [\"product_specs.md\"]\n'
        "}\n\n"
        "Return valid JSON ONLY. Do not include explanation, comments, markdown formatting, code fences, or text outside the JSON array. "
        "Do NOT wrap the JSON in ``` or any other characters. If you cannot follow instructions, output an empty array []."
    )

    user_prompt = f"""
User request:
{query}

Context (project documentation + HTML text):
{rag['context_text']}

Remember:
- Use only information from the context.
- Include both positive and negative test cases if applicable.
"""

    raw_output = call_llm(system_prompt=system_prompt, user_prompt=user_prompt)

    test_cases: List[TestCase] = []

    # Try to parse JSON
    try:
        parsed = json.loads(raw_output)
        if isinstance(parsed, dict):
            parsed = [parsed]
        for obj in parsed:
            tc = TestCase(
                id=obj.get("id", ""),
                feature=obj.get("feature", ""),
                scenario=obj.get("scenario", ""),
                steps=obj.get("steps", []),
                expected_result=obj.get("expected_result", ""),
                grounded_in=obj.get("grounded_in", []),
            )
            test_cases.append(tc)
    except Exception:
        # If JSON parsing fails, we just return empty list and raw text
        test_cases = []

    return {
        "raw_output": raw_output,
        "test_cases": test_cases,
    }


def generate_selenium_script_from_test_case(test_case: TestCase) -> str:
    rag = retrieve_context(
        f"{test_case.feature} - {test_case.scenario}", top_k=10
    )
    html_full = rag["html_full"]

    if not html_full:
        raise RuntimeError(
            "checkout.html was not uploaded or stored in the knowledge base."
        )

    system_prompt = (
        "You are a senior QA automation engineer using Selenium with Python. "
        "Generate a complete, runnable Selenium Python script for the given test case. "
        "Use ONLY selectors that match the provided checkout.html structure. "
        "Assume the HTML file is served at http://localhost:8501/static/checkout.html "
        "(or adjust URL according to the README). "
        "Use best practices: waits instead of sleeps where possible, clear structure, and comments. "
        "Output ONLY Python code, no explanation text."
    )

    # Build a JSON string for the test case manually to avoid pydantic.json() issues
    test_case_json = json.dumps(test_case.dict(), indent=2)

    # We include the full HTML so the LLM can see IDs, names, etc.
    user_prompt = f"""
Test Case (JSON):
{test_case_json}

Project Documentation + HTML-derived context:
{rag['context_text']}

Full checkout.html (full file content):
{html_full}

Requirements:
- Use Selenium with Python.
- Import everything needed, including webdriver, By, WebDriverWait, expected_conditions.
- Assume Chrome driver is available on PATH.
- Do NOT invent any elements; use IDs/names/classes that exist in the HTML.
- At the end, assert the expected result described in the test case.
"""

    script = call_llm(system_prompt=system_prompt, user_prompt=user_prompt)
    return script
