# Research Taste OS

Notion-first MVP workflow for improving Accounting PhD research taste.

The system turns papers into structured Paper Cards, Taste Memos, idea extensions, idea scorecards, Mini Proposals, Referee Critiques, Advisor Memos, and weekly research-taste reviews.

Core loop:

```text
Paper Intake -> Paper Card -> Taste Memo -> Idea Extensions -> Idea Scoring -> Mini Proposal -> Referee Simulation -> Advisor Memo
```

## MVP Assumptions

- Notion is the main interface and database.
- Automation is manually triggered through the `research-os` CLI for reliability.
- PDF parsing is intentionally minimal: paste paper text/abstracts or pass `.txt`/`.md` files.
- The Notion API creates databases and properties, but saved Notion views may need to be created manually in the Notion UI.
- Relation properties are added after database creation because Notion needs target database IDs first.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Edit `.env`:

```bash
NOTION_API_KEY=secret_...
NOTION_PARENT_PAGE_ID=...
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```

Share the parent Notion page with your Notion integration before running setup.

## Create Notion Databases

```bash
research-os setup-notion
```

This creates:

- `Paper Bank`
- `Taste Memos`
- `Idea Bank`
- `Mini Proposals`
- `Referee Critiques`
- `Writing Bank`

The command appends the generated database IDs to `.env`. Then run:

```bash
research-os smoke-test
```

The smoke test creates one sample Paper, Taste Memo, Idea, Proposal, Critique, and Writing Bank entry.

## Daily Workflow

## No-Manual Mode

Fastest path: pass one PDF file or PDF URL. The system guesses title/year, defaults to `journal=WP` and `field=Other`, then runs the whole pipeline.

```bash
research-os run-pdf ./papers/paper.pdf
```

Tip on macOS: type `research-os run-pdf `, then drag the PDF into Terminal and press Enter.

For a PDF URL:

```bash
research-os run-pdf "https://example.com/paper.pdf"
```

For a folder of PDFs:

```bash
research-os run-folder ./papers --limit 5
```

Optional overrides are available only when the auto-detected metadata is bad:

```bash
research-os run-pdf ./papers/paper.pdf --title "Correct Paper Title" --field Disclosure
```

Advanced path: give the system one title plus a PDF URL, local PDF, or text file.

```bash
research-os run-paper \
  --title "Does Disclosure Discipline Managers?" \
  --authors "Author A; Author B" \
  --journal WP \
  --year 2026 \
  --field Disclosure \
  --url "https://example.com/paper.pdf"
```

For a local PDF:

```bash
research-os run-paper \
  --title "Paper title" \
  --journal WP \
  --year 2026 \
  --field Capital\ Markets \
  --content ./papers/paper.pdf
```

For paper notes or extracted text, use `.md` or `.txt`:

```bash
research-os run-paper \
  --title "Paper title" \
  --journal WP \
  --year 2026 \
  --field Auditing \
  --content ./papers/paper_notes.md
```

Abstract-only still works, but it is only a quick screening mode:

```bash
research-os run-paper \
  --title "Paper title" \
  --journal WP \
  --year 2026 \
  --field Disclosure \
  --abstract "Paste abstract here"
```

What it does automatically:

- Creates the Paper Bank entry.
- Generates the Paper Card.
- Creates the linked Taste Memo.
- Generates exactly 3 idea extensions.
- Scores all 3 ideas.
- If any idea is `Promote`, picks the highest score and creates a Mini Proposal.
- Runs Referee Simulation.
- Appends an Advisor Memo.

PDF support is intentionally simple: it reads extractable text from the first 40 pages. Scanned PDFs need OCR text first.

If you prefer to add papers directly inside Notion, set `Status = Inbox`, then run:

```bash
research-os process-inbox --limit 3
```

That processes up to 3 inbox papers end-to-end.

Add a paper:

