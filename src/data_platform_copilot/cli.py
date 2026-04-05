from __future__ import annotations

import argparse
from pathlib import Path

from .agent import DataPlatformCopilot
from .evaluation import evaluate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Data Platform Copilot demo CLI")
    parser.add_argument(
        "--corpus-dir",
        default=str(Path("data") / "corpus"),
        help="Path to the JSON corpus directory.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    ask_parser = subparsers.add_parser("ask", help="Ask an operational troubleshooting question.")
    ask_parser.add_argument("question", help="Natural-language question to answer.")

    subparsers.add_parser("show-index", help="Show the indexed document inventory.")

    eval_parser = subparsers.add_parser("evaluate", help="Run the deterministic evaluation suite.")
    eval_parser.add_argument(
        "--eval-path",
        default=str(Path("data") / "eval" / "cases.json"),
        help="Path to evaluation cases JSON.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    corpus_dir = Path(args.corpus_dir)
    copilot = DataPlatformCopilot(corpus_dir)

    if args.command == "ask":
        answer = copilot.ask(args.question)
        print(f"Question: {answer.question}\n")
        print("Answer:")
        print(answer.answer)
        print("\nLikely root causes:")
        for item in answer.likely_root_causes:
            print(f"- {item}")
        print("\nNext steps:")
        for item in answer.next_steps:
            print(f"- {item}")
        print("\nCitations:")
        for citation in answer.citations:
            doc_type = next(
                result.chunk.doc_type for result in answer.retrieved if result.chunk.doc_id == citation
            )
            print(f"- {citation} [{doc_type}]")
        return

    if args.command == "show-index":
        print(copilot.show_index())
        return

    if args.command == "evaluate":
        print(evaluate(corpus_dir, Path(args.eval_path)))


if __name__ == "__main__":
    main()
