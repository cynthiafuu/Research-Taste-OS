from __future__ import annotations

import re
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

from .. import prompts
from ..config import Settings, append_env_values, normalize_notion_id, require
from ..llm_client import LLMClient
from ..notion_client import (
    NotionClient,
    checkbox_prop,
    multi_select_prop,
    number_prop,
    relation_prop,
    rich_text_prop,
    select_prop,
    title_prop,
    url_prop,
)
from ..schema import BASE_SCHEMAS, data_source_properties, relation_patches
from ..utils.pdf_text import read_text_source
from ..utils.scoring import SCORE_FIELDS, decision_for_scores, total_score


def setup_notion() -> dict[str, str]:
    settings = Settings()
    parent_id = normalize_notion_id(require(settings.notion_parent_page_id, "NOTION_PARENT_PAGE_ID"))
    notion = NotionClient(settings)
    ids: dict[str, str] = {}
    for key, (title, properties) in BASE_SCHEMAS.items():
        db = notion.create_database(parent_id, title, {})
        data_source_id = notion.database_data_source_id(db["id"])
        notion.update_data_source(data_source_id, data_source_properties(properties))
        ids[key] = data_source_id
        print(f"Created {title}: {data_source_id}")
    for key, properties in relation_patches(ids).items():
        notion.update_data_source(ids[key], properties)
    append_env_values(
        {
            "PAPER_BANK_DB_ID": ids["paper_bank"],
            "TASTE_MEMOS_DB_ID": ids["taste_memos"],
            "IDEA_BANK_DB_ID": ids["idea_bank"],
            "MINI_PROPOSALS_DB_ID": ids["mini_proposals"],
            "REFEREE_BANK_DB_ID": ids["referee_bank"],
            "WRITING_BANK_DB_ID": ids["writing_bank"],
        }
    )
    return ids


def add_paper(args: Any) -> dict[str, Any]:
    settings = Settings()
    notion = NotionClient(settings)
    db_id = require(settings.paper_bank_db_id, "PAPER_BANK_DB_ID")
    page = notion.create_page(
        db_id,
        {
            "Title": title_prop(args.title),
            "Authors": rich_text_prop(args.authors),
            "Journal": select_prop(args.journal),
            "Year": number_prop(args.year),
            "Field": multi_select_prop(args.field or []),
            "PDF/Link": url_prop(args.url),
            "Status": select_prop("Inbox"),
            "Importance": number_prop(args.importance),
        },
        args.abstract and f"## Intake Notes\n{args.abstract}",
    )
    print(f"Created paper: {page['id']}")
    return page


def generate_paper_card(args: Any) -> str:
    settings = Settings()
    notion = NotionClient(settings)
    llm = LLMClient(settings)
    content = read_text_source(args.content) or notion.page_text(args.paper_id)
    markdown = llm.complete(prompts.PAPER_CARD.format(content=content))
    notion.append_markdown(args.paper_id, markdown)
    notion.update_page(args.paper_id, {"Status": select_prop("Reading")})
    print(f"Added Paper Card to paper: {args.paper_id}")
    return markdown


def generate_taste_memo(args: Any) -> dict[str, Any]:
    settings = Settings()
    notion = NotionClient(settings)
    llm = LLMClient(settings)
    db_id = require(settings.taste_memos_db_id, "TASTE_MEMOS_DB_ID")
    content = read_text_source(args.content) or notion.page_text(args.paper_id)
    markdown = llm.complete(prompts.TASTE_MEMO.format(content=content))
    scores = _taste_scores(markdown)
    paper_title = _page_title(notion.retrieve_page(args.paper_id), "Title") or "Paper"
    page = notion.create_page(
        db_id,
        {
            "Memo Title": title_prop(f"{paper_title} Taste Memo"),
            "Paper": relation_prop([args.paper_id]),
            "Question Importance": number_prop(scores.get("Question Importance", 3)),
            "Theoretical Tension": number_prop(scores.get("Theoretical Tension", 3)),
            "Setting Quality": number_prop(scores.get("Setting Quality", 3)),
            "Identification Quality": number_prop(scores.get("Identification Quality", 3)),
            "Contribution Strength": number_prop(scores.get("Contribution Strength", 3)),
            "Writing Quality": number_prop(scores.get("Writing Quality", 3)),
            "Key Lesson": rich_text_prop(_first_section_line(markdown, "What I Should Learn")),
            "Status": select_prop("Draft"),
        },
        markdown,
    )
    notion.update_page(args.paper_id, {"Related Taste Memo": relation_prop([page["id"]])})
    print(f"Created Taste Memo: {page['id']}")
    return page


