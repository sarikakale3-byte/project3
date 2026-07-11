import json
import re
from functools import lru_cache

from langchain_core.tools import tool

from .llm import get_llm
from .model import IntentResult


# Deterministic keyword-based intent classification
_INTENT_RULES: list[tuple[str, list[str], str]] = [
    (
        "claim_rejection",
        [
            r"claim rejected",
            r"claim denied",
            r"rejection reason",
            r"why was my claim rejected",
            r"claim decline",
            r"not approved",
            r"claim repudiated",
        ],
        "claims_review_team",
    ),
    (
        "complaint",
        [
            r"\bcomplaint\b",
            r"frustrat",
            r"upset",
            r"angry",
            r"escalate",
            r"poor service",
            r"worst service",
            r"still waiting",
            r"no response",
            r"delay in claim",
        ],
        "grievance_redressal_team",
    ),
    (
        "claim_status",
        [
            r"claim status",
            r"status of claim",
            r"track claim",
            r"claim update",
            r"claim progress",
            r"where is my claim",
            r"claim processing",
        ],
        "claims_operations_team",
    ),
    (
        "claim_submission",
        [
            r"submit claim",
            r"file claim",
            r"register claim",
            r"new claim",
            r"claim application",
            r"claim request",
        ],
        "claims_intake_team",
    ),
    (
        "document_request",
        [
            r"required documents",
            r"claim documents",
            r"document checklist",
            r"supporting documents",
            r"upload documents",
            r"paperwork",
        ],
        "documentation_team",
    ),
    (
        "policy_coverage",
        [
            r"policy coverage",
            r"covered under policy",
            r"coverage details",
            r"sum insured",
            r"deductible",
            r"policy benefits",
            r"policy exclusion",
            r"what is covered",
        ],
        "policy_services_team",
    ),
    (
        "reimbursement_query",
        [
            r"reimbursement",
            r"settlement amount",
            r"claim payment",
            r"when will i receive payment",
            r"claim settlement",
            r"payment status",
            r"cashless claim",
            r"refund status",
        ],
        "settlement_team",
    ),
]

_DEFAULT_ROUTING = "customer_support"


def _classify(customer_message: str) -> IntentResult:
    text = customer_message.lower()

    for intent, patterns, routing in _INTENT_RULES:
        matches = sum(
            1 for pattern in patterns
            if re.search(pattern, text)
        )

        if matches:
            confidence = min(0.6 + (0.15 * matches), 0.98)

            return IntentResult(
                intent=intent,
                confidence=confidence,
                routing=routing
            )

    return IntentResult(
        intent="general_faq",
        confidence=0.5,
        routing=_DEFAULT_ROUTING
    )


@tool
def classify_intent(customer_message: str) -> str:
    """
    Deterministically classify the customer's message into an
    insurance-related intent category using keyword rules.

    Use this tool to identify claim-related issues and route them to the
    appropriate operations team.

    It does NOT answer policy or claim-processing questions.
    Use knowledge_retrieval for factual insurance information.

    Returns:
    {
        "intent": str,
        "confidence": float,
        "routing": str
    }

    Supported intents:
    - claim_status
    - claim_submission
    - document_request
    - policy_coverage
    - claim_rejection
    - reimbursement_query
    - complaint
    - general_faq
    """
    return _classify(customer_message).model_dump_json()


@lru_cache(maxsize=1)
def _get_rag_pipeline():
    from .rag.pipeline import RAGPipeline

    return RAGPipeline(llm=get_llm())


# Initialize during startup to avoid thread-safety issues
_get_rag_pipeline()


@tool
def knowledge_retrieval(query: str) -> str:
    """
    Retrieve a grounded and cited answer from the Insurance Knowledge Base.

    Use this tool whenever a customer asks factual questions regarding:

    - Policy coverage and exclusions
    - Claim procedures
    - Claim submission guidelines
    - Required documents
    - Settlement timelines
    - Reimbursement process
    - Eligibility criteria
    - Cashless claims
    - Network hospitals/garages
    - Claim rejection reasons
    - Insurance FAQs

    Returns:

    {
        "answer": str,
        "citations": list[str]
    }
    """
    rag_answer = _get_rag_pipeline().answer(query)

    return json.dumps(
        {
            "answer": rag_answer.answer,
            "citations": rag_answer.citations
        }
    )