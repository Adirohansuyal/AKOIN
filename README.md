# COREP Reporting Assistant

An LLM-powered prototype for automating PRA COREP regulatory reporting using RAG (Retrieval-Augmented Generation) and structured output generation.

## Overview of the System

This system assists financial institutions in generating COREP (Common Reporting) templates by combining regulatory knowledge retrieval with LLM-based data extraction and validation.

**Key Features:**
- RAG-based regulatory context retrieval
- Structured COREP template generation (C01.00, C02.00)
- Field validation and aggregation
- FastAPI backend + Streamlit frontend
- Docker containerized deployment

## Architecture

### Flow
```
User → Streamlit → FastAPI → Retrieval → LLM → Template → UI
```

### Components
- **Backend (FastAPI)**: REST API for COREP generation and validation
- **Frontend (Streamlit)**: Interactive UI for template selection and data input
- **RAG Engine**: Semantic search over regulatory documents using FAISS
- **LLM Integration**: Groq API for structured output generation

### System Diagram

```
                    ┌──────────────────────┐
                    │   Streamlit UI       │
                    │  (Chat Interface)   │
                    └─────────┬────────────┘
                              │
                              │ User Query
                              ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │  Backend Orchestrator│
                    └─────────┬────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼

 ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
 │  RAG Retriever │  │   Groq LLM     │  │ Validation     │
 │ (FAISS +       │  │ Interpretation │  │ Engine         │
 │ Embeddings)    │  │ + Structuring  │  │                │
 └───────┬────────┘  └────────┬───────┘  └────────┬───────┘
         │                    │                   │
         │ Retrieved Rules   │ JSON Output       │ Flags
         ▼                    ▼                   ▼

            ┌────────────────────────────────┐
            │   Field Aggregation Layer      │
            │ (Combine CET1 components etc.)│
            └───────────────┬────────────────┘
                            │
                            ▼
                 ┌────────────────────────┐
                 │ Template Mapper       │
                 │ COREP C01.00 Extract  │
                 └────────────┬──────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ Structured Output   │
                    │ Template Table      │
                    │ Audit Log           │
                    └──────────────────────┘
```

The system begins with a Streamlit chat interface where the user submits a regulatory reporting scenario. The FastAPI backend orchestrates the workflow. A Retrieval-Augmented Generation layer searches PRA and COREP regulatory texts using vector embeddings. Retrieved rules are passed to a Groq-hosted LLM, which interprets them and produces structured COREP-aligned JSON output. A deterministic aggregation and validation layer ensures field consistency. Finally, the data is mapped into a human-readable COREP template extract with an accompanying audit trail.

## Prerequisites

- Python 3.8+
- Docker & Docker Compose (optional)
- Groq API key

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd corep_assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

4. Add regulatory data:
```bash
# Place regulatory text in data/regulatory_text.txt
```

### Docker Setup

```bash
docker-compose up --build
```

## Usage

### Running Locally

**Start Backend:**
```bash
uvicorn app:app --reload --port 8000
```

**Start Frontend:**
```bash
streamlit run streamlit_app.py --server.port 8501
```

### Using Docker

```bash
docker-compose up
```

Access the application:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

### `POST /generate`

Generate COREP report from input data.

**Request:**
```json
{
  "template": "C01.00",
  "input_data": {
    "share_capital": 500000,
    "retained_earnings": 200000
  }
}
```

**Response:**
```json
{
  "template": "C01.00",
  "fields": {
    "common_equity_tier_1": 700000,
    "tier_1_capital": 700000
  },
  "validation": {
    "valid": true,
    "errors": []
  }
}
```

## Project Structure

```
corep_assistant/
├── app.py                  # FastAPI backend
├── streamlit_app.py        # Streamlit frontend
├── rag.py                  # RAG engine
├── llm.py                  # LLM integration
├── validation.py           # Field validation
├── template_mapper.py      # Template mapping
├── aggregator.py           # Field aggregation
├── schema.py               # Data schemas
├── data/                   # Regulatory documents
├── docker-compose.yml      # Docker orchestration
├── Dockerfile.backend      # Backend container
├── Dockerfile.frontend     # Frontend container
└── requirements.txt        # Python dependencies
```

## Configuration

Edit `.env` to configure:

```env
GROQ_API_KEY=your_api_key_here
```

## Development

**Run tests:**
```bash
pytest
```

**Format code:**
```bash
black .
```

## Limitations

- Prototype stage - not production-ready
- Limited to C01.00 and C02.00 templates
- Requires manual regulatory document preparation
- No persistent storage

## License

MIT

## Contributing

Contributions welcome. Please open an issue before submitting PRs.
