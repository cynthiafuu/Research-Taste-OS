---
name: research-taste-os
description: Turn business and social science research PDFs or literature folders into a Notion research-taste workspace with paper cards, research mechanics, taste memos, idea scorecards, proposal drafts, simulated referee reports, and advisor memos.
---

# 商科社科论文精读与开题导师

Use this skill when the user wants to deeply read business or social science research papers, build research taste, classify a literature folder, or turn papers into feasible thesis, seminar, or PhD research ideas. The daily system is intentionally simple: one paper becomes one Paper Bank row, and the full analysis lives inside that paper page.

## Marketplace Positioning

- Tabbit type: Task skill / agent workflow.
- User promise: upload one business/social science paper PDF, then receive a structured reading and topic-development page in Notion.
- Core outcome: PDF -> Paper Card -> Research Mechanics -> Taste Memo -> 3 Idea Extensions -> 8-factor Scorecards -> My Judgment. Strong ideas continue to Mini Proposal, Referee Simulation, and Advisor Memo.
- Best user: business, economics, finance, accounting, management, sociology, education, communication, public policy, and other social science students or researchers who read many papers and need sharper topic judgment.
- Differentiator: this does not only summarize a paper; it forces contribution, identification, construct validity, mechanism, feasibility, and advisor-readiness checks.

## Operating Rules

- Write all Notion-facing output in English.
- Treat `Paper Bank` as the main interface. Do not push the user back into the old multi-database workflow unless they explicitly ask for relational mode.
- Preserve the Extraction v2 contract: capture research topic, method, contribution type, key contribution, model/method summary, core variables, and data/setting when processing papers. Do not reproduce full equations unless the user explicitly asks.
- Do not run `research-os setup-notion` unless the user explicitly wants a new Notion workspace; it creates another database set.
- Prefer `.venv/bin/research-os` from the project root so the correct editable install and `.env` are used.
- Never print `.env` secrets or API keys.

## Intake Routing

- If the user gives one PDF path or URL, run `run-pdf`.
- If the user gives a folder and wants a library overview, run `classify-folder`.
- If the user gives a small folder and explicitly wants full deep reading for each paper, run `run-folder --limit N`.
- If the user points to an existing Notion paper page and wants a refresh, run `enhance-paper`.
- If the Notion dashboard is cluttered or missing sections, run `ux-v2`.
- If required Notion or OpenAI environment variables are missing, explain the missing setup briefly and do not invent credentials.

## Project Location

Default local project:

```bash
<project-root>
```

If that path is missing, search for a repo containing `pyproject.toml`, `src/research_taste_os/cli.py`, and `README.md`.

## Core Commands

From the project root:

```bash
.venv/bin/research-os run-pdf "/full/path/to/paper.pdf"
.venv/bin/research-os classify-folder "/full/path/to/Literature"
.venv/bin/research-os run-folder "/full/path/to/Literature" --limit 3
.venv/bin/research-os ux-v2
.venv/bin/research-os enhance-paper --paper-id "NOTION_PAGE_ID" --content "/full/path/to/paper.pdf"
```

Use `run-pdf` for one PDF, `classify-folder` for a recursive literature-library import, `run-folder` only for a small full-pipeline batch, `enhance-paper` to refresh Extraction v2 for an existing paper page, and `ux-v2` to rebuild the simplified Notion dashboard and backfill missing `My Judgment` sections.

## Workflow Shape

The current recommended flow is:

```text
PDF -> Paper Bank row -> Paper Card -> Research Mechanics -> Taste Memo -> Idea Extensions -> Scorecards -> My Judgment
```

If an idea meets the Promote rule, the paper page may also include Mini Proposal, Referee Simulation, and Advisor Memo sections.

## Suggested Tabbit Invocation Copy

Chinese user-facing prompt:

```text
请把这篇商科/社科论文跑一遍“商科社科论文精读与开题导师”：先建立 Paper Card，再拆研究问题、理论、设定、数据、方法、识别/论证、贡献和机制；然后生成 taste memo、3 个可延展选题、8 项评分表和给导师看的开题 memo。输出写入我的 Notion Paper Bank 页面。
```

English user-facing prompt:

```text
Process this business or social science research PDF through Research Taste OS. Create the Paper Card, Research Mechanics, Taste Memo, three idea extensions, scorecards, and advisor-ready follow-up sections in the Notion Paper Bank page.
```

## When Working On The Code

Read `references/notion-workflow.md` for command details, Notion UX expectations, and common troubleshooting notes before changing workflow behavior.
