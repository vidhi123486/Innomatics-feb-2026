# RAG-Based Customer Support Assistant

This project is a Retrieval-Augmented Generation (RAG) based customer support assistant. It reads a customer support PDF knowledge base, stores the extracted information in ChromaDB, retrieves the most relevant content for a user query, and generates a grounded answer.

The project also includes routing logic and Human-in-the-Loop (HITL) escalation using a LangGraph workflow.

## Project Objective

The goal of this project is to build a customer support assistant that can:

- Process a PDF knowledge base
- Split the document into meaningful chunks
- Create embeddings for retrieval
- Store and search vectors using ChromaDB
- Answer user questions using retrieved context
- Route queries based on customer support intent
- Escalate low-confidence or sensitive queries to a human reviewer

## Knowledge Base

The current knowledge base file is:

```text
data/customer_support_q&a.pdf
```

This PDF contains customer support Q&A information for:

- Account management
- Billing and payments
- Orders and delivery
- Technical issues
- Refunds and returns

## Folder Structure

```text
Design & Build a RAG-Based Customer Support Assistant/
|-- chroma_db/
|-- data/
|   `-- customer_support_q&a.pdf
|-- src/
|   |-- __init__.py
|   |-- chunker.py
|   |-- embeddings.py
|   |-- hitl.py
|   |-- llm.py
|   |-- loader.py
|   |-- rag_pipeline.py
|   |-- retriever.py
|   |-- router.py
|   `-- workflow.py
|-- .env.example
|-- main.py
|-- README.md
`-- requirements.txt
```

## Main Files

| File | Purpose |
|---|---|
| `main.py` | Main entry point for running the assistant |
| `src/loader.py` | Loads and extracts text from PDF files |
| `src/chunker.py` | Splits extracted text into chunks |
| `src/embeddings.py` | Creates local deterministic embeddings |
| `src/retriever.py` | Stores and retrieves chunks from ChromaDB |
| `src/router.py` | Detects query intent such as orders, billing, account, or technical support |
| `src/hitl.py` | Handles Human-in-the-Loop escalation decisions |
| `src/workflow.py` | Defines the LangGraph workflow |
| `src/llm.py` | Generates the final answer from retrieved context |
| `src/rag_pipeline.py` | Connects all components together |

## Technology Used

- Python
- ChromaDB
- LangGraph
- PyPDF
- OpenAI package, optional

The project uses a local deterministic embedding model by default, so it can run without an OpenAI API key.

## Setup Instructions

Open VS Code terminal or CMD in the project folder.

### 1. Create a virtual environment

```cmd
python -m venv venv
```

If `python` does not work, use:

```cmd
py -m venv venv
```

### 2. Activate the virtual environment

```cmd
venv\Scripts\activate
```

After activation, the terminal should show `(venv)`.

### 3. Install dependencies

```cmd
pip install -r requirements.txt
```

## How to Run

### Step 1: Build the ChromaDB index

Run this once before asking questions:

```cmd
python main.py ingest
```

This command:

- Reads `data/customer_support_q&a.pdf`
- Extracts text from the PDF
- Splits the text into chunks
- Generates embeddings
- Stores the chunks in `chroma_db`

### Step 2: Ask questions in interactive mode

```cmd
python main.py
```

You will see:

```text
Ask a question (or type 'exit'):
```

Example:

```text
Ask a question (or type 'exit'): How can I track my order?
```

Expected output:

```text
Answer:
Use the tracking link in your order confirmation email.
```

Type `exit` to stop the assistant.

### Step 3: Ask a single question directly

```cmd
python main.py ask "How can I track my order?"
```

Example output:

```text
Answer:
Use the tracking link in your order confirmation email.
```

### Step 4: Run demo

```cmd
python main.py demo
```

This runs ingestion and then asks a default sample question.

## Sample Questions

Try these questions:

```cmd
python main.py ask "How can I track my order?"
python main.py ask "I forgot my password. What should I do?"
python main.py ask "How do I request a refund?"
python main.py ask "What payment methods do you support?"
python main.py ask "The app is not loading. What should I do?"
```

## HITL Escalation

Human-in-the-Loop escalation is triggered when:

- The query is sensitive
- The query is too vague
- No relevant chunks are found
- Retrieval confidence is low
- The query is complex and may require human judgment

Example:

```cmd
python main.py ask "I want to file a legal complaint"
```

Expected behavior:

```text
Answer:
Escalated to human reviewer. Reason: Sensitive customer issue requires human support review.
```

## Debug Output

For normal use, the assistant prints only the final answer.

If you want to inspect routing, confidence, sources, and HITL status, use:

```cmd
python main.py ask "How can I track my order?" --debug
```

Debug output includes:

- detected route
- route reason
- route confidence
- retrieval confidence
- HITL status
- source file and page number

## Configuration

The file `.env.example` shows optional configuration values:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
DATA_DIR=data
CHROMA_DIR=chroma_db
COLLECTION_NAME=customer_support_kb
CHUNK_SIZE=900
CHUNK_OVERLAP=150
TOP_K=4
MIN_CONFIDENCE=0.55
```

The project can run without creating a `.env` file because default values are already provided in the code.

## Important Notes

- Always run `python main.py ingest` after changing or replacing the PDF.
- The `chroma_db` folder is generated automatically after ingestion.
- The PDF should contain selectable text. Scanned image-only PDFs may not extract correctly.
- Use `--debug` only when you want detailed internal output.

## Project Flow

```text
PDF Knowledge Base
        |
        v
PDF Loader
        |
        v
Text Chunker
        |
        v
Embedding Generator
        |
        v
ChromaDB Vector Store
        |
        v
Retriever
        |
        v
LangGraph Workflow
        |
        v
Router + HITL Decision
        |
        v
Final Answer
```

## Evaluation Coverage

This project satisfies the required concepts:

- RAG system design
- PDF knowledge base processing
- Chunking
- Embeddings
- ChromaDB vector storage
- Retrieval layer
- Query answering
- LangGraph workflow
- Conditional routing
- Human-in-the-Loop escalation
- Customer support bot use case

