# Insurance Claims Assistant

A LangChain-based AI assistant for insurance claim processing with a tool-calling agent, RAG-backed knowledge retrieval, Redis-backed session memory, and a FastAPI backend with Streamlit frontend.

## Tech Stack

- **LLM**: GPT-4o-mini (OpenAI)
- **Embeddings**: text-embedding-3-small (OpenAI)
- **Reranker**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Vector Store**: ChromaDB
- **Cache/Memory**: Redis (Upstash)
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Agent Framework**: LangChain

## Project Structure

```
├── strealit.py            # Chatbot UI (Streamlit)
app/
├── main.py                 # FastAPI app: /chat, /reset, /health, /ingest, /sources
├── chain.py                # Tool-calling agent with memory + cache wiring
├── tools.py                # Intent classification + knowledge retrieval
├── model.py                # Pydantic request/response models
├── prompts.py              # System prompt + few-shot examples
├── memory.py               # Redis-backed session chat history
├── cache.py                # Redis-backed response cache
├── llm.py                  # Shared ChatOpenAI instance
├── logging_utils.py        # Structured JSON logging
├── job_tracker.py          # Async job tracking for ingestion
└── rag/
    ├── __init__.py
    ├── chunking.py         # Document chunking with overlap
    ├── embeddings.py       # Embedding factory (OpenAI)
    ├── hybrid_retriever.py # BM25 + Dense ensemble retrieval
    ├── ingest.py           # Document ingestion pipeline
    ├── loaders.py          # PDF, DOCX, HTML, CSV loaders
    ├── pipeline.py         # RAG pipeline with re-ranking
    ├── query_transform.py  # Multi-query transformation
    ├── reranker.py         # Cross-encoder re-ranking
    └── vectorstore.py      # ChromaDB vector store

data/
├── knowledge_base/         # Source documents (PDF/DOCX/HTML/CSV)
└── generate_sample_docs.py # One-off generator for sample docs

eval/
├── dataset.py              # Hand-written QA pairs (14 items)
├── metrics.py              # Ragas + LLM-judge scoring
└── run_eval.py             # CLI entrypoint, writes JSON results

tests/
├── test_chunking.py        # Chunking unit tests
├── test_embeddings.py      # Embedding tests
├── test_dataset.py         # Dataset validation tests
├── test_integration.py     # API integration tests
├── test_loaders.py         # Document loader tests
└── test_metrics.py         # Evaluation metrics tests

```

## Setup Instructions

### 1. Clone the Repository

git clone <your-repo-url>
cd project3

### 2. Create and Activate Virtual Environment

python3 -m venv venv

source venv/bin/activate

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Configure Environment Variables

Create a .env file at root level abnd add below:

# OpenAI
OPENAI_API_KEY=<your_api_key_here>

# LangSmith (for tracing)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<your_langsmith_api_key>
LANGSMITH_PROJECT=insurance-bot

# Redis (Upstash)
UPSTASH_REDIS_REST_URL=<https://your-redis-url.upstash.io>
UPSTASH_REDIS_REST_TOKEN=<your-redis-token>

# Vector Store
CHROMA_PERSIST_DIR=./data/chroma_db

# Knowledge Base
KNOWLEDGE_BASE_DIR=./data/knowledge_base

# FastAPI
FASTAPI_URL=http://localhost:8000

### 5. Ingest Documents into Vector Store

This loads the knowledge base, chunks it, embeds it with OpenAI, and upserts it into a persistent Chroma collection. **Run this once before starting the API** (and again any time the knowledge base changes):

python -m app.rag.ingest

### 6. Run the Backend API

uvicorn app.main:app --reload

The API will be available at `http://localhost:8000`.

#### API Endpoints

- `GET /health` - Health check (vector store + Redis connectivity)
- `POST /chat` - Chat with the agent
  ```json
  {
    "message": "How do I file a claim?",
    "session_id": "user-123"
  }
  ```
- `POST /reset` - Clear session memory
  ```json
  {
    "session_id": "user-123"
  }
  ```
