from __future__ import annotations

from typing import Any


FIELDS = ["Disclosure", "Capital Markets", "Auditing", "Tax", "Governance", "AI/Data", "Other"]
JOURNALS = ["TAR", "JAR", "JAE", "RAST", "CAR", "WP", "Other"]


def title() -> dict[str, Any]:
    return {"title": {}}


def text() -> dict[str, Any]:
    return {"rich_text": {}}


def number() -> dict[str, Any]:
    return {"number": {"format": "number"}}


def checkbox() -> dict[str, Any]:
    return {"checkbox": {}}


def url() -> dict[str, Any]:
    return {"url": {}}


def created_time() -> dict[str, Any]:
    return {"created_time": {}}


def select(options: list[str]) -> dict[str, Any]:
    return {"select": {"options": [{"name": name} for name in options]}}


def multi_select(options: list[str]) -> dict[str, Any]:
    return {"multi_select": {"options": [{"name": name} for name in options]}}


def relation(database_id: str) -> dict[str, Any]:
    return {"relation": {"data_source_id": database_id, "type": "single_property", "single_property": {}}}


def data_source_properties(properties: dict[str, Any]) -> dict[str, Any]:
    title_names = [name for name, definition in properties.items() if "title" in definition]
    if not title_names:
        return properties
    title_name = title_names[0]
    converted = {"Name": {"name": title_name}}
    converted.update({name: definition for name, definition in properties.items() if name != title_name})
    return converted


def formula(expression: str) -> dict[str, Any]:
    return {"formula": {"expression": expression}}


BASE_SCHEMAS: dict[str, tuple[str, dict[str, Any]]] = {
    "paper_bank": (
        "Paper Bank",
        {
            "Title": title(),
            "Authors": text(),
            "Journal": select(JOURNALS),
            "Year": number(),
            "Field": multi_select(FIELDS),
            "PDF/Link": url(),
            "Status": select(["Inbox", "Reading", "Processed", "Error", "Archived"]),
            "Importance": number(),
            "Created Date": created_time(),
        },
    ),
    "taste_memos": (
        "Taste Memos",
        {
            "Memo Title": title(),
            "Question Importance": number(),
            "Theoretical Tension": number(),
            "Setting Quality": number(),
            "Identification Quality": number(),
            "Contribution Strength": number(),
            "Writing Quality": number(),
            "Overall Taste Score": formula(
                "(prop(\"Question Importance\") + prop(\"Theoretical Tension\") + prop(\"Setting Quality\") + prop(\"Identification Quality\") + prop(\"Contribution Strength\") + prop(\"Writing Quality\")) / 6"
            ),
            "Key Lesson": text(),
            "Status": select(["Draft", "Reviewed", "Useful", "Archived"]),
        },
    ),
    "idea_bank": (
        "Idea Bank",
        {
            "Idea Title": title(),
            "Field": multi_select(FIELDS),
            "Research Question": text(),
            "Setting": text(),
            "Data Needed": text(),
            "Identification": text(),
            "Question Importance": number(),
            "Theoretical Tension": number(),
            "Setting Quality": number(),
            "Identification Credibility": number(),
            "Construct Validity": number(),
            "Mechanism Testability": number(),
            "Contribution": number(),
            "Feasibility": number(),
            "Total Score": formula(
                "prop(\"Question Importance\") + prop(\"Theoretical Tension\") + prop(\"Setting Quality\") + prop(\"Identification Credibility\") + prop(\"Construct Validity\") + prop(\"Mechanism Testability\") + prop(\"Contribution\") + prop(\"Feasibility\")"
            ),
            "Decision": select(["Promote", "Revise", "Hold", "Archive"]),
            "Stage": select(["Raw", "Scored", "Proposal", "Advisor", "Active Project", "Archived"]),
        },
    ),
    "mini_proposals": (
        "Mini Proposals",
        {
            "Proposal Title": title(),
            "Status": select(["Draft", "Critiqued", "Revised", "Sent to Advisor", "Archived"]),
            "Target Journal Logic": select(["TAR-style", "JAR-style", "JAE-style", "RAST-style", "CAR-style"]),
            "Main Validity Threat": text(),
            "Advisor Ready": checkbox(),
            "Created Date": created_time(),
        },
    ),
    "referee_bank": (
        "Referee Critiques",
        {
            "Critique Title": title(),
            "Critique Type": select(["Theory", "Identification", "Measurement", "Writing", "Advisor Feedback"]),
            "Severity": select(["Fatal", "Major", "Moderate", "Minor"]),
            "Status": select(["Open", "Addressed", "Ignored", "Archived"]),
            "Action Needed": text(),
            "Created Date": created_time(),
        },
    ),
    "writing_bank": (
        "Writing Bank",
        {
            "Entry Title": title(),
            "Type": select(["Motivation", "Gap", "Identification", "Contribution", "Hypothesis", "Transition"]),
            "Source": text(),
            "Quality": number(),
            "Reusable?": checkbox(),
            "Field": multi_select(FIELDS),
        },
    ),
}


def relation_patches(ids: dict[str, str]) -> dict[str, dict[str, Any]]:
    return {
        "paper_bank": {
            "Related Taste Memo": relation(ids["taste_memos"]),
            "Related Ideas": relation(ids["idea_bank"]),
        },
        "taste_memos": {"Paper": relation(ids["paper_bank"])},
        "idea_bank": {
            "Source Paper": relation(ids["paper_bank"]),
            "Related Proposal": relation(ids["mini_proposals"]),
        },
        "mini_proposals": {"Idea": relation(ids["idea_bank"])},
        "referee_bank": {"Proposal": relation(ids["mini_proposals"])},
    }