def generate_ideas(args: Any) -> list[dict[str, Any]]:
    settings = Settings()
    notion = NotionClient(settings)
    llm = LLMClient(settings)
    db_id = require(settings.idea_bank_db_id, "IDEA_BANK_DB_ID")
    content = read_text_source(args.content) or notion.page_text(args.source_id)
    data = llm.json(prompts.IDEAS.format(content=content))
    ideas = data.get("ideas", [])[:3]
    while len(ideas) < 3:
        ideas.append({"title": f"Idea {len(ideas) + 1}", "body_markdown": "## Research Question\nTBD"})
    pages = []
    for idea in ideas[:3]:
        page = notion.create_page(
            db_id,
            {
                "Idea Title": title_prop(idea.get("title", "Untitled Idea")),
                "Source Paper": relation_prop([args.paper_id] if getattr(args, "paper_id", None) else []),
                "Field": multi_select_prop(idea.get("field", [])),
                "Research Question": rich_text_prop(idea.get("research_question", "")),
                "Setting": rich_text_prop(idea.get("setting", "")),
                "Data Needed": rich_text_prop(idea.get("data_needed", "")),
                "Identification": rich_text_prop(idea.get("identification", "")),
                "Stage": select_prop("Raw"),
            },
            idea.get("body_markdown", ""),
        )
        pages.append(page)
        print(f"Created idea: {page['id']}")
    return pages


def score_idea(args: Any) -> dict[str, Any]:
    settings = Settings()
    notion = NotionClient(settings)
    llm = LLMClient(settings)
    content = read_text_source(args.content) or notion.page_text(args.idea_id)
    data = llm.json(prompts.SCORE_IDEA.format(content=content))
    scores = {field: int(data.get("scores", {}).get(field, 0)) for field in SCORE_FIELDS}
    decision = decision_for_scores(scores)
    total = total_score(scores)
    explanation = data.get("explanation_markdown", "")
    body = f"""## Score Explanation
Total Score: {total}
Decision: {decision}

### Fatal Flaw
{data.get("fatal_flaw", "")}

### Best Version
{data.get("best_version", "")}

### Minimum Data Needed
{data.get("minimum_data_needed", "")}

### Main Empirical Design
{data.get("main_empirical_design", "")}

### One-Sentence Contribution
{data.get("one_sentence_contribution", "")}

{explanation}
"""
    properties = {field: number_prop(value) for field, value in scores.items()}
    properties.update({"Decision": select_prop(decision), "Stage": select_prop("Scored")})
    notion.update_page(args.idea_id, properties)
    notion.append_markdown(args.idea_id, body)
    print(f"Scored idea {args.idea_id}: {total} / {decision}")
    return {"scores": scores, "total": total, "decision": decision}


