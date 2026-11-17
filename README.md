# AI Knowledge Assistant

### A Retrieval-Augmented Generation (RAG) Backend for Intelligent Document Search and Question Answering

AI Knowledge Assistant is a Python-based RAG application that enables users to interact with their documents through natural-language questions.

The system processes documents, extracts and chunks their content, generates semantic embeddings, retrieves relevant information, and uses a Large Language Model (LLM) to generate context-aware responses grounded in the retrieved knowledge.

Built with **FastAPI, PostgreSQL, Sentence Transformers, LangChain, and Groq**, this project focuses on modular backend architecture and practical implementation of Retrieval-Augmented Generation.

---

## Overview

Traditional LLM applications can generate answers that are not supported by a user's private knowledge.

AI Knowledge Assistant addresses this challenge by implementing a Retrieval-Augmented Generation pipeline.

Instead of relying entirely on the LLM's internal knowledge, the system retrieves relevant information from uploaded documents and supplies that context to the model before generating a response.

### Key Capabilities

- Document ingestion and text extraction.
- Support for PDF, TXT, and DOCX documents.
- Text cleaning and intelligent chunking.
- Semantic embedding generation using Sentence Transformers.
- Similarity-based document retrieval.
- Re-ranking of retrieved chunks.
- Context-aware prompt construction.
- LLM-powered answer generation using Groq.
- Grounded responses based on retrieved document content.
- Fallback response when relevant information is unavailable.
- PostgreSQL database integration.
- Database schema and migration management with Alembic.
- Automated testing with Pytest.

---

## Architecture

The application follows a modular Retrieval-Augmented Generation architecture.

### Document Ingestion Pipeline

```text
Document Upload
      |
      v
File Validation
      |
      v
Text Extraction
(PDF / TXT / DOCX)
      |
      v
Text Cleaning
      |
      v
Text Chunking
      |
      v
Embedding Generation
      |
      v
Knowledge Storage
      |
      v
Documents Ready for Retrieval
```

### Question Answering Pipeline

```text
User Question
      |
      v
Question Embedding
      |
      v
Semantic Retrieval
      |
      v
Top 10 Relevant Chunks
      |
      v
Re-ranking
      |
      v
Top 5 Relevant Chunks
      |
      v
Context Builder
      |
      v
Prompt Construction
      |
      v
Groq LLM
      |
      v
Grounded Answer
      |
      v
Response to User
```

### RAG Pipeline Components

| Component | Responsibility |
|---|---|
| Document Parser | Extracts text from supported file formats |
| Text Splitter | Divides documents into manageable chunks |
| Embedding Model | Converts text into numerical vectors |
| Retriever | Finds semantically relevant chunks |
| Re-ranker | Improves relevance of retrieved results |
| Context Builder | Organizes retrieved information |
| Prompt Template | Provides instructions and context to the LLM |
| LLM Service | Generates the final response |
| RAG Service | Orchestrates the complete pipeline |

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Core programming language |
| FastAPI | REST API development |
| PostgreSQL | Relational database |
| SQLAlchemy | Database ORM |
| Alembic | Database migrations |
| Sentence Transformers | Semantic embedding generation |
| LangChain Text Splitters | Document chunking |
| Groq | LLM inference |
| PyMuPDF | PDF text extraction |
| python-docx | DOCX text extraction |
| Pydantic | Data validation and settings |
| PyJWT | JWT authentication |
| Argon2 | Secure password hashing |
| Poetry | Dependency and environment management |
| Pytest | Automated testing |

---

## Project Structure

```text
AI_knowledge_Assistant/
│
├── alembic/
│   └── migrations/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── test_documents/
│
├── tests/
│
├── alembic.ini
├── pyproject.toml
├── poetry.lock
├── .gitignore
└── README.md
```

*Note: The structure above illustrates the logical application layers. Refer to the repository for the exact current module and file names.*

---

## Installation and Setup

### Prerequisites

Make sure you have the following installed:

- Python 3.11 or higher
- Poetry
- PostgreSQL
- Git
- Groq API Key

### 1. Clone the Repository

```bash
git clone https://github.com/kubrasiraj/AI_knowledge_Assistant.git
```

```bash
cd AI_knowledge_Assistant
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Configure Environment Variables

Create a `.env` file in the project root.

Configure your database connection and Groq API credentials.

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/ai_knowledge_assistant

GROQ_API_KEY=your_groq_api_key
```

Add any additional authentication and application settings required by the project's configuration.

**Important:** Never commit your actual `.env` file or API keys to GitHub.

### 4. Run Database Migrations

```bash
poetry run alembic upgrade head
```

### 5. Start the FastAPI Server

```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 6. Explore API Documentation

FastAPI automatically provides interactive API documentation.

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Testing

The project uses Pytest for testing individual components and application functionality.

Run the complete test suite:

```bash
poetry run pytest
```

Run tests with verbose output:

```bash
poetry run pytest -v
```

The repository also contains component-level tests covering:

- Document parsing
- Text chunking
- Embedding generation
- Context construction
- Database operations
- LLM integration
- Retrieval
- Re-ranking
- RAG pipeline

---

## Design Principles

The project follows several practical AI engineering principles:

**1. Modular Architecture**

Individual RAG components are separated into services to improve maintainability and make the system easier to extend.

**2. Retrieval Before Generation**

The LLM receives relevant document context rather than being expected to answer every question from its pretrained knowledge.

**3. Relevance Optimization**

Retrieved chunks are re-ranked before context construction to improve the quality of information provided to the LLM.

**4. Grounded Responses**

The system is designed to return an insufficient-information response when the knowledge base does not contain relevant information.

**5. Database Versioning**

Alembic manages database schema changes through migrations.

**6. Testability**

Individual components have dedicated tests, allowing functionality to be verified independently.



## Learning Outcomes

This project demonstrates practical implementation and understanding of:

- Retrieval-Augmented Generation architecture.
- Document ingestion and preprocessing.
- Semantic search and vector embeddings.
- Retrieval and re-ranking strategies.
- LLM integration and prompt engineering.
- FastAPI backend development.
- PostgreSQL and SQLAlchemy.
- Authentication fundamentals.
- Database migrations.
- Modular service architecture.
- Testing AI-powered backend components.

---

## Author

**Kubra Siraj**

Computer Science Undergraduate | AI Engineering

Interested in Generative AI, Agentic AI, RAG Systems, and Python Backend Engineering.

- GitHub: https://github.com/kubrasiraj
- Project Repository: https://github.com/kubrasiraj/AI_knowledge_Assistant

---

*Built as a practical exploration of Retrieval-Augmented Generation and production-oriented AI backend engineering.*
