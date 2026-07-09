from __future__ import annotations


def rich_text(text: str) -> list[dict]:
    return [{"type": "text", "text": {"content": text[:2000]}}]


def paragraph(text: str) -> dict:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich_text(text)}}


def heading(level: int, text: str) -> dict:
    block_type = f"heading_{min(max(level, 1), 3)}"
    return {"object": "block", "type": block_type, block_type: {"rich_text": rich_text(text)}}


def bulleted(text: str) -> dict:
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rich_text(text)}}


def markdown_to_blocks(markdown: str) -> list[dict]:
    blocks: list[dict] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("### "):
            blocks.append(heading(3, line[4:]))
        elif line.startswith("## "):
            blocks.append(heading(2, line[3:]))
        elif line.startswith("# "):
            blocks.append(heading(1, line[2:]))
        elif line.startswith("- "):
            blocks.append(bulleted(line[2:]))
        else:
            blocks.append(paragraph(line))
    return blocks
