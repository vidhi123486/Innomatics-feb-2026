# AI Resume Screening System with Tracing

This project implements a modular AI-powered resume screening system using LangChain and LangSmith tracing.

It satisfies requirements:

- taking one job description and at least three resumes as input
- extracting skills, tools, education, and experience
- applying matching logic against job requirements
- producing a score from 0 to 100
- generating an explanation for the score
- enabling LangSmith tracing for every pipeline step
- using a modular structure with `prompts/`, `chains/`, and `main.py`
- using `PromptTemplate`, LCEL, and `.invoke()`

## Project Structure

```text
.
|-- chains/
|   |-- __init__.py
|   |-- explanation_chain.py
|   |-- extraction_chain.py
|   |-- llm_factory.py
|   |-- schemas.py
|   `-- scoring.py
|   `-- scoring_chain.py
|-- data/
|   |-- job_description.txt
|   `-- resumes/
|       |-- average_resume.txt
|       |-- strong_resume.txt
|       `-- weak_resume.txt
|-- prompts/
|   |-- explanation_prompt.txt
|   `-- extraction_prompt.txt
|-- outputs/
|-- .env.example
|-- main.py
|-- README.md
`-- requirements.txt
```

## How the Pipeline Works

1. The system reads the job description and each resume.
2. A LangChain extraction chain pulls structured details from the text.
3. A deterministic scoring module compares the resume against the job requirements.
4. A second LangChain chain produces a grounded explanation using only extracted evidence.
5. LangSmith tracing records each run and each step for debugging.

Expected flow:

```text
Resume -> Extract -> Match -> Score -> Explain -> Trace
```

## Prompt Engineering Choices

The prompts are designed to:

- use clear instructions
- enforce structured JSON output
- avoid hallucinations
- avoid assuming skills that are not present in the resume

Example rule included in the prompt:

```text
Do not invent skills, tools, education, or experience.
If something is unclear, leave it out instead of guessing.
```

## Important Note

This project avoids hardcoded candidate outcomes. Scores are computed from extracted resume evidence and job requirements, then explained through a grounded explanation step.
