from pydantic import BaseModel, Field
import os

class IntentResult(BaseModel):
    intent: str = Field(
        description="""
        claim_status | claim_submission | document_request |
        policy_coverage | claim_rejection | reimbursement_query |
        complaint | general_faq
        """
    )
    confidence: float = Field(ge=0, le=1)
    routing: str


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Customer insurance-related query"
    )
    session_id: str = Field(
        default="default",
        description="Chat session identifier"
    )


class ChatResponse(BaseModel):
    response: str
    session_id: str
    cached: bool = False


class ResetRequest(BaseModel):
    session_id: str = Field(
        default="default",
        description="Session identifier to reset"
    )


class ClaimDetails(BaseModel):
    claim_id: str
    policy_number: str
    claim_type: str = Field(
        description="health | motor | life | travel | property"
    )
    status: str = Field(
        description="submitted | under_review | approved | rejected | settled"
    )


class RetrievedChunk(BaseModel):
    content: str
    source: str
    score: float


class RAGAnswer(BaseModel):
    answer: str
    citations: list[str] = Field(default_factory=list)
    contexts: list[RetrievedChunk] = Field(default_factory=list)


class ClaimSubmissionRequest(BaseModel):
    customer_name: str
    policy_number: str
    claim_type: str = Field(
        description="health | motor | life | travel | property"
    )
    incident_date: str
    description: str


class ClaimSubmissionResponse(BaseModel):
    claim_id: str
    message: str
    status: str = "submitted"


class ClaimStatusResponse(BaseModel):
    claim_id: str
    policy_number: str
    status: str
    remarks: str | None = None


class PolicyCoverageResponse(BaseModel):
    policy_number: str
    coverage_details: str
    deductible: float | None = None
    sum_insured: float | None = None


class IngestRequest(BaseModel):
    knowledge_base_dir: str = Field(
        default=os.getenv("KNOWLEDGE_BASE_DIR", "./data/knowledge_base"),
        description="Knowledge base directory path (default: from KNOWLEDGE_BASE_DIR env var or ./data/knowledge_base)"
    )


class IngestResponse(BaseModel):
    job_id: str
    status: str
    message: str


class IngestStatusResponse(BaseModel):
    job_id: str
    status: str
    started_at: float | None = None
    completed_at: float | None = None
    chunks_ingested: int | None = None
    error: str | None = None


class EvaluateResponse(BaseModel):
    job_id: str
    status: str
    message: str


class EvaluateStatusResponse(BaseModel):
    job_id: str
    status: str
    started_at: float | None = None
    completed_at: float | None = None
    summary: dict | None = None
    error: str | None = None


class SourceDocument(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    last_queried: float | None = None


class DeleteResponse(BaseModel):
    doc_id: str
    deleted_chunks: int
    message: str
