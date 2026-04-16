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

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file using `.env.example`.

For OpenAI:

```env
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=resume-screening-assignment
```

For Hugging Face:

```env
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=resume-screening-assignment
```

For Groq:

```env
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=resume-screening-assignment
```

## Run the Project

Using OpenAI:

```bash
python main.py --provider openai --model gpt-4o-mini
```

Using Hugging Face:

```bash
python main.py --provider huggingface --model mistralai/Mixtral-8x7B-Instruct-v0.1
```

Using Groq:
```bash
python main.py --provider groq --model llama-3.1-8b-instant
```

The program will:

- evaluate all three resumes
- print score and explanation for each candidate
- save structured results to `outputs/results.json`

## LangSmith Tracing Requirements

Make sure these environment variables are set:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=resume-screening-assignment
```

You should see at least three resume runs in LangSmith:

- `strong_resume.txt`
- `average_resume.txt`
- `weak_resume.txt`

The traces will show:

- job description extraction
- resume extraction
- explanation generation

This makes debugging easy and satisfies the tracing requirement.

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

## Scoring Logic

The final score is out of 100 and is based on:

- required skill match: 45 points
- required tool match: 20 points
- experience match: 20 points
- education match: 5 points
- resume evidence quality: 10 points

This scoring approach is intentionally explainable and easy to justify in a report.

## Debugging and Incorrect Output Discussion

If the LLM extracts a borderline skill too generously, the deterministic scoring notes and LangSmith traces make it easier to inspect where the mismatch happened.

One useful debugging example is the average resume:

- it mentions `Basic Machine Learning`
- it does not clearly show strong supervised learning depth
- traces help verify whether the extraction step was too lenient

That gives you a concrete example to discuss in your report under "incorrect output" and debugging.

## Submission Notes

For your assignment submission, include:

- the complete code
- LangSmith screenshots showing traces
- a short report explaining the pipeline, scoring logic, prompts, and debugging observations
- your GitHub link if required

## Important Note

This project avoids hardcoded candidate outcomes. Scores are computed from extracted resume evidence and job requirements, then explained through a grounded explanation step.
