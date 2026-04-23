from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from src.rag_pipeline import RAGPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RAG-based customer support assistant")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("ingest", help="Load PDFs and build the ChromaDB index")

    ask_parser = subparsers.add_parser("ask", help="Ask a question from the customer support PDF")
    ask_parser.add_argument("question", type=str, help="Question text")
    ask_parser.add_argument("--debug", action="store_true", help="Show full JSON output")

    demo_parser = subparsers.add_parser("demo", help="Run ingestion and a sample question")
    demo_parser.add_argument(
        "--question",
        default="How can I track my order?",
        help="Optional demo question",
    )
    demo_parser.add_argument("--debug", action="store_true", help="Show full JSON output")

    return parser


def print_answer(result: dict) -> None:
    print("\nAnswer:")
    print(textwrap.fill(result["answer"], width=110))
    if result.get("requires_human"):
        print(f"\nEscalation reason: {result.get('escalation_reason')}")


def interactive_loop(pipeline: RAGPipeline) -> None:
    while True:
        question = input("Ask a question (or type 'exit'): ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not question:
            continue
        result = pipeline.ask(question)
        print_answer(result)
        print()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    pipeline = RAGPipeline(Path(__file__).resolve().parent)

    if args.command is None:
        interactive_loop(pipeline)
        return

    if args.command == "ingest":
        print(json.dumps(pipeline.ingest(), indent=2))
        return

    if args.command == "ask":
        result = pipeline.ask(args.question)
        print_answer(result)
        return

    if args.command == "demo":
        pipeline.ingest()
        result = pipeline.ask(args.question)
        print_answer(result)

if __name__ == "__main__":
    main()
