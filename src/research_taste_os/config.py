from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(override=True)


@dataclass(frozen=True)
class Settings:
    notion_api_key: str | None = os.getenv("NOTION_API_KEY")
    notion_parent_page_id: str | None = os.getenv("NOTION_PARENT_PAGE_ID")
    notion_version: str = os.getenv("NOTION_VERSION", "2026-03-11")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    paper_bank_db_id: str | None = os.getenv("PAPER_BANK_DB_ID")
    taste_memos_db_id: str | None = os.getenv("TASTE_MEMOS_DB_ID")
    idea_bank_db_id: str | None = os.getenv("IDEA_BANK_DB_ID")
    mini_proposals_db_id: str | None = os.getenv("MINI_PROPOSALS_DB_ID")
    referee_bank_db_id: str | None = os.getenv("REFEREE_BANK_DB_ID")
    writing_bank_db_id: str | None = os.getenv("WRITING_BANK_DB_ID")

    @property
    def db_ids(self) -> dict[str, str | None]:
        return {
            "paper_bank": self.paper_bank_db_id,
            "taste_memos": self.taste_memos_db_id,
            "idea_bank": self.idea_bank_db_id,
            "mini_proposals": self.mini_proposals_db_id,
            "referee_bank": self.referee_bank_db_id,
            "writing_bank": self.writing_bank_db_id,
        }


def require(value: str | None, name: str) -> str:
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def normalize_notion_id(value: str) -> str:
    value = value.strip().strip('"').strip("'")
    if "=" in value:
        value = value.rsplit("=", 1)[-1].strip()
    matches = re.findall(r"[0-9a-fA-F]{32}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", value)
    if matches:
        value = matches[-1]
    compact = value.replace("-", "")
    if len(compact) == 32 and re.fullmatch(r"[0-9a-fA-F]{32}", compact):
        return f"{compact[:8]}-{compact[8:12]}-{compact[12:16]}-{compact[16:20]}-{compact[20:]}".lower()
    return value


def append_env_values(values: dict[str, str], env_path: str = ".env") -> None:
    path = Path(env_path)
    existing = path.read_text() if path.exists() else ""
    seen: set[str] = set()
    output: list[str] = []
    for line in existing.splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            output.append(line)
            continue
        key, raw_value = line.split("=", 1)
        clean_key = key.strip()
        if clean_key in values:
            output.append(f"{clean_key}={values[clean_key]}")
            seen.add(clean_key)
        else:
            output.append(line)
    for key, value in values.items():
        if key not in seen:
            output.append(f"{key}={value}")
    path.write_text("\n".join(output).rstrip() + "\n")
