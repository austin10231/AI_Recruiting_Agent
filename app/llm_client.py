"""LLM client with real-call path and local mock fallback.

Design goals:
- Keep step code simple and explicit
- Support real OpenAI calls when API key is configured
- Keep `python main.py` runnable without API key (mock mode)
"""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI


class LLMClient:
    """Thin abstraction around model calls and JSON parsing."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
        self.mock_mode = not bool(self.api_key)
        self._client = OpenAI(api_key=self.api_key) if not self.mock_mode else None

    def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate plain text from model (or return marker in mock mode)."""
        if self.mock_mode:
            return "MOCK_MODE_RESPONSE"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
        )
        content = resp.choices[0].message.content
        return content.strip() if content else ""

    def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        fallback: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate JSON and parse to Python dict.

        In mock mode, returns `fallback` if provided, otherwise {}.
        """
        if self.mock_mode:
            return fallback.copy() if fallback is not None else {}

        text = self.generate_text(prompt=prompt, system_prompt=system_prompt)
        try:
            parsed = self._extract_json_object(text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

        if fallback is not None:
            return fallback.copy()
        raise ValueError("Model response was not valid JSON object.")

    @staticmethod
    def _extract_json_object(text: str) -> Any:
        """Parse JSON object, with simple brace-based fallback extraction."""
        # Direct parse first.
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Best-effort: extract the first {...} block.
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in model response.")

        return json.loads(text[start : end + 1])