def promote_idea(args: Any) -> dict[str, Any]:
    settings = Settings()
    notion = NotionClient(settings)
    llm = LLMClient(settings)
    proposal_db_id = require(settings.mini_proposals_db_id, "MINI_PROPOSALS_DB_ID")
    idea_page = notion.retrieve_page(args.idea_id)
    props = idea_page.get("properties", {})
    scores = {field: _number_value(props.get(field)) for field in SCORE_FIELDS}
    if any(value is None for value in scores.values()):
        raise SystemExit("Idea must be scored before promotion.")
    decision = _select_value(props.get("Decision"))
    if decision != "Promote" and not args.force:
        raise SystemExit(f"Idea decision is {decision or 'unset'}, not Promote. Use --force only after manual review.")
    gate_decision = decision_for_scores({key: int(value or 0) for key, value in scores.items()})
    if gate_decision != "Promote" and not args.force:
        raise SystemExit("Hard rule blocks promotion: identification, contribution, or feasibility is below 3.")
    content = notion.page_text(args.idea_id)
    markdown = llm.complete(prompts.MINI_PROPOSAL.format(content=content))
    title = _page_title(idea_page, "Idea Title") or "Mini Proposal"
    page = notion.create_page(
        proposal_db_id,
        {
            "Proposal Title": title_prop(title),
            "Idea": relation_prop([args.idea_id]),
            "Status": select_prop("Draft"),
            "Target Journal Logic": select_prop(args.target_journal_logic),
            "Main Validity Threat": rich_text_prop(_first_section_line(markdown, "12. Main Validity Threats")),
            "Advisor Ready": checkbox_prop(False),
        },
        markdown,
    )
    notion.update_page(args.idea_id, {"Related Proposal": relation_prop([page["id"]]), "Stage": select_prop("Proposal")})
    print(f"Created Mini Proposal: {page['id']}")
    return page


def simulate_referees(args: Any) -> list[dict[str, Any]]:
    settings = Settings()
    notion = NotionClient(settings)
    llm = LLMClient(settings)
    db_id = require(settings.referee_bank_db_id, "REFEREE_BANK_DB_ID")
    content = read_text_source(args.content) or notion.page_text(args.proposal_id)
    data = llm.json(prompts.REFEREE.format(content=content))
    pages = []
    for critique in data.get("critiques", [])[:3]:
        page = notion.create_page(
            db_id,
            {
                "Critique Title": title_prop(critique.get("title", "Referee Critique")),
                "Proposal": relation_prop([args.proposal_id]),
                "Critique Type": select_prop(critique.get("type", "Theory")),
                "Severity": select_prop(critique.get("severity", "Major")),
                "Status": select_prop("Open"),
                "Action Needed": rich_text_prop(critique.get("action_needed", "")),
            },
            critique.get("body_markdown", ""),
        )
        pages.append(page)
        print(f"Created critique: {page['id']}")
    notion.update_page(args.proposal_id, {"Status": select_prop("Critiqued")})
    return pages


def generate_advisor_memo(args: Any) -> str:
    settings = Settings()
    notion = NotionClient(settings)
    llm = LLMClient(settings)
    content = read_text_source(args.content) or notion.page_text(args.proposal_id)
    markdown = llm.complete(prompts.ADVISOR_MEMO.format(content=content))
    if "Main Concern I Want Feedback On" not in markdown:
        markdown += "\n\n### Main Concern I Want Feedback On\nWhat is the single most important validity threat to resolve before investing further?"
    notion.append_markdown(args.proposal_id, markdown)
    notion.update_page(args.proposal_id, {"Status": select_prop("Sent to Advisor"), "Advisor Ready": checkbox_prop(True)})
    print(f"Added Advisor Memo to proposal: {args.proposal_id}")
    return markdown


