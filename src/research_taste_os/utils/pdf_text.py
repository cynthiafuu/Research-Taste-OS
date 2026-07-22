from __future__ import annotations

import io
import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

try:
    import pdfplumber
except ImportError:  # pragma: no cover - optional extraction enhancer
    pdfplumber = None


MAX_CHARS = 65000
BAD_TITLE_MARKERS = ["pii:", "s0378", "microsoft word", "untitled", "default"]


def read_text_source(path_or_text: str | None) -> str:
    if not path_or_text:
        return ""
    if _is_url(path_or_text):
        return read_url(path_or_text)
    if _looks_like_direct_text(path_or_text):
        return _truncate(path_or_text)
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
    pypdf_pages = _extract_pypdf_pages(content)
    plumber_pages = _extract_pdfplumber_pages(content)
    page_count = max(len(pypdf_pages), len(plumber_pages))
    pages = []
    for index in range(min(page_count, 40)):
        pypdf_text = pypdf_pages[index] if index < len(pypdf_pages) else ""
        plumber_text = plumber_pages[index] if index < len(plumber_pages) else ""
        best_text = _best_page_text(pypdf_text, plumber_text)
        if best_text:
            pages.append(f"[Page {index + 1}]\n{best_text}")
    text = "\n\n".join(part.strip() for part in pages if part.strip())
    if not text:
        raise SystemExit("Could not extract text from this PDF. Try another PDF URL or save OCR text as .txt/.md.")
    formula_candidates = _formula_candidates(text)
    if formula_candidates:
        text += "\n\n[Formula Candidates]\n" + "\n".join(f"- {line}" for line in formula_candidates)
    return text


def _extract_pypdf_pages(content: bytes) -> list[str]:
    reader = PdfReader(io.BytesIO(content))
    pages = []
    for index, page in enumerate(reader.pages):
        if index >= 40:
            break
        pages.append(page.extract_text() or "")
    return pages


def _extract_pdfplumber_pages(content: bytes) -> list[str]:
    if pdfplumber is None:
        return []
    pages = []
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for index, page in enumerate(pdf.pages):
                if index >= 40:
                    break
                text = page.extract_text(x_tolerance=1, y_tolerance=3, layout=True) or ""
                tables = page.extract_tables() or []
                table_text = "\n".join(_table_to_text(table) for table in tables[:3])
                pages.append("\n".join(part for part in [text, table_text] if part.strip()))
    except Exception:
        return []
    return pages


def _best_page_text(pypdf_text: str, plumber_text: str) -> str:
    pypdf_text = pypdf_text.strip()
    plumber_text = plumber_text.strip()
    if not plumber_text:
        return pypdf_text
    if not pypdf_text:
        return plumber_text
    if _formula_signal(plumber_text) >= _formula_signal(pypdf_text):
        return plumber_text if len(plumber_text) >= len(pypdf_text) * 0.6 else pypdf_text
    return pypdf_text if len(pypdf_text) >= len(plumber_text) * 0.6 else plumber_text


def _table_to_text(table: list[list[str | None]]) -> str:
    rows = []
    for row in table:
        cells = [(cell or "").strip() for cell in row]
        if any(cells):
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def _formula_candidates(text: str) -> list[str]:
    candidates = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if len(line) < 12 or len(line) > 240:
            continue
        if _formula_signal(line) < 2:
            continue
        lower = line.lower()
        if any(skip in lower for skip in ["copyright", "http", "www.", "email", "appendix table"]):
            continue
        candidates.append(line)
    return _dedupe_preserve_order(candidates)[:12]


def _formula_signal(text: str) -> int:
    signal = 0
    if "=" in text or " = " in text:
        signal += 2
    if re.search(r"\b(reg|model|equation|estimate|where|dependent variable)\b", text, re.IGNORECASE):
        signal += 1
    if re.search(r"\b(beta|alpha|gamma|delta|theta|lambda|coefficient|subscript)\b|[βγαδθλ]", text, re.IGNORECASE):
        signal += 1
    if re.search(r"\b(i,t|it|j,t|firm|year|quarter)\b|[_{}]", text, re.IGNORECASE):
        signal += 1
    if re.search(r"[+\-*/×÷]", text):
        signal += 1
    return signal


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen = set()
    output = []
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(value)
    return output