- `POST /ingest` - Trigger document ingestion (async)
- `GET /ingest/status/{job_id}` - Check ingestion job status
- `GET /sources` - List all documents in knowledge base
- `DELETE /sources/{doc_id}` - Delete a document
- `POST /evaluate` - Run evaluation
- `POST /retrieve` - Pure retrieval (debug endpoint)

**Interactive API Docs:** http://localhost:8000/docs

### 7. Run the Streamlit Frontend

In a second terminal (with the venv activated):

streamlit run streamlit.py

Open http://localhost:8501 and chat with the bot.

## Running Tests

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_chunking.py
pytest tests/test_integration.py
pytest tests/test_metrics.py

## Running Evaluation

Measures retrieval quality, answer quality, and end-to-end quality against a fixed QA dataset:

python -m eval.run_eval

Results are written as structured JSON to `eval/results/eval_<timestamp>.json`.

## How It Works

### 1. Intent Classification

When a user sends a message, the agent first classifies the intent using deterministic rules:

- `greeting` - Hello, hi, hey
- `claim_status` - Check claim status
- `file_claim` - File a new claim
- `policy_info` - Policy coverage questions
- `upload_docs` - Document upload requests
- `general_faq` - General insurance questions
- `human_handoff` - Request human agent
- `out_of_scope` - Off-topic queries

### 2. Knowledge Retrieval (RAG)

For knowledge-based intents, the system:

1. **Multi-Query Transform**: LLM generates 3-4 query variants
2. **Hybrid Retrieval**: Each query retrieves via:
   - **BM25** (sparse, keyword-based) - weight: 0.4
   - **Dense** (vector-based, OpenAI embeddings) - weight: 0.6
3. **Re-ranking**: Cross-encoder scores and ranks all results
4. **Top-K Selection**: Returns top 4 most relevant chunks

### 3. Response Generation

The LLM generates an answer using:
- Retrieved context chunks with citations
- System prompt with insurance assistant guidelines
- Few-shot examples for consistent formatting

### 4. Caching & Memory

- **Response Cache**: SHA256 hash of (query + context), 1-hour TTL
- **Session Memory**: Redis-backed chat history with configurable TTL

## Configuration

### Chunking
- **Default chunk size**: 500 characters
- **Default overlap**: 75 characters
- **Strategy**: Recursive character splitting

### Retrieval
- **Retrieve K**: 5 documents per query
- **Rerank Top N**: 4 documents
- **BM25 Weight**: 0.4
- **Dense Weight**: 0.6

### LLM
- **Model**: gpt-4o-mini
- **Temperature**: 0.1 (deterministic)
- **Max Tokens**: 500

## Development

### Adding New Document Types

Edit `app/rag/loaders.py`:

_LOADER_BY_EXTENSION = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".html": lambda path: BSHTMLLoader(path, open_encoding="utf-8"),
    ".htm": lambda path: BSHTMLLoader(path, open_encoding="utf-8"),
    ".csv": CSVLoader,
    # Add new type here
}

### Adding New Intents

Edit `app/tools.py` and add a new pattern to `INTENT_PATTERNS`:

INTENT_PATTERNS = [
    (r"\b(hello|hi|hey)\b", "greeting"),
    # Add new intent here
]


### Adding New Evaluation Metrics

Edit `eval/metrics.py` and add a new judge function:

def judge_custom_metric(answer: str, context: list[str]) -> ScoreResult:
    prompt = f"Evaluate custom metric...\n\nANSWER:\n{answer}\n\nCONTEXT:\n{context}"
    return _judge(prompt, ScoreResult)

## Troubleshooting

### Redis Connection Issues

- Verify `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` in `.env`
- Check Upstash dashboard for connection limits
- Ensure firewall allows outbound HTTPS to Upstash

### ChromaDB Issues

- Verify `CHROMA_PERSIST_DIR` exists and is writable
- Delete `./data/chroma_db` and re-run ingestion if corrupted
- Check disk space for vector storage

### OpenAI API Errors

- Verify `OPENAI_API_KEY` is set correctly
- Check API key has credits available
- Ensure you're using a supported model (gpt-4o-mini, text-embedding-3-small)