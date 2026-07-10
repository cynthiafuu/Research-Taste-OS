from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAIError, RateLimitError

from .config import Settings, require
from .prompts import SYSTEM


class LLMClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            raise SystemExit("Missing dependency: openai. Run `pip install -e .` or `pip install -r requirements.txt`.") from exc
        self.client = OpenAI(api_key=require(self.settings.openai_api_key, "OPENAI_API_KEY"))

    def complete(self, prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model=self.settings.openai_model,
                input=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
            )
        except RateLimitError as exc:
            raise SystemExit(
                "OpenAI API quota/billing is not available. The PDF was read and the Paper Bank row was created, "
                "but AI generation cannot continue until OPENAI_API_KEY has usable credits/billing."
            ) from exc
        except OpenAIError as exc:
            raise SystemExit(f"OpenAI API error: {exc}") from exc
        return response.output_text.strip()

    def json(self, prompt: str) -> dict[str, Any]:
        try:
            response = self.client.responses.create(
                model=self.settings.openai_model,
                input=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
            )
        except RateLimitError as exc:
            raise SystemExit(
                "OpenAI API quota/billing is not available. AI scoring/generation cannot continue until "
                "OPENAI_API_KEY has usable credits/billing."
            ) from exc
        except OpenAIError as exc:
            raise SystemExit(f"OpenAI API error: {exc}") from exc
        text = response.output_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