def infer_pdf_metadata(path_or_url: str) -> dict[str, str | int | None]:
    if _is_url(path_or_url):
        filename = Path(urlparse(path_or_url).path).stem
        try:
            response = requests.get(
                path_or_url,
                headers={"User-Agent": "ResearchTasteOS/0.1"},
                timeout=60,
                allow_redirects=True,
            )
            response.raise_for_status()
            reader = PdfReader(io.BytesIO(response.content))
            first_text = reader.pages[0].extract_text() if reader.pages else ""
            metadata_title = _metadata_title(reader)
            page_title = _title_from_first_page(first_text)
            title = _best_title(metadata_title, page_title, filename)
            year = _year_from_text(f"{filename}\n{first_text}")
            return {
                "title": title,
                "authors": _authors_from_first_page(first_text, title),
                "abstract": _abstract_from_text(first_text),
                "year": year,
                "source": response.url,
            }
        except Exception:
            return {"title": _title_from_filename(filename), "authors": "", "abstract": "", "year": _year_from_text(filename), "source": path_or_url}
    path = Path(path_or_url)
    filename = path.stem
    if path.exists() and path.is_file() and path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        first_text = reader.pages[0].extract_text() if reader.pages else ""
        metadata_title = _metadata_title(reader)
        page_title = _title_from_first_page(first_text)
        title = _best_title(metadata_title, page_title, filename)
        year = _year_from_text(f"{filename}\n{first_text}")
        return {
            "title": title,
            "authors": _authors_from_first_page(first_text, title),
            "abstract": _abstract_from_text(first_text),
            "year": year,
            "source": str(path),
        }
    return {"title": _title_from_filename(filename or path_or_url), "authors": "", "abstract": "", "year": _year_from_text(path_or_url), "source": path_or_url}


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


def _looks_like_direct_text(value: str) -> bool:
    if "\n" in value or "\r" in value:
        return True
    if len(value) > 500:
        return True
    return False


def _metadata_title(reader: PdfReader) -> str | None:
    metadata = reader.metadata
    if not metadata:
        return None
    title = getattr(metadata, "title", None) or metadata.get("/Title")
    if not title:
        return None
    clean = str(title).strip()
    if not clean or _bad_title(clean):
        return None
    return clean[:200]


def _title_from_first_page(text: str | None) -> str | None:
    if not text:
        return None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidates = []
    for index, line in enumerate(lines[:20]):
        if len(line) < 12 or len(line) > 180:
            continue
        lower = line.lower()
        if any(skip in lower for skip in ["abstract", "introduction", "journal", "ssrn", "working paper", "received", "accepted"]):
            continue
        if _bad_title(line):
            continue
        if re.fullmatch(r"[\d\s.,;:()/-]+", line):
            continue
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if next_line and _looks_like_title_continuation(next_line):
            line = f"{line} {next_line}"
        candidates.append(line)
    return candidates[0] if candidates else None


def _best_title(metadata_title: str | None, page_title: str | None, filename: str) -> str:
    for candidate in [page_title, metadata_title, _title_from_filename(filename)]:
        if candidate and not _bad_title(candidate):
            return candidate
    return _title_from_filename(filename)


def _bad_title(value: str) -> bool:
    lower = value.lower().strip()
    return any(marker in lower for marker in BAD_TITLE_MARKERS)


def _authors_from_first_page(text: str | None, title: str | None) -> str:
    if not text:
        return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    start = _author_start_index(lines, title)
    candidates = []
    for line in lines[start : start + 6]:
        lower = line.lower()
        if _looks_like_title_continuation(line):
            continue
        if any(stop in lower for stop in ["abstract", "received", "accepted", "journal", "keywords", "jel"]):
            break
        if "@" in line or any(ch.isdigit() for ch in line) or "university" in lower or "department" in lower:
            continue
        if len(line) < 4 or len(line) > 180:
            continue
        candidates.append(line.replace("*", "").strip())
    return "; ".join(candidates[:3])


def _looks_like_title_continuation(line: str) -> bool:
    lower = line.strip().lower()
    return lower.startswith(("to ", "and ", "of ", "for ", "in ", "on ", "with ", "without "))


def _author_start_index(lines: list[str], title: str | None) -> int:
    if not title:
        return 1
    title_words = set(re.findall(r"[a-z]+", title.lower()))
    best_index = 0
    best_score = 0
    for index, line in enumerate(lines[:15]):
        words = set(re.findall(r"[a-z]+", line.lower()))
        score = len(title_words & words)
        if score > best_score:
            best_score = score
            best_index = index
    return min(best_index + 2, len(lines))


def _abstract_from_text(text: str | None) -> str:
    if not text:
        return ""
    normalized = re.sub(r"\s+", " ", text)
    match = re.search(r"\bAbstract\b[:\s]*(.*?)(?:\bJEL\b|\bKeywords\b|\b1\.\s+Introduction\b|\bIntroduction\b)", normalized, re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).strip()[:1800]


def _title_from_filename(filename: str) -> str:
    cleaned = re.sub(r"[_-]+", " ", filename)
    cleaned = re.sub(r"\b(19|20)\d{2}\b", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned.title() if cleaned else "Untitled Paper"


def _year_from_text(text: str | None) -> int | None:
    if not text:
        return None
    matches = re.findall(r"\b(20[0-3]\d|19[8-9]\d)\b", text)
    if not matches:
        return None
    return int(matches[-1])
