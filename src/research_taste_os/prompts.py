from __future__ import annotations


SYSTEM = (
    "You are a rigorous Accounting PhD research assistant. Be concise, structured, "
    "skeptical about identification and contribution, and avoid motivational filler."
)

PAPER_CARD = """Create a concise Paper Card for the paper below.

Focus on the research question, setting, data, method, findings, and why this paper may be worth reading.

Output in Markdown with this exact structure:
## Paper Card
### One-Sentence Summary
### Research Question
### Setting
### Data
### Method
### Main Finding
### Initial Reason to Read

Paper content:
{content}
"""

TASTE_MEMO = """Create a PhD-level Taste Memo.

Do not merely summarize. Explain why this paper is or is not top-journal quality.
Include preliminary 1-5 scores for question importance, theoretical tension, setting quality,
identification quality, contribution strength, and writing quality.

Output Markdown with this structure:
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
## Preliminary Scores

Paper content:
{content}
"""

IDEAS = """Generate exactly 3 research extensions from this paper for an Accounting PhD student.

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

Avoid vague X-affects-Y ideas. Prioritize accounting, disclosure, capital markets, auditing,
governance, tax, and AI/data settings.

Return strict JSON only:
{{"ideas":[{{"title":"","field":["Disclosure"],"research_question":"","setting":"","data_needed":"","identification":"","body_markdown":""}}]}}

Source paper memo:
{content}
"""

SCORE_IDEA = """Evaluate this research idea as a top accounting journal editor and PhD advisor.

Score 1-5 on:
1. Question Importance
2. Theoretical Tension
3. Setting Quality
4. Identification Credibility
5. Construct Validity
6. Mechanism Testability
7. Contribution
8. Feasibility within one year

Apply this hard rule: if Identification Credibility < 3 OR Contribution < 3 OR Feasibility < 3,
do not choose Promote.

Return strict JSON only:
{{"scores":{{"Question Importance":0,"Theoretical Tension":0,"Setting Quality":0,"Identification Credibility":0,"Construct Validity":0,"Mechanism Testability":0,"Contribution":0,"Feasibility":0}},"fatal_flaw":"","best_version":"","minimum_data_needed":"","main_empirical_design":"","one_sentence_contribution":"","explanation_markdown":""}}

Idea:
{content}
"""

MINI_PROPOSAL = """Turn this research idea into a concise 1-2 page Accounting PhD mini proposal.

Use this Markdown structure:
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

Keep it concise. No filler. No overclaiming.

Idea:
{content}
"""

REFEREE = """Act as three referees for a top accounting journal proposal.

Referee 1 focuses on theory and contribution.
Referee 2 focuses on identification and empirical design.
Referee 3 focuses on measurement and alternative explanations.

Return strict JSON only:
{{"critiques":[{{"title":"Referee 1 - Theory and Contribution","type":"Theory","severity":"Major","action_needed":"","body_markdown":"## Main Concern\\n\\n## Why It Matters\\n\\n## Is It Fatal?\\n\\n## Evidence Needed\\n\\n## Revision Plan"}}],"editor_recommendation":""}}

Proposal:
{content}
"""

ADVISOR_MEMO = """Create a concise advisor-facing memo from this proposal.

Tone: professional, confident, not overly deferential.
Length: maximum one page.

Use this Markdown structure:
## Advisor Memo
### Working Title
### Research Question
### Core Motivation
### Identification Idea
### Data Plan
### Expected Contribution
### Main Concern I Want Feedback On

Proposal:
{content}
"""

WEEKLY_REVIEW = """Create a one-page Weekly Research Taste Review from the records below.

Rules:
1. Maximum 1 page.
2. No motivational filler.
3. Focus on judgment improvement.
4. Highlight only the best 1-2 ideas.

Use this Markdown structure:
# Weekly Research Taste Review
## Papers Processed This Week
## Best Paper Lesson
## Ideas Generated
## Ideas Promoted
## Ideas Archived
## Best Mini Proposal
## Main Weakness in My Current Taste
## Next Week Plan

Records:
{content}
"""
