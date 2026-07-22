from __future__ import annotations


SYSTEM = (
    "You are a rigorous Accounting PhD research assistant. Be concise, structured, "
    "skeptical about identification and contribution, and avoid motivational filler. "
    "Write all outputs entirely in English."
)

PAPER_CARD = """Create a concise Paper Card for the paper below.

Focus on the research question, setting, data, method, findings, contribution, and why this paper may be worth reading.
When formulas, equations, variable definitions, or regression models are visible in the extracted text,
preserve the central model in readable plain text or LaTeX-like notation.

Output in Markdown with this exact structure:
## Paper Card
### One-Sentence Summary
### Research Question
### Setting
### Data
### Method
### Key Formula or Empirical Model
### Core Variables
### Main Finding
### Contribution
### Initial Reason to Read

Paper content:
{content}
"""

EXTRACTION_V2 = """Extract structured research mechanics from this accounting research paper.

Write entirely in English. Be conservative: if an item is not visible in the supplied text, say "Not clearly detected" rather than inventing it.
Pay special attention to formulas, equations, regression models, variable definitions, contribution claims, research topics, and empirical method.

Allowed research_topic values:
Disclosure, Market Reaction, Earnings Quality, Auditing, Tax, Governance, Debt Contracting, Analysts, Enforcement, ESG, AI/Data, Other

Allowed method values:
Archival, Difference-in-Differences, Event Study, Regression Discontinuity, Instrumental Variables, Experiment, Survey, Text Analysis, Machine Learning, Structural, Theory, Other

Allowed contribution_type values:
New Question, New Setting, New Data, New Measure, Identification, Mechanism, Theory, Method, Policy Relevance, Other

Return strict JSON only:
{{
  "research_topic": ["Other"],
  "method": ["Archival"],
  "contribution_type": ["Other"],
  "key_contribution": "",
  "formula_or_model": "",
  "core_variables": "",
  "data_setting": "",
  "identification_summary": "",
  "mechanism_summary": "",
  "classification_rationale": "",
  "body_markdown": "## Research Mechanics\\n### Topics and Methods\\n\\n### Contribution\\n\\n### Key Formula or Empirical Model\\n\\n### Core Variables\\n\\n### Data and Setting\\n\\n### Identification\\n\\n### Mechanism\\n"
}}

Paper Card:
{paper_card}

Paper content:
{content}
"""

TASTE_MEMO = """Create a PhD-level Taste Memo.

Do not merely summarize. Explain why this paper is or is not top-journal quality.
Include preliminary 1-5 scores for question importance, theoretical tension, setting quality,
identification quality, contribution strength, and writing quality.

Output Markdown with this structure:
## One-Sentence Contribution
## Contribution Type
## Research Question
## Why This Question Matters
## Theoretical Tension
## Institutional Setting
## Data and Sample
## Identification Strategy
## Empirical Design
## Key Formula or Empirical Model
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
