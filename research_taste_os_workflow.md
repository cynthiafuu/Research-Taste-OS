# Research Taste OS — Notion + AI Workflow Spec

## 0. Goal
Build a lightweight Notion-based workflow that helps an Accounting PhD student improve research taste and turn paper reading into publishable research ideas.

Core loop:

```text
Paper → Taste Memo → Idea Extraction → Idea Scoring → Mini Proposal → Referee Simulation → Advisor Memo
```

Design principles:

1. Keep manual work minimal.
2. Store everything in Notion.
3. AI handles extraction, summarization, scoring drafts, and critique.
4. Human only decides: save, revise, archive, or pitch.
5. Every output should be short, structured, and reusable.

---

## 1. MVP Scope
Build the simplest useful version first.

### MVP must support

1. Add a paper manually by title, PDF/link, journal, year, and topic.
2. Generate a structured Paper Card.
3. Generate a Taste Memo.
4. Generate 3 research idea extensions from the paper.
5. Score each idea using an 8-factor rubric.
6. Promote high-score ideas to Mini Proposal.
7. Generate a Referee Simulation.
8. Generate a 1-page Advisor Memo.

### MVP does not need

1. Fancy dashboard UI.
2. Full paper crawler.
3. Automatic PDF parsing perfection.
4. Multi-user collaboration.
5. Citation manager integration.
6. Complex charts.

---

## 2. Notion Database Structure
Create 6 Notion databases.

### Database 1: `Paper Bank`
Purpose: store papers and basic metadata.

Properties:

| Property | Type | Notes |
|---|---|---|
| Title | Title | Paper title |
| Authors | Text | Author names |
| Journal | Select | TAR, JAR, JAE, RAST, CAR, WP, Other |
| Year | Number | Publication or working paper year |
| Field | Multi-select | Disclosure, Capital Markets, Auditing, Tax, Governance, AI/Data, Other |
| PDF/Link | URL/File | Paper file or URL |
| Status | Select | Inbox, Reading, Processed, Archived |
| Importance | Number | 1–5 |
| Created Date | Created time | Auto |
| Related Taste Memo | Relation | Link to Taste Memo |
| Related Ideas | Relation | Link to Idea Bank |

---

### Database 2: `Taste Memos`
Purpose: store PhD-level research taste memos.

Properties:

| Property | Type | Notes |
|---|---|---|
| Memo Title | Title | Usually paper title + “Taste Memo” |
| Paper | Relation | Link to Paper Bank |
| Question Importance | Number | 1–5 |
| Theoretical Tension | Number | 1–5 |
| Setting Quality | Number | 1–5 |
| Identification Quality | Number | 1–5 |
| Contribution Strength | Number | 1–5 |
| Writing Quality | Number | 1–5 |
| Overall Taste Score | Formula | Average of the six scores |
| Key Lesson | Text | One-sentence lesson |
| Status | Select | Draft, Reviewed, Useful, Archived |

Page body template:

```markdown
## One-Sentence Contribution

## Research Question

## Why This Question Matters

## Theoretical Tension

## Institutional Setting

## Data and Sample

## Identification Strategy

## Empirical Design

## Main Findings

## Strongest Part

## Weakest Part

## Likely Referee Concerns

## Why It Still Works

## What I Should Learn
```

---

### Database 3: `Idea Bank`
Purpose: store research ideas generated from papers or real-world settings.

Properties:

| Property | Type | Notes |
|---|---|---|
| Idea Title | Title | Short descriptive title |
| Source Paper | Relation | Link to Paper Bank, optional |
| Field | Multi-select | Disclosure, Capital Markets, Auditing, Tax, Governance, AI/Data |
| Research Question | Text | One-sentence question |
| Setting | Text | Institutional/event setting |
| Data Needed | Text | Key datasets |
| Identification | Text | DID/event study/IV/RD/panel/etc. |
| Question Importance | Number | 1–5 |
| Theoretical Tension | Number | 1–5 |
| Setting Quality | Number | 1–5 |
| Identification Credibility | Number | 1–5 |
| Construct Validity | Number | 1–5 |
| Mechanism Testability | Number | 1–5 |
| Contribution | Number | 1–5 |
| Feasibility | Number | 1–5 |
| Total Score | Formula | Sum of 8 scores |
| Decision | Select | Promote, Revise, Hold, Archive |
| Stage | Select | Raw, Scored, Proposal, Advisor, Active Project, Archived |
| Related Proposal | Relation | Link to Mini Proposals |