def run_paper(args: Any) -> dict[str, Any]:
    content = (
        read_text_source(getattr(args, "content", None))
        or read_text_source(getattr(args, "url", None))
        or getattr(args, "abstract", "")
    )
    if not content:
        raise SystemExit("Give the pipeline a PDF URL, local PDF path, .txt/.md path, or abstract.")
    paper = add_paper(args)
    paper_id = paper["id"]
    generate_paper_card(SimpleNamespace(paper_id=paper_id, content=content))
    memo = generate_taste_memo(SimpleNamespace(paper_id=paper_id, content=None))
    ideas = generate_ideas(SimpleNamespace(source_id=memo["id"], paper_id=paper_id, content=None))
    scored = []
    for idea in ideas:
        result = score_idea(SimpleNamespace(idea_id=idea["id"], content=None))
        scored.append({"page": idea, **result})
    proposal = _promote_best_scored_idea(scored, getattr(args, "target_journal_logic", "TAR-style"))
    critiques = []
    advisor_memo = None
    if proposal:
        critiques = simulate_referees(SimpleNamespace(proposal_id=proposal["id"], content=None))
        advisor_memo = generate_advisor_memo(SimpleNamespace(proposal_id=proposal["id"], content=None))
        print("Auto pipeline finished through Advisor Memo.")
    else:
        print("Auto pipeline stopped after scoring because no idea met Promote rules.")
    return {
        "paper": paper,
        "memo": memo,
        "ideas": ideas,
        "scored": scored,
        "proposal": proposal,
        "critiques": critiques,
        "advisor_memo": advisor_memo,
    }


def process_inbox(args: Any) -> list[dict[str, Any]]:
    settings = Settings()
    notion = NotionClient(settings)
    paper_db = require(settings.paper_bank_db_id, "PAPER_BANK_DB_ID")
    data = notion.query_database(
        paper_db,
        {
            "page_size": args.limit,
            "filter": {"property": "Status", "select": {"equals": "Inbox"}},
        },
    )
    results = []
    for paper in data.get("results", []):
        paper_id = paper["id"]
        title = _page_title(paper, "Title") or paper_id
        print(f"Processing Inbox paper: {title} ({paper_id})")
        generate_paper_card(SimpleNamespace(paper_id=paper_id, content=None))
        memo = generate_taste_memo(SimpleNamespace(paper_id=paper_id, content=None))
        ideas = generate_ideas(SimpleNamespace(source_id=memo["id"], paper_id=paper_id, content=None))
        scored = []
        for idea in ideas:
            result = score_idea(SimpleNamespace(idea_id=idea["id"], content=None))
            scored.append({"page": idea, **result})
        proposal = _promote_best_scored_idea(scored, args.target_journal_logic)
        critiques = []
        advisor_memo = None
        if proposal:
            critiques = simulate_referees(SimpleNamespace(proposal_id=proposal["id"], content=None))
            advisor_memo = generate_advisor_memo(SimpleNamespace(proposal_id=proposal["id"], content=None))
        notion.update_page(paper_id, {"Status": select_prop("Processed")})
        results.append(
            {
                "paper": paper,
                "memo": memo,
                "ideas": ideas,
                "scored": scored,
                "proposal": proposal,
                "critiques": critiques,
                "advisor_memo": advisor_memo,
            }
        )
    if not results:
        print("No Inbox papers found.")
    return results


def weekly_review(args: Any) -> str:
    settings = Settings()
    notion = NotionClient(settings)
    llm = LLMClient(settings)
    paper_db = require(settings.paper_bank_db_id, "PAPER_BANK_DB_ID")
    writing_db = require(settings.writing_bank_db_id, "WRITING_BANK_DB_ID")
    idea_db = require(settings.idea_bank_db_id, "IDEA_BANK_DB_ID")
    proposal_db = require(settings.mini_proposals_db_id, "MINI_PROPOSALS_DB_ID")
    records = {
        "papers": notion.query_database(paper_db, {"page_size": 10}).get("results", []),
        "ideas": notion.query_database(idea_db, {"page_size": 10}).get("results", []),
        "proposals": notion.query_database(proposal_db, {"page_size": 10}).get("results", []),
    }
    markdown = llm.complete(prompts.WEEKLY_REVIEW.format(content=str(records)))
    page = notion.create_page(
        writing_db,
        {
            "Entry Title": title_prop(f"Weekly Research Taste Review - {datetime.now(timezone.utc).date()}"),
            "Type": select_prop("Transition"),
            "Source": rich_text_prop("Research Taste OS weekly review"),
            "Quality": number_prop(3),
            "Reusable?": checkbox_prop(False),
            "Field": multi_select_prop([]),
        },
        markdown,
    )
    print(f"Created weekly review in Writing Bank: {page['id']}")
    return markdown


