import os
from typing import List, Dict, Any

import openai

# Configure OpenAI via environment variable
openai.api_key = os.getenv("OPENAI_API_KEY", "")


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> str:
    """
    Thin wrapper around OpenAI ChatCompletion.
    You can replace this with any other LLM provider.
    """
    if not openai.api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Please export it before running the backend."
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    return resp.choices[0].message["content"].strip()