Decision rule:

| Total Score | Decision |
|---|---|
| 34–40 | Promote |
| 28–33 | Revise |
| 22–27 | Hold |
| <22 | Archive |

Hard rule:

```text
If Identification Credibility < 3 OR Contribution < 3 OR Feasibility < 3, do not promote.
```

---

### Database 4: `Mini Proposals`
Purpose: turn good ideas into 1–2 page proposal drafts.

Properties:

| Property | Type | Notes |
|---|---|---|
| Proposal Title | Title | Clear research title |
| Idea | Relation | Link to Idea Bank |
| Status | Select | Draft, Critiqued, Revised, Sent to Advisor, Archived |
| Target Journal Logic | Select | TAR-style, JAR-style, JAE-style, RAST-style, CAR-style |
| Main Validity Threat | Text | Biggest weakness |
| Advisor Ready | Checkbox | True when concise enough to send |
| Created Date | Created time | Auto |

Page body template:

```markdown
## 1. Research Question

## 2. Motivation

## 3. Theoretical Tension

## 4. Institutional Setting

## 5. Hypotheses

## 6. Data and Sample

## 7. Identification Strategy

## 8. Main Empirical Design

## 9. Mechanism Tests

## 10. Robustness Tests

## 11. Expected Contribution

## 12. Main Validity Threats

## 13. Feasibility Checklist
```

---

### Database 5: `Referee Bank`
Purpose: store simulated and real critique.

Properties:

| Property | Type | Notes |
|---|---|---|
| Critique Title | Title | Proposal + critique type |
| Proposal | Relation | Link to Mini Proposals |
| Critique Type | Select | Theory, Identification, Measurement, Writing, Advisor Feedback |
| Severity | Select | Fatal, Major, Moderate, Minor |
| Status | Select | Open, Addressed, Ignored, Archived |
| Action Needed | Text | Concrete revision action |
| Created Date | Created time | Auto |

Page body template:

```markdown
## Main Concern

## Why It Matters

## Is It Fatal?

## Evidence Needed

## Revision Plan
```

---

### Database 6: `Writing Bank`
Purpose: store reusable academic writing patterns.

Properties:

| Property | Type | Notes |
|---|---|---|
| Entry Title | Title | Short label |
| Type | Select | Motivation, Gap, Identification, Contribution, Hypothesis, Transition |
| Source | Text | Paper/source if any |
| Quality | Number | 1–5 |
| Reusable? | Checkbox | True/false |
| Field | Multi-select | Disclosure, Capital Markets, Auditing, Tax, Governance, AI/Data |

Page body template:

```markdown
## Original Sentence / Pattern

## Why It Works

## Reusable Template

## My Version
```

---

## 3. Workflow Steps

### Step 1: Add Paper
Trigger: user manually creates a new page in `Paper Bank` with Status = `Inbox`.

Automation:

1. Detect new paper.
2. Extract title, authors, year, journal, abstract if available.
3. Create initial Paper Card in the page body.
4. Set Status = `Reading`.

AI output format:

```markdown
## Paper Card

### One-Sentence Summary

### Research Question

### Setting

### Data

### Method

### Main Finding

### Initial Reason to Read
```

---

### Step 2: Generate Taste Memo
Trigger: user changes Paper Bank Status to `Processed` OR clicks/manual command `Generate Taste Memo`.

Automation:

1. Read paper content or Paper Card.
2. Create a linked page in `Taste Memos`.
3. Fill memo template.
4. Assign preliminary 1–5 scores.
5. Add one `Key Lesson`.

Human action:

```text
Review the memo and adjust scores manually.
```

---

### Step 3: Generate Idea Extensions
Trigger: Taste Memo Status = `Reviewed` or manual command `Generate Ideas`.

