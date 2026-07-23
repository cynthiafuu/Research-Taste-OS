from __future__ import annotations

import json
import re
import time
from json import JSONDecodeError
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
        response = self._create_response(prompt, "The PDF was read and the Paper Bank row was created")
        return response.output_text.strip()

    def json(self, prompt: str) -> dict[str, Any]:
        response = self._create_response(prompt, "AI scoring/generation cannot continue")
        text = _strip_json_response(response.output_text)
        try:
            data = json.loads(text, strict=False)
            if not _contains_suspicious_control_chars(data):
                return data
        except JSONDecodeError:
            pass
        repaired = _escape_invalid_json_backslashes(_extract_json_object(text))
        try:
            return json.loads(repaired, strict=False)
        except JSONDecodeError as exc:
            raise SystemExit(f"OpenAI returned invalid JSON: {exc}") from exc

    def _create_response(self, prompt: str, failure_context: str) -> Any:
        last_error: OpenAIError | None = None
        for attempt in range(4):
            try:
                return self.client.responses.create(
                    model=self.settings.openai_model,
                    input=[
                        {"role": "system", "content": SYSTEM},
                        {"role": "user", "content": prompt},
                    ],
                )
            except RateLimitError as exc:
                raise SystemExit(
                    "OpenAI API quota/billing is not available. "
                    f"{failure_context}, but AI generation cannot continue until OPENAI_API_KEY has usable credits/billing."
                ) from exc
            except OpenAIError as exc:
                last_error = exc
                if attempt == 3:
                    break
                time.sleep(2 * (attempt + 1))
        raise SystemExit(f"OpenAI API error after retries: {last_error}") from last_error


def _strip_json_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return text
    return text[start : end + 1]


def _escape_invalid_json_backslashes(text: str) -> str:
    text = re.sub(r"\\u(?![0-9a-fA-F]{4})", r"\\\\u", text)
    text = re.sub(r"\\([bfnrt])(?=[A-Za-z])", r"\\\\\1", text)
    return re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", text)


def _contains_suspicious_control_chars(value: Any) -> bool:
    if isinstance(value, str):
        return any(char in value for char in ["\b", "\f", "\t"])
    if isinstance(value, list):
        return any(_contains_suspicious_control_chars(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_suspicious_control_chars(item) for item in value.values())
    return False
