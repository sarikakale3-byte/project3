import os

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")


def get_embeddings() -> Embeddings:
    """Factory for the configured embedding provider.

    Supports OpenAI and HuggingFace embeddings. Configure via EMBEDDING_PROVIDER
    environment variable.
    """
    if EMBEDDING_PROVIDER == "openai":
        return OpenAIEmbeddings(model="text-embedding-3-small")
    elif EMBEDDING_PROVIDER == "huggingface":
        model_name = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        hf_token = os.getenv("HF_TOKEN")
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"token": hf_token} if hf_token else {}
        )
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER}")
