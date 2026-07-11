from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import threading
from dotenv import load_dotenv
from .chain import chat
from . import memory
from .model import ChatRequest, ChatResponse, ResetRequest, IngestRequest, IngestResponse, IngestStatusResponse, EvaluateResponse, EvaluateStatusResponse, SourceDocument, DeleteResponse
from .job_tracker import job_tracker
from .rag.ingest import run_ingest

load_dotenv()

app = FastAPI(
    title="SK Insurance Claim Assistant",
    description ="Langchain powered description smart bot for memeory, cache and structured output"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
def chat_endpoint(req: ChatRequest) :
    try:
        response_text, cached = chat(session_id=req.session_id, message=req.message)
        return ChatResponse(session_id=req.session_id, response=response_text, cached=cached)
    except Exception as exc :
        raise HTTPException(
        status_code=500,
        detail=str(exc)
    )


@app.post("/reset")
def reset_endpoint(req: ResetRequest) -> bool :
    memory.clear_session(req.session_id)
    return True


@app.get("/health")
def health_endpoint() -> dict:
    checks = {}

    try:
        from .rag.vectorstore import get_vectorstore
        collection_count = len(get_vectorstore().get()["ids"])
        checks["vectorstore"] = {"ok": True, "chunk_count": collection_count}
    except Exception as exc:
        checks["vectorstore"] = {"ok": False, "error": str(exc)}

    try:
        memory._get_client().ping()
        checks["redis"] = {"ok": True}
    except Exception as exc:
        checks["redis"] = {"ok": False, "error": str(exc)}

    checks["openai_api_key_configured"] = bool(os.getenv("OPENAI_API_KEY"))

    status = "ok" if checks["vectorstore"]["ok"] and checks["redis"]["ok"] else "degraded"
    return {"status": status, "checks": checks}


def _run_ingest_job(job_id: str, custom_dir: str | None) -> None:
    """Background task to run ingestion and update job status."""
    try:
        job_tracker.mark_running(job_id)
        
        # Temporarily override the knowledge base directory if provided
        original_dir = os.getenv("KNOWLEDGE_BASE_DIR")
        if custom_dir:
            os.environ["KNOWLEDGE_BASE_DIR"] = custom_dir
        
        try:
            chunks_ingested = run_ingest()
            job_tracker.mark_completed(job_id, chunks_ingested)
        finally:
            # Restore original directory
            if custom_dir:
                if original_dir:
                    os.environ["KNOWLEDGE_BASE_DIR"] = original_dir
                else:
                    os.environ.pop("KNOWLEDGE_BASE_DIR", None)
                    
    except Exception as exc:
        job_tracker.mark_failed(job_id, str(exc))


@app.post("/ingest", response_model=IngestResponse)
def ingest_endpoint(req: IngestRequest) -> IngestResponse:
    """Trigger async ingestion of knowledge base documents into the vector store."""
    job = job_tracker.create_job("ingest")
    
    # Run ingestion in background thread
    thread = threading.Thread(
        target=_run_ingest_job,
        args=(job.job_id, req.knowledge_base_dir),
        daemon=True
    )
    thread.start()
    
    return IngestResponse(
        job_id=job.job_id,
        status="pending",
        message="Ingestion job started. Use /ingest/status/{job_id} to check progress."
    )


@app.get("/ingest/status/{job_id}", response_model=IngestStatusResponse)
def ingest_status_endpoint(job_id: str) -> IngestStatusResponse:
    """Get the status of an ingestion job."""
    job = job_tracker.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    return IngestStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        started_at=job.started_at,
        completed_at=job.completed_at,
        chunks_ingested=job.chunks_ingested,
        error=job.error
    )


@app.post("/evaluate")
def evaluate_endpoint() -> dict:
    """Run evaluation against the test dataset."""
    try:
        from eval.run_eval import run_eval
        result = run_eval()
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@app.get("/sources", response_model=list[SourceDocument])
def list_sources() -> list[SourceDocument]:
    """List all indexed documents with metadata and chunk counts."""
    try:
        from .rag.vectorstore import get_vectorstore
        vectorstore = get_vectorstore()
        
        # Get all documents
        result = vectorstore.get()
        ids = result.get("ids", [])
        metadatas = result.get("metadatas", [])
        
        # Group by source document
        sources = {}
        for chunk_id, metadata in zip(ids, metadatas):
            if metadata is None:
                continue
            
            source = metadata.get("source", "unknown")
            if source not in sources:
                sources[source] = {
                    "doc_id": source,
                    "filename": source,
                    "chunk_count": 0,
                    "last_queried": None
                }
            sources[source]["chunk_count"] += 1
        
        return [SourceDocument(**source) for source in sources.values()]
        
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list sources: {str(exc)}"
        )


@app.delete("/sources/{doc_id}", response_model=DeleteResponse)
def delete_source(doc_id: str) -> DeleteResponse:
    """Delete a document and all its chunks from the vector store."""
    try:
        from .rag.vectorstore import get_vectorstore
        vectorstore = get_vectorstore()
        
        # Get all documents
        result = vectorstore.get()
        ids = result.get("ids", [])
        metadatas = result.get("metadatas", [])
        
        # Find chunks belonging to this document
        chunks_to_delete = []
        for chunk_id, metadata in zip(ids, metadatas):
            if metadata is None:
                continue
            
            source = metadata.get("source", "")
            if source == doc_id:
                chunks_to_delete.append(chunk_id)
        
        if not chunks_to_delete:
            raise HTTPException(
                status_code=404,
                detail=f"Document '{doc_id}' not found in vector store"
            )
        
        # Delete the chunks
        vectorstore.delete(ids=chunks_to_delete)
        
        return DeleteResponse(
            doc_id=doc_id,
            deleted_chunks=len(chunks_to_delete),
            message=f"Successfully deleted {len(chunks_to_delete)} chunks from '{doc_id}'"
        )
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete source: {str(exc)}"
        )
