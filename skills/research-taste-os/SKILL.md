---
name: research-taste-os
description: Notion-first workflow for processing accounting PhD research papers into the user's Research Taste OS. Use when the user wants to run paper PDFs through `research-os`, batch-process literature folders, refresh or clean the Notion Research Taste OS dashboard, maintain the Paper Bank single-page workflow, or troubleshoot Notion/OpenAI output quality for research taste notes.
---

# Research Taste OS

Use this skill to operate the user's Notion-first research taste workflow. The daily system is intentionally simple: one paper becomes one Paper Bank row, and the full analysis lives inside that paper page.

## Operating Rules

- Write all Notion-facing output in English.
- Treat `Paper Bank` as the main interface. Do not push the user back into the old multi-database workflow unless they explicitly ask for relational mode.
- Do not run `research-os setup-notion` unless the user explicitly wants a new Notion workspace; it creates another database set.
- Prefer `.venv/bin/research-os` from the project root so the correct editable install and `.env` are used.
- Never print `.env` secrets or API keys.

## Project Location

Default local project:

```bash
/Users/sylviafu/APP I created/research workflow-p0
```

If that path is missing, search for a repo containing `pyproject.toml`, `src/research_taste_os/cli.py`, and `README.md`.

## Core Commands

From the project root:

```bash
.venv/bin/research-os run-pdf "/full/path/to/paper.pdf"
.venv/bin/research-os run-folder "/full/path/to/Literature" --limit 3
.venv/bin/research-os ux-v2
```

Use `run-pdf` for one PDF, `run-folder` for a batch, and `ux-v2` to rebuild the simplified Notion dashboard and backfill missing `My Judgment` sections.

## Workflow Shape

The current recommended flow is:

```text
PDF -> Paper Bank row -> Paper Card -> Taste Memo -> Idea Extensions -> Scorecards -> My Judgment
```

If an idea meets the Promote rule, the paper page may also include Mini Proposal, Referee Simulation, and Advisor Memo sections.

## When Working On The Code

Read `references/notion-workflow.md` for command details, Notion UX expectations, and common troubleshooting notes before changing workflow behavior.