```bash
research-os add-paper \
  --title "Does Disclosure Discipline Managers?" \
  --authors "Author A; Author B" \
  --journal WP \
  --year 2026 \
  --field Disclosure \
  --url "https://example.com/paper.pdf" \
  --abstract "Paste abstract here"
```

Generate a Paper Card:

```bash
research-os generate-paper-card --paper-id "NOTION_PAGE_ID" --content "Paste abstract or paper notes"
```

Create a Taste Memo:

```bash
research-os taste-memo --paper-id "NOTION_PAGE_ID"
```

Generate exactly 3 idea extensions:

```bash
research-os ideas --source-id "TASTE_MEMO_PAGE_ID" --paper-id "PAPER_PAGE_ID"
```

Score an idea:

```bash
research-os score --idea-id "IDEA_PAGE_ID"
```

Promote a strong idea:

```bash
research-os proposal --idea-id "IDEA_PAGE_ID" --target-journal-logic TAR-style
```

Simulate referees:

```bash
research-os referee --proposal-id "PROPOSAL_PAGE_ID"
```

Generate advisor memo:

```bash
research-os advisor-memo --proposal-id "PROPOSAL_PAGE_ID"
```

Weekly review:

```bash
research-os weekly-review
```

## Notion Views To Add

Create these simple views in Notion after setup:

Paper Bank:
- `Inbox`: filter `Status = Inbox`
- `Reading Queue`: filter `Status = Reading`, sort `Importance` descending
- `Processed`: filter `Status = Processed`

Taste Memos:
- `Needs Review`: filter `Status = Draft`
- `Useful Lessons`: filter `Status = Useful`, sort `Overall Taste Score` descending

Idea Bank:
- `Raw Ideas`: filter `Stage = Raw`
- `Promote/Revise`: filter `Decision is Promote or Revise`, sort `Total Score` descending
- `Archived`: filter `Stage = Archived`

Mini Proposals:
- `Drafts`: filter `Status = Draft`
- `Needs Revision`: filter `Status = Critiqued`
- `Advisor Ready`: filter `Advisor Ready = checked`

Referee Critiques:
- `Open Major Issues`: filter `Status = Open` and `Severity is Fatal or Major`
- `Addressed`: filter `Status = Addressed`

Writing Bank:
- `Reusable Lines`: filter `Reusable? = checked`, sort `Quality` descending
- `Weekly Reviews`: filter `Source contains Research Taste OS weekly review`

## Quality Gates

- No idea can be promoted without all 8 scores.
- If `Identification Credibility`, `Contribution`, or `Feasibility` is below 3, promotion is blocked.
- Taste Memos include `Why It Still Works`.
- Mini Proposals include `Main Validity Threats`.
- Advisor Memos include one specific feedback question.

## Prompt Templates

Prompt templates live in [src/research_taste_os/prompts.py](</Users/sylviafu/APP I created/research workflow-p0/src/research_taste_os/prompts.py>).

They cover:

- Paper Card extraction
- Taste Memo drafting
- Idea generation
- 8-factor idea scoring
- Mini Proposal drafting
- Referee simulation
- Advisor Memo drafting
- Weekly review

## Files

- [src/research_taste_os/schema.py](</Users/sylviafu/APP I created/research workflow-p0/src/research_taste_os/schema.py>): Notion database schemas.
- [src/research_taste_os/notion_client.py](</Users/sylviafu/APP I created/research workflow-p0/src/research_taste_os/notion_client.py>): Notion API wrapper.
- [src/research_taste_os/workflows/core.py](</Users/sylviafu/APP I created/research workflow-p0/src/research_taste_os/workflows/core.py>): workflow actions.
- [src/research_taste_os/cli.py](</Users/sylviafu/APP I created/research workflow-p0/src/research_taste_os/cli.py>): command-line entry point.

## Future Upgrades

Keep these out until the MVP is working:

- SSRN/journal/RSS import
- PDF section parsing
- Paper clustering
- Email digest
- Advisor feedback tracker
- Writing style comparison against TAR/JAR/JAE intros
- Dashboard metrics
