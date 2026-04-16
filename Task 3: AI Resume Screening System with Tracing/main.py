from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from chains.explanation_chain import build_explanation_chain
from chains.extraction_chain import build_extraction_chain
from chains.llm_factory import create_llm
from chains.scoring_chain import build_scoring_chain

BASE_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Resume Screening System with LangChain and LangSmith tracing.")
    parser.add_argument("--provider", default="openai", choices=["openai", "huggingface", "groq"], 
                        help="LLM provider to use.")
    parser.add_argument("--model", default=None, help="Optional model name override.")
    parser.add_argument(
        "--job-file",
        default="data/job_description.txt",
        help="Path to the job description text file.",
    )
    parser.add_argument(
        "--resume-dir",
        default="data/resumes",
        help="Path to the folder containing resume text files.",
    )
    parser.add_argument(
        "--output-file",
        default="outputs/results.json",
        help="Path to the JSON output file.",
    )
    return parser.parse_args()


def load_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def ensure_output_path(path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def tracing_status() -> str:
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
    project_name = os.getenv("LANGCHAIN_PROJECT", "not-set")
    if tracing_enabled:
        return f"Tracing enabled. Project: {project_name}"
    return "Tracing disabled. Set LANGCHAIN_TRACING_V2=true and LANGCHAIN_API_KEY for LangSmith."


def main() -> None:
    load_dotenv()
    args = parse_args()

    llm = create_llm(provider=args.provider, model_name=args.model, temperature=0.0)
    extraction_chain = build_extraction_chain(llm)
    explanation_chain = build_explanation_chain(llm)
    scoring_chain = build_scoring_chain()

    job_file = BASE_DIR / args.job_file
    resume_dir = BASE_DIR / args.resume_dir
    output_file = BASE_DIR / args.output_file

    job_text = load_text(job_file)
    resume_files = sorted(resume_dir.glob("*.txt"))

    if not resume_files:
        raise FileNotFoundError(f"No resume files found in {resume_dir}")

    print("AI Resume Screening System")
    print(tracing_status())
    print("-" * 72)

    job_extraction = extraction_chain.invoke(
        {"document_type": "job_description", "document_text": job_text},
        config={
            "run_name": "job_description_extraction",
            "tags": ["job-description", "extraction"],
            "metadata": {"source": str(job_file)},
        },
    )

    all_results = []

    for resume_file in resume_files:
        resume_text = load_text(resume_file)

        resume_extraction = extraction_chain.invoke(
            {"document_type": "resume", "document_text": resume_text},
            config={
                "run_name": "resume_extraction",
                "tags": ["resume", "extraction", resume_file.stem],
                "metadata": {"resume_file": str(resume_file)},
            },
        )

        score_breakdown = scoring_chain.invoke(
            {"job_extraction": job_extraction, "resume_extraction": resume_extraction},
            config={
                "tags": ["resume", "scoring", resume_file.stem],
                "metadata": {"resume_file": str(resume_file)},
            },
        )

        explanation = explanation_chain.invoke(
            {
                "job_extraction": job_extraction.model_dump_json(indent=2),
                "resume_extraction": resume_extraction.model_dump_json(indent=2),
                "score_details": json.dumps(score_breakdown.to_dict(), indent=2),
            },
            config={
                "run_name": "resume_explanation",
                "tags": ["resume", "explanation", resume_file.stem],
                "metadata": {"resume_file": str(resume_file), "fit_label": score_breakdown.fit_label},
            },
        )

        result = {
            "resume_file": resume_file.name,
            "candidate_summary": resume_extraction.summary,
            "score": score_breakdown.final_score,
            "fit_label": score_breakdown.fit_label,
            "matched_skills": score_breakdown.matched_skills,
            "missing_skills": score_breakdown.missing_skills,
            "matched_tools": score_breakdown.matched_tools,
            "missing_tools": score_breakdown.missing_tools,
            "scoring_notes": score_breakdown.notes,
            "explanation": explanation.explanation,
            "matched_points": explanation.matched_points,
            "missing_points": explanation.missing_points,
        }
        all_results.append(result)

        print(f"Resume: {resume_file.name}")
        print(f"Score: {result['score']} | Fit: {result['fit_label']}")
        print(f"Explanation: {result['explanation']}")
        print("-" * 72)

    output_path = ensure_output_path(output_file)
    output_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"Saved structured results to: {output_path}")


if __name__ == "__main__":
    main()
