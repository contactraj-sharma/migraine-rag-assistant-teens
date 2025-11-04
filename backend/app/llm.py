"""Utility helpers to talk to an LLM provider."""
from __future__ import annotations

import os
from typing import List

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None  # type: ignore


DEFAULT_SYSTEM_PROMPT = (
    "You are a compassionate healthcare assistant for teenagers experiencing migraines. "
    "Use the provided context to answer the question in a supportive and factual tone. "
    "If the context is insufficient, acknowledge limitations and encourage consulting a healthcare professional."
)


class LLMClient:
    def __init__(self) -> None:
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.api_key = os.getenv("OPENAI_API_KEY")

    def generate(self, question: str, context_chunks: List[str]) -> str:
        context_block = "\n\n".join(context_chunks)
        if self.api_key and openai is not None:
            openai.api_key = self.api_key
            response = openai.ChatCompletion.create(  # type: ignore[attr-defined]
                model=self.model,
                messages=[
                    {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Context:\n{context_block}\n\nQuestion: {question}",
                    },
                ],
                temperature=0.2,
            )
            return response["choices"][0]["message"]["content"].strip()
        summary = (
            "Based on available information: "
            f"{context_block if context_chunks else 'No migraine-specific guidance was found.'}"
        )
        return summary + "\n\nAlways talk with a healthcare professional for personalized care."


def get_llm_client() -> LLMClient:
    return LLMClient()
