from __future__ import annotations

from typing import Any

import requests

from .config import Settings, require
from .utils.notion_blocks import markdown_to_blocks


class NotionClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {require(self.settings.notion_api_key, 'NOTION_API_KEY')}",
            "Notion-Version": self.settings.notion_version,
            "Content-Type": "application/json",
        }

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers=self.headers,
            json=payload,
            timeout=60,
        )
        if response.status_code >= 400:
            raise SystemExit(f"Notion API error {response.status_code}: {response.text}")
        return response.json()

    def create_database(self, parent_page_id: str, title: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request(
            "POST",
            "/databases",
            {
                "parent": {"type": "page_id", "page_id": parent_page_id},
                "title": [{"type": "text", "text": {"content": title}}],
                "properties": properties,
            },
        )

    def update_database(self, database_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request("PATCH", f"/databases/{database_id}", {"properties": properties})

    def create_page(
        self,
        database_id: str,
        properties: dict[str, Any],
        markdown: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "parent": {"database_id": database_id},
            "properties": properties,
        }
        if markdown:
            payload["children"] = markdown_to_blocks(markdown)[:100]
        return self.request("POST", "/pages", payload)

    def update_page(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request("PATCH", f"/pages/{page_id}", {"properties": properties})

    def append_markdown(self, page_id: str, markdown: str) -> dict[str, Any]:
        blocks = markdown_to_blocks(markdown)
        result: dict[str, Any] = {}
        for offset in range(0, len(blocks), 100):
            result = self.request(
                "PATCH",
                f"/blocks/{page_id}/children",
                {"children": blocks[offset : offset + 100]},
            )
        return result

    def retrieve_page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/pages/{page_id}")

    def retrieve_block_children(self, block_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        cursor = None
        while True:
            suffix = f"?start_cursor={cursor}" if cursor else ""
            data = self.request("GET", f"/blocks/{block_id}/children{suffix}")
            results.extend(data.get("results", []))
            if not data.get("has_more"):
                return results
            cursor = data.get("next_cursor")

    def query_database(self, database_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("POST", f"/databases/{database_id}/query", payload or {})

    def page_text(self, page_id: str) -> str:
        blocks = self.retrieve_block_children(page_id)
        lines: list[str] = []
        for block in blocks:
            block_type = block.get("type")
            data = block.get(block_type, {})
            text = "".join(part.get("plain_text", "") for part in data.get("rich_text", []))
            if text:
                if block_type and block_type.startswith("heading_"):
                    level = block_type[-1]
                    lines.append(f"{'#' * int(level)} {text}")
                else:
                    lines.append(text)
        return "\n".join(lines)


def title_prop(value: str) -> dict[str, Any]:
    return {"title": [{"type": "text", "text": {"content": value[:2000]}}]}


def rich_text_prop(value: str | None) -> dict[str, Any]:
    return {"rich_text": [{"type": "text", "text": {"content": (value or "")[:2000]}}]}


def select_prop(value: str | None) -> dict[str, Any]:
    return {"select": {"name": value} if value else None}


def multi_select_prop(values: list[str] | None) -> dict[str, Any]:
    return {"multi_select": [{"name": value} for value in (values or [])]}


def number_prop(value: int | float | None) -> dict[str, Any]:
    return {"number": value}


def url_prop(value: str | None) -> dict[str, Any]:
    return {"url": value}


def checkbox_prop(value: bool) -> dict[str, Any]:
    return {"checkbox": value}


def relation_prop(page_ids: list[str] | None) -> dict[str, Any]:
    return {"relation": [{"id": page_id} for page_id in (page_ids or [])]}