Automation:

1. Generate exactly 3 extensions.
2. Each extension must include research question, setting, data, ID strategy, contribution, and risk.
3. Create 3 linked pages in `Idea Bank` with Stage = `Raw`.

Each idea page body:

```markdown
## Research Question

## Why It Matters

## Theoretical Tension

## Setting

## Data Needed

## Identification Strategy

## Main Test

## Mechanism Tests

## Expected Contribution

## Biggest Risk
```

---

### Step 4: Score Ideas
Trigger: Idea Stage = `Raw` OR manual command `Score Idea`.

Automation:

1. Score the idea on 8 dimensions.
2. Compute Total Score.
3. Apply decision rule.
4. Write a short explanation.
5. Update Stage = `Scored`.

Human action:

```text
Only review ideas with Decision = Promote or Revise.
Archive the rest.
```

---

### Step 5: Promote to Mini Proposal
Trigger: Idea Decision = `Promote`.

Automation:

1. Create linked page in `Mini Proposals`.
2. Fill 1–2 page proposal template.
3. Set proposal Status = `Draft`.
4. Set Idea Stage = `Proposal`.

Human action:

```text
Read the proposal and decide whether the idea is actually worth discussing with advisor.
```

---

### Step 6: Referee Simulation
Trigger: Proposal Status = `Draft` OR manual command `Simulate Referees`.

Automation:

1. Generate 3 critiques:
   - Referee 1: theory and contribution.
   - Referee 2: identification and empirical design.
   - Referee 3: measurement and alternative explanations.
2. Store each critique in `Referee Bank`.
3. Update proposal Status = `Critiqued`.

Human action:

```text
Mark each critique as Fatal, Major, Moderate, or Minor.
```

---

### Step 7: Generate Advisor Memo
Trigger: Proposal Status = `Revised` and Advisor Ready = checked.

Automation:

1. Generate a one-page advisor-facing memo.
2. Keep it concise and professional.
3. Add it to the proposal page body.

Advisor memo format:

```markdown
## Advisor Memo

### Working Title

### Research Question

### Core Motivation

### Identification Idea

### Data Plan

### Expected Contribution

### Main Concern I Want Feedback On
```

---

## 4. Automation Commands
Use simple slash-style commands in the local app or CLI.

```text
/add-paper
/generate-paper-card
/generate-taste-memo
/generate-ideas
/score-idea
/promote-idea
/simulate-referees
/generate-advisor-memo
/weekly-review
```

Minimum CLI examples:

```bash
research-os add-paper --title "..." --url "..."
research-os taste-memo --paper-id "..."
research-os ideas --paper-id "..."
research-os score --idea-id "..."
research-os proposal --idea-id "..."
research-os referee --proposal-id "..."
research-os advisor-memo --proposal-id "..."
research-os weekly-review
```

---

## 5. Weekly Review Automation
Trigger: every Sunday or manual command `/weekly-review`.

Output:

```markdown
# Weekly Research Taste Review

## Papers Processed This Week

## Best Paper Lesson

## Ideas Generated

## Ideas Promoted

## Ideas Archived

## Best Mini Proposal

## Main Weakness in My Current Taste

## Next Week Plan
```

Rules:

1. Maximum 1 page.
2. No motivational filler.
3. Focus on judgment improvement.
4. Highlight only the best 1–2 ideas.

---

## 6. AI Prompt Templates

### Prompt A: Paper Card

```text
You are an Accounting PhD research assistant. Create a concise Paper Card for the paper below.

Focus on the research question, setting, data, method, findings, and why this paper may be worth reading.

Output in this exact structure:
1. One-sentence summary
2. Research question
3. Setting
4. Data
5. Method
6. Main finding
7. Initial reason to read

Paper content:
[PASTE PAPER TEXT OR ABSTRACT]
```

---

### Prompt B: Taste Memo

