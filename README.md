# Universal LLM-Powered Data Assistant

Backend MVP for ULDA, an AI assistant that ingests enterprise documents and lets users ask natural-language questions across connected data sources.

## Problem Statement

Enterprise data is usually scattered across PDFs, spreadsheets, documents, and databases. ULDA solves this by creating a single conversational interface that ingests source data, indexes its content, and returns contextual answers with source citations.

## Features

- Upload and ingest `TXT`, `PDF`, `CSV`, `DOCX`, and `XLSX` sources
- Connect a PostgreSQL source and ingest table/schema summaries
- Automatic text extraction and chunking
- Source and document catalog endpoints
- Conversation storage and message history
- ChromaDB-backed chunk storage and retrieval
- RAG-based chat endpoint with citation-ready responses
- Optional OpenAI response generation when `ULDA_OPENAI_API_KEY` is configured
- Local SQLite default setup for quick MVP development

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Optionally create a `.env` file in the project root:

```env
ULDA_APP_DATABASE_URL=sqlite:///./ulda.db
ULDA_UPLOAD_DIR=assets/uploads
ULDA_CHROMA_PATH=assets/chroma
ULDA_OPENAI_API_KEY=your-api-key
```

The app stores application entities in the SQL database and keeps chunks/embeddings in ChromaDB.
For a real LLM response path, set `ULDA_OPENAI_API_KEY`. Otherwise ULDA uses local deterministic embeddings.
In this current Python 3.14 environment, the vector layer automatically falls back to a local persistent store because Chroma's Python package is not fully compatible here. On Python 3.11/3.12, the same abstraction uses ChromaDB directly.

## Usage

Start the development server:

```bash
uvicorn src.app.main:app --reload
```

Open the API docs at `http://127.0.0.1:8000/docs`.

Useful endpoints:

- `POST /api/v1/sources/upload`
- `POST /api/v1/sources/postgresql`
- `GET /api/v1/sources/`
- `POST /api/v1/conversations/`
- `POST /api/v1/chat/query`
- `GET /api/v1/conversations/{conversation_id}/messages`

## Screenshots

No screenshots are included yet. The repository includes a demo source file in `assets/demo_company_policy.txt` for local testing.

## Technology Stack

- Python
- FastAPI
- SQLModel
- SQLAlchemy
- PostgreSQL
- SQLite fallback for local development
- ChromaDB
- Pydantic Settings
- PyPDF
- OpenPyXL
- python-docx
- OpenAI API
- PostgreSQL / SQLAlchemy connectors

## Architecture

See [docs/architecture.md](/Users/muslimakosmagambetova/online_learning/docs/architecture.md).

## Repository Structure

```text
project-root/
├── src/
├── docs/
├── tests/
├── assets/
├── README.md
├── AUDIT.md
├── .gitignore
├── LICENSE
├── alembic.ini
└── requirements.txt
```
# ulda
