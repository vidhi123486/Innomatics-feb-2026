from __future__ import annotations

import os

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpoint
from langchain_openai import ChatOpenAI


def create_llm(provider: str = "openai", model_name: str | None = None, temperature: float = 0.0):
    provider = provider.lower().strip()

    if provider == "openai":
        return ChatOpenAI(
            model=model_name or "gpt-4o-mini",
            temperature=temperature,
        )

    if provider == "huggingface":
        repo_id = model_name or os.getenv("HUGGINGFACE_REPO_ID", "mistralai/Mixtral-8x7B-Instruct-v0.1")
        return HuggingFaceEndpoint(
            repo_id=repo_id,
            temperature=temperature,
            max_new_tokens=1024,
        )

    if provider == "groq":
        return ChatGroq(
            model=model_name or "llama-3.3-70b-versatile",
            temperature=temperature,
        )

    raise ValueError("Unsupported provider. Use 'openai', 'huggingface', or 'groq'.")
