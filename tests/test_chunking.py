"""Unit tests for app.rag.chunking module."""
import pytest
from langchain_core.documents import Document

from app.rag.chunking import chunk_documents, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


class TestChunkDocuments:
    """Test chunk_documents function."""

    def test_chunk_documents_basic(self):
        """Test basic chunking functionality."""
        docs = [
            Document(
                page_content="This is a test document. " * 100,
                metadata={"source": "test.txt"}
            )
        ]
        
        chunks = chunk_documents(docs)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, Document) for chunk in chunks)

    def test_chunk_documents_adds_chunk_id(self):
        """Test that chunk_id is added to metadata."""
        docs = [
            Document(
                page_content="Test content. " * 50,
                metadata={"source": "test.txt"}
            )
        ]
        
        chunks = chunk_documents(docs)
        
        for i, chunk in enumerate(chunks):
            assert "chunk_id" in chunk.metadata
            assert chunk.metadata["chunk_id"] == f"test.txt::{i}"

    def test_chunk_documents_preserves_source(self):
        """Test that source metadata is preserved."""
        docs = [
            Document(
                page_content="Test content. " * 50,
                metadata={"source": "my_doc.pdf"}
            )
        ]
        
        chunks = chunk_documents(docs)
        
        for chunk in chunks:
            assert chunk.metadata["source"] == "my_doc.pdf"

    def test_chunk_documents_custom_size(self):
        """Test chunking with custom chunk size."""
        docs = [
            Document(
                page_content="Test content. " * 100,
                metadata={"source": "test.txt"}
            )
        ]
        
        chunks = chunk_documents(docs, chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) > 0

    def test_chunk_documents_empty_list(self):
        """Test chunking with empty document list."""
        chunks = chunk_documents([])
        assert len(chunks) == 0

    def test_chunk_documents_multiple_documents(self):
        """Test chunking multiple documents."""
        docs = [
            Document(page_content="Content 1. " * 50, metadata={"source": "doc1.txt"}),
            Document(page_content="Content 2. " * 50, metadata={"source": "doc2.txt"}),
        ]
        
        chunks = chunk_documents(docs)
        
        # Check that chunk_ids are unique and correctly formatted
        chunk_ids = [chunk.metadata["chunk_id"] for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))  # All unique
        
        # Check sources are preserved
        sources = set(chunk.metadata["source"] for chunk in chunks)
        assert sources == {"doc1.txt", "doc2.txt"}

    def test_default_chunk_size(self):
        """Test default chunk size constant."""
        assert DEFAULT_CHUNK_SIZE == 500

    def test_default_chunk_overlap(self):
        """Test default chunk overlap constant."""
        assert DEFAULT_CHUNK_OVERLAP == 75