```text
You are an Accounting PhD advisor. Create a PhD-level Taste Memo.

Do not merely summarize. Explain why this paper is or is not top-journal quality.

Use this structure:
1. One-sentence contribution
2. Research question
3. Why the question matters
4. Theoretical tension
5. Institutional setting
6. Data and sample
7. Identification strategy
8. Empirical design
9. Main findings
10. Strongest part
11. Weakest part
12. Likely referee concerns
13. Why it still works despite limitations
14. What I should learn
15. Six taste scores from 1 to 5: question importance, theoretical tension, setting quality, identification quality, contribution strength, writing quality

Paper content:
[PASTE PAPER TEXT OR PAPER CARD]
```

---

### Prompt C: Generate Ideas

```text
Generate exactly 3 research extensions from this paper for an Accounting PhD student.

Each idea must include:
1. Idea title
2. Research question
3. Why it matters
4. Theoretical tension
5. Setting
6. Data needed
7. Identification strategy
8. Main test
9. Mechanism tests
10. Expected contribution
11. Biggest risk

Avoid vague X-affects-Y ideas. Prioritize accounting, disclosure, capital markets, auditing, governance, tax, and AI/data settings.

Source paper memo:
[PASTE TASTE MEMO]
```

---

### Prompt D: Score Idea

```text
Evaluate this research idea as a top accounting journal editor and PhD advisor.

Score 1–5 on:
1. Question importance
2. Theoretical tension
3. Setting quality
4. Identification credibility
5. Construct validity
6. Mechanism testability
7. Contribution
8. Feasibility within one year

Then output:
1. Total score
2. Decision: Promote, Revise, Hold, or Archive
3. Fatal flaw if any
4. Best version of the idea
5. Minimum data needed
6. Main empirical design
7. One-sentence contribution

Idea:
[PASTE IDEA]
```

---

### Prompt E: Mini Proposal

```text
Turn this research idea into a concise 1–2 page Accounting PhD mini proposal.

Use this structure:
1. Research question
2. Motivation
3. Theoretical tension
4. Institutional setting
5. Hypotheses
6. Data and sample
7. Identification strategy
8. Main empirical design
9. Mechanism tests
10. Robustness tests
11. Expected contribution
12. Main validity threats
13. Feasibility checklist

Keep it concise. No filler. No overclaiming.

Idea:
[PASTE SCORED IDEA]
```

---

### Prompt F: Referee Simulation

```text
Act as three referees for a top accounting journal proposal.

Referee 1 focuses on theory and contribution.
Referee 2 focuses on identification and empirical design.
Referee 3 focuses on measurement and alternative explanations.

For each referee, output:
1. Main concern
2. Why it matters
3. Is it fatal?
4. Evidence needed
5. Revision plan

End with an editor-style recommendation: promising, revise heavily, or archive.

Proposal:
[PASTE MINI PROPOSAL]
```

---

### Prompt G: Advisor Memo

```text
Create a concise advisor-facing memo from this proposal.

Tone: professional, confident, not overly deferential.
Length: maximum one page.

Use this structure:
1. Working title
2. Research question
3. Core motivation
4. Identification idea
5. Data plan
6. Expected contribution
7. Main concern I want feedback on

Proposal:
[PASTE REVISED PROPOSAL]
```

---

## 7. Recommended Technical Implementation

### Stack

Use the simplest stack:

```text
Python or TypeScript
Notion API
OpenAI API or local LLM wrapper
SQLite or local JSON cache
CLI first, web UI later
```

### Environment variables

```bash
NOTION_API_KEY=
NOTION_PARENT_PAGE_ID=
OPENAI_API_KEY=
PAPER_BANK_DB_ID=
TASTE_MEMOS_DB_ID=
IDEA_BANK_DB_ID=
MINI_PROPOSALS_DB_ID=
REFEREE_BANK_DB_ID=
WRITING_BANK_DB_ID=
```

### Notion API notes

1. Use Notion API version `2026-03-11`.
2. Create databases under a parent Notion page.
3. Create pages inside databases/data sources with matching property names.
4. Use templates for page body content when possible.
5. Webhooks are optional for MVP; polling is easier.
6. Prefer manual commands before real-time automation.

### Suggested folder structure

