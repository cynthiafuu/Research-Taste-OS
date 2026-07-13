from __future__ import annotations

import argparse

from .workflows import core


def main() -> None:
    parser = argparse.ArgumentParser(prog="research-os", description="Notion-first Research Taste OS MVP")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup-notion", help="Create the six Notion databases and append IDs to .env").set_defaults(
        func=core.setup_notion
    )
    sub.add_parser("smoke-test", help="Create one sample page in each database").set_defaults(func=core.smoke_test)
    sub.add_parser("polish-notion", help="Improve schemas, repair error rows, and append a readable dashboard").set_defaults(
        func=core.polish_notion
    )

    add = sub.add_parser("add-paper", help="Create a Paper Bank entry")
    add.add_argument("--title", required=True)
    add.add_argument("--authors", default="")
    add.add_argument("--journal", default="WP")
    add.add_argument("--year", type=int)
    add.add_argument("--field", action="append", default=[])
    add.add_argument("--url")
    add.add_argument("--importance", type=int, default=3)
    add.add_argument("--abstract", default="")
    add.set_defaults(func=core.add_paper)

    run = sub.add_parser("run-paper", help="One-command single-page pipeline: one Paper Bank page contains all analysis")
    run.add_argument("--title", required=True)
    run.add_argument("--authors", default="")
    run.add_argument("--journal", default="WP")
    run.add_argument("--year", type=int)
    run.add_argument("--field", action="append", default=[])
    run.add_argument("--url")
    run.add_argument("--importance", type=int, default=3)
    run.add_argument("--abstract", default="")
    run.add_argument("--content", help="Paper text, abstract, URL, or path to .pdf/.txt/.md")
    run.add_argument("--target-journal-logic", default="TAR-style")
    run.add_argument("--relational", action="store_true", help="Use the old multi-database workflow")
    run.set_defaults(func=core.run_paper)

    run_pdf = sub.add_parser("run-pdf", help="Upload-style single-page pipeline: one PDF becomes one Paper Bank page")
    run_pdf.add_argument("pdf", nargs="+", help="Local PDF path or PDF URL")
    run_pdf.add_argument("--title", help="Optional override if auto-detected title is bad")
    run_pdf.add_argument("--authors", default="")
    run_pdf.add_argument("--journal", default="WP")
    run_pdf.add_argument("--year", type=int)
    run_pdf.add_argument("--field", action="append", default=[])
    run_pdf.add_argument("--importance", type=int, default=3)
    run_pdf.add_argument("--target-journal-logic", default="TAR-style")
    run_pdf.add_argument("--relational", action="store_true", help="Use the old multi-database workflow")
    run_pdf.set_defaults(func=core.run_pdf)

    run_folder = sub.add_parser("run-folder", help="Process every PDF in a folder with minimal metadata")
    run_folder.add_argument("folder", help="Folder containing PDF files")
    run_folder.add_argument("--limit", type=int, default=5)
    run_folder.add_argument("--authors", default="")
    run_folder.add_argument("--journal", default="WP")
    run_folder.add_argument("--field", action="append", default=["Other"])
    run_folder.add_argument("--importance", type=int, default=3)
    run_folder.add_argument("--target-journal-logic", default="TAR-style")
    run_folder.set_defaults(func=core.run_folder)

    inbox = sub.add_parser("process-inbox", help="Automatically process Paper Bank pages with Status = Inbox")
    inbox.add_argument("--limit", type=int, default=3)
    inbox.add_argument("--target-journal-logic", default="TAR-style")
    inbox.set_defaults(func=core.process_inbox)

    paper_card = sub.add_parser("generate-paper-card", aliases=["paper-card"], help="Append a Paper Card to a paper")
    paper_card.add_argument("--paper-id", required=True)
    paper_card.add_argument("--content", help="Paper text, abstract, URL, or path to .pdf/.txt/.md")
    paper_card.set_defaults(func=core.generate_paper_card)

    taste = sub.add_parser("generate-taste-memo", aliases=["taste-memo"], help="Create a linked Taste Memo")
    taste.add_argument("--paper-id", required=True)
    taste.add_argument("--content", help="Paper/Card text, URL, or path to .pdf/.txt/.md")
    taste.set_defaults(func=core.generate_taste_memo)

    ideas = sub.add_parser("generate-ideas", aliases=["ideas"], help="Create exactly 3 Idea Bank entries")
    ideas.add_argument("--source-id", required=True, help="Taste Memo page ID or other source page ID")
    ideas.add_argument("--paper-id", help="Optional source Paper Bank page ID for relation")
    ideas.add_argument("--content", help="Memo text or path to .txt/.md")
    ideas.set_defaults(func=core.generate_ideas)

    score = sub.add_parser("score-idea", aliases=["score"], help="Score one idea using the 8-factor rubric")
    score.add_argument("--idea-id", required=True)
    score.add_argument("--content", help="Idea text or path to .txt/.md")
    score.set_defaults(func=core.score_idea)

    proposal = sub.add_parser("promote-idea", aliases=["proposal"], help="Promote a scored idea to Mini Proposal")
    proposal.add_argument("--idea-id", required=True)
    proposal.add_argument("--target-journal-logic", default="TAR-style")
    proposal.add_argument("--force", action="store_true", help="Allow promotion after manual review despite decision label")
    proposal.set_defaults(func=core.promote_idea)

    referee = sub.add_parser("simulate-referees", aliases=["referee"], help="Create three Referee Critiques")
    referee.add_argument("--proposal-id", required=True)
    referee.add_argument("--content", help="Proposal text or path to .txt/.md")
    referee.set_defaults(func=core.simulate_referees)

    advisor = sub.add_parser("generate-advisor-memo", aliases=["advisor-memo"], help="Append advisor memo to proposal")
    advisor.add_argument("--proposal-id", required=True)
    advisor.add_argument("--content", help="Proposal text or path to .txt/.md")
    advisor.set_defaults(func=core.generate_advisor_memo)

    sub.add_parser("weekly-review", help="Generate weekly review in Writing Bank").set_defaults(func=core.weekly_review)

    args = parser.parse_args()
    result = args.func(args) if args.command not in {"setup-notion"} else args.func()
    if isinstance(result, str):
        print(result)


if __name__ == "__main__":
    main()
