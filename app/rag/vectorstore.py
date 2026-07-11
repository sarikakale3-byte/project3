"""
Chroma vector store configuration for the Insurance Claim
Processing Assistant knowledge base.

Indexed documents may include:

- Policy Coverage FAQs
- Claim Submission Guides
- Claim Rejection Policies
- Reimbursement Policies
- Document Checklists
- Insurance FAQs
"""

import os

from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever

from .embeddings import get_embeddings


COLLECTION_NAME = "insurance_claims_knowledge_base"


def _persist_dir() -> str:
    return os.getenv(
        "CHROMA_PERSIST_DIR",
        "./data/chroma_db"
    )


def get_vectorstore() -> Chroma:
    """
    Returns the Chroma vector store used for storing
    insurance knowledge-base embeddings.
    """
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=_persist_dir(),
    )


def get_dense_retriever(
    k: int = 5,
) -> BaseRetriever:
    """
    Dense vector retriever used by the RAG pipeline.

    Returns top-k semantically relevant insurance
    documents for a customer query.
    """
    return get_vectorstore().as_retriever(
        search_kwargs={"k": k}
    )