```text
research-taste-os/
  README.md
  .env.example
  requirements.txt or package.json
  src/
    config.py
    notion_client.py
    llm_client.py
    prompts.py
    workflows/
      add_paper.py
      generate_paper_card.py
      generate_taste_memo.py
      generate_ideas.py
      score_idea.py
      promote_idea.py
      simulate_referees.py
      advisor_memo.py
      weekly_review.py
    utils/
      pdf_text.py
      notion_blocks.py
      scoring.py
  tests/
```

---

## 8. Implementation Order for Codex

Build in this order.

### Phase 1: Notion setup

1. Create 6 Notion databases with schemas above.
2. Store database IDs in `.env`.
3. Add basic Notion read/write functions.
4. Test creating one page in each database.

Acceptance test:

```text
Running setup/test creates one sample Paper, Taste Memo, Idea, Proposal, Critique, and Writing Bank entry in Notion.
```

---

### Phase 2: Paper Card and Taste Memo

1. Add `/add-paper` command.
2. Add `/generate-paper-card` command.
3. Add `/generate-taste-memo` command.
4. Write outputs back to Notion page bodies.

Acceptance test:

```text
Given one paper title + abstract, the system creates a Paper Card and linked Taste Memo in Notion.
```

---

### Phase 3: Idea generation and scoring

1. Add `/generate-ideas` command.
2. Create exactly 3 linked Idea pages.
3. Add `/score-idea` command.
4. Auto-fill scores and decision.

Acceptance test:

```text
Given one Taste Memo, the system creates 3 ideas, scores them, and labels each Promote/Revise/Hold/Archive.
```

---

### Phase 4: Proposal and critique

1. Add `/promote-idea` command.
2. Add `/simulate-referees` command.
3. Store critiques in Referee Bank.

Acceptance test:

```text
Given one promoted idea, the system creates a Mini Proposal and three linked referee critiques.
```

---

### Phase 5: Advisor memo and weekly review

1. Add `/generate-advisor-memo` command.
2. Add `/weekly-review` command.
3. Generate a concise weekly summary page in Notion.

Acceptance test:

```text
The system generates one advisor memo and one weekly review page with links to relevant papers, ideas, proposals, and critiques.
```

---

## 9. Low-Difficulty User Workflow

Daily use should be this simple:

```text
1. Add paper to Paper Bank.
2. Run generate Paper Card.
3. Run generate Taste Memo.
4. Review scores manually.
5. Run generate Ideas.
6. Review only Promote/Revise ideas.
7. Promote best idea.
8. Run Referee Simulation.
9. Revise.
10. Generate Advisor Memo.
```

Weekly target:

```text
2 papers → 2 taste memos → 6 ideas → 2 scored seriously → 1 mini proposal
```

Monthly target:

```text
8 papers → 8 taste memos → 24 ideas → 4 mini proposals → 1 advisor-ready idea
```

---

## 10. Quality Rules

The system should enforce these rules:

1. No idea can be promoted without scores.
2. No idea can be promoted if Identification, Contribution, or Feasibility is below 3.
3. Every Taste Memo must include “Why It Still Works.”
4. Every Mini Proposal must include “Main Validity Threats.”
5. Every Advisor Memo must include one specific question for advisor feedback.
6. AI outputs should be concise by default.
7. User should never need to manually copy the same content twice.

---

## 11. Future Upgrades

Only after MVP works:

1. Auto-import papers from SSRN, journal RSS, Google Scholar alerts, or Semantic Scholar.
2. PDF parsing with section detection.
3. Paper clustering by topic.
4. Automatic weekly email digest.
5. Advisor feedback tracker.
6. Writing style comparison against TAR/JAR/JAE introductions.
7. Dashboard showing idea pipeline and score distribution.
8. Export advisor memo as PDF.

---

## 12. Definition of Success

The workflow succeeds if after 8 weeks it produces:

```text
16 processed papers
16 Taste Memos
40–50 candidate ideas
10–15 scored ideas
4–8 Mini Proposals
1–2 advisor-ready ideas
```

The final goal is not automation for its own sake. The goal is to build a repeatable system that trains research judgment, filters weak ideas early, and turns strong ideas into advisor-ready research proposals.
