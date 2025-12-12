from __future__ import annotations

import os
from typing import List, Dict, Any

from openai import OpenAI


class OpenAILLMClient:
    """Thin wrapper around OpenAI Chat Completions.

    This is intentionally minimal: it exposes a single `chat` method so that
    later we can swap implementations (e.g. Ollama) without changing pipelines.
    """

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """Call the OpenAI chat completion API and return the assistant message text.

        Parameters
        ----------
        messages: list of {"role": ..., "content": ...}
            Standard OpenAI-style chat messages.
        kwargs: any
            Extra keyword arguments passed through to `client.chat.completions.create`.
        """
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            **kwargs,
        )
        # Simple API: just return the first choice content as a string.
        return response.choices[0].message.content or ""