def _promote_best_scored_idea(scored: list[dict[str, Any]], target_journal_logic: str) -> dict[str, Any] | None:
    promotable = [item for item in scored if item.get("decision") == "Promote"]
    if not promotable:
        return None
    best = max(promotable, key=lambda item: int(item.get("total", 0)))
    return promote_idea(
        SimpleNamespace(
            idea_id=best["page"]["id"],
            target_journal_logic=target_journal_logic,
            force=False,
        )
    )


def smoke_test(args: Any) -> None:
    settings = Settings()
    notion = NotionClient(settings)
    db_ids = {key: require(value, key.upper() + "_DB_ID") for key, value in settings.db_ids.items()}
    paper = notion.create_page(
        db_ids["paper_bank"],
        {"Title": title_prop("Sample Paper"), "Status": select_prop("Inbox"), "Importance": number_prop(3)},
        "## Paper Card\nSample card.",
    )
    memo = notion.create_page(
        db_ids["taste_memos"],
        {"Memo Title": title_prop("Sample Taste Memo"), "Paper": relation_prop([paper["id"]]), "Status": select_prop("Draft")},
        "## Why It Still Works\nSample memo.",
    )
    idea = notion.create_page(
        db_ids["idea_bank"],
        {"Idea Title": title_prop("Sample Idea"), "Source Paper": relation_prop([paper["id"]]), "Stage": select_prop("Raw")},
        "## Research Question\nSample idea.",
    )
    proposal = notion.create_page(
        db_ids["mini_proposals"],
        {"Proposal Title": title_prop("Sample Proposal"), "Idea": relation_prop([idea["id"]]), "Status": select_prop("Draft")},
        "## 12. Main Validity Threats\nSample threat.",
    )
    critique = notion.create_page(
        db_ids["referee_bank"],
        {
            "Critique Title": title_prop("Sample Critique"),
            "Proposal": relation_prop([proposal["id"]]),
            "Critique Type": select_prop("Theory"),
            "Severity": select_prop("Moderate"),
            "Status": select_prop("Open"),
        },
        "## Main Concern\nSample critique.",
    )
    writing = notion.create_page(
        db_ids["writing_bank"],
        {"Entry Title": title_prop("Sample Writing Pattern"), "Type": select_prop("Motivation"), "Quality": number_prop(3)},
        "## Original Sentence / Pattern\nSample.",
    )
    print("Smoke test pages created:")
    for page in [paper, memo, idea, proposal, critique, writing]:
        print(page["id"])


def _page_title(page: dict[str, Any], property_name: str) -> str:
    parts = page.get("properties", {}).get(property_name, {}).get("title", [])
    return "".join(part.get("plain_text", "") for part in parts)


def _select_value(prop: dict[str, Any] | None) -> str | None:
    select = (prop or {}).get("select")
    return select.get("name") if select else None


def _number_value(prop: dict[str, Any] | None) -> int | float | None:
    return (prop or {}).get("number")


def _taste_scores(markdown: str) -> dict[str, int]:
    names = [
        "Question Importance",
        "Theoretical Tension",
        "Setting Quality",
        "Identification Quality",
        "Contribution Strength",
        "Writing Quality",
    ]
    scores: dict[str, int] = {}
    for name in names:
        pattern = re.compile(name.replace(" ", r"\s*") + r"[^0-9]*([1-5])", re.IGNORECASE)
        match = pattern.search(markdown)
        if match:
            scores[name] = int(match.group(1))
    return scores


def _first_section_line(markdown: str, section: str) -> str:
    pattern = re.compile(rf"#+\s*{re.escape(section)}\s*\n+(.+?)(?:\n#+|\Z)", re.IGNORECASE | re.DOTALL)
    match = pattern.search(markdown)
    if not match:
        return ""
    for line in match.group(1).splitlines():
        line = line.strip(" -*")
        if line:
            return line[:2000]
    return ""
