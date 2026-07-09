from __future__ import annotations

import io
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader


MAX_CHARS = 65000


def read_text_source(path_or_text: str | None) -> str:
    if not path_or_text:
        return ""
    if _is_url(path_or_text):
        return read_url(path_or_text)
    path = Path(path_or_text)
    if path.exists() and path.is_file():
        if path.suffix.lower() in {".txt", ".md"}:
            return _truncate(path.read_text(errors="ignore"))
        if path.suffix.lower() == ".pdf":
            return _truncate(read_pdf_bytes(path.read_bytes()))
    return _truncate(path_or_text)


def read_url(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": "ResearchTasteOS/0.1"},
        timeout=60,
        allow_redirects=True,
    )
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").lower()
    if "pdf" in content_type or urlparse(response.url).path.lower().endswith(".pdf"):
        return _truncate(read_pdf_bytes(response.content))
    return _truncate(read_html(response.text))


def read_pdf_bytes(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    pages = []
    for index, page in enumerate(reader.pages):
        if index >= 40:
            break
        pages.append(page.extract_text() or "")
    text = "\n\n".join(part.strip() for part in pages if part.strip())
    if not text:
        raise SystemExit("Could not extract text from this PDF. Try another PDF URL or save OCR text as .txt/.md.")
    return text


def read_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    meta_parts = []
    for attr in ["description", "citation_abstract", "dc.description"]:
        tag = soup.find("meta", attrs={"name": attr})
        if tag and tag.get("content"):
            meta_parts.append(tag["content"])
    body = soup.get_text("\n", strip=True)
    return "\n\n".join(part for part in [title, *meta_parts, body] if part)


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"}


def _truncate(text: str) -> str:
    return text[:MAX_CHARS]
