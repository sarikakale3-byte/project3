"""Unit tests for app.rag.loaders module."""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document

from app.rag.loaders import load_document, load_knowledge_base, _LOADER_BY_EXTENSION


class TestLoadDocument:
    """Test load_document function."""

    def test_load_document_adds_source_metadata(self):
        """Test that source filename is added to metadata."""
        mock_doc = Document(
            page_content="Test content",
            metadata={}
        )
        
        mock_loader = MagicMock()
        mock_loader.load.return_value = [mock_doc]
        
        with patch.dict(_LOADER_BY_EXTENSION, {".txt": lambda path: mock_loader}):
            with patch("os.path.splitext", return_value=(".txt", ".txt")):
                docs = load_document("/path/to/test.txt")
        
        assert len(docs) == 1
        assert docs[0].metadata["source"] == "test.txt"

    def test_load_document_unsupported_extension(self):
        """Test that unsupported file types raise ValueError."""
        with patch.dict(_LOADER_BY_EXTENSION, {}, clear=True):
            with pytest.raises(ValueError, match="Unsupported document type"):
                load_document("/path/to/file.xyz")

    def test_load_document_preserves_content(self):
        """Test that document content is preserved."""
        mock_doc = Document(
            page_content="Important content here",
            metadata={}
        )
        
        mock_loader = MagicMock()
        mock_loader.load.return_value = [mock_doc]
        
        with patch.dict(_LOADER_BY_EXTENSION, {".txt": lambda path: mock_loader}):
            with patch("os.path.splitext", return_value=(".txt", ".txt")):
                docs = load_document("/path/to/test.txt")
        
        assert docs[0].page_content == "Important content here"


class TestLoadKnowledgeBase:
    """Test load_knowledge_base function."""

    def test_load_knowledge_base_empty_directory(self, tmp_path):
        """Test loading from empty directory."""
        docs = load_knowledge_base(str(tmp_path))
        assert len(docs) == 0

    def test_load_knowledge_base_skips_unsupported_files(self, tmp_path):
        """Test that unsupported files are skipped."""
        # Create unsupported file
        (tmp_path / "unsupported.xyz").write_text("test")
        
        docs = load_knowledge_base(str(tmp_path))
        assert len(docs) == 0

    def test_load_knowledge_base_loads_supported_files(self, tmp_path):
        """Test that supported files are loaded."""
        # Create a mock supported file (using .csv which is in the supported extensions)
        (tmp_path / "test.csv").write_text("test content")
        
        mock_doc = Document(page_content="test content", metadata={})
        
        with patch.object(
            __import__('app.rag.loaders', fromlist=['load_document']),
            'load_document',
            return_value=[mock_doc]
        ) as mock_load:
            docs = load_knowledge_base(str(tmp_path))
        
        assert len(docs) == 1
        mock_load.assert_called_once()

    def test_load_knowledge_base_skips_directories(self, tmp_path):
        """Test that subdirectories are skipped."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file.txt").write_text("test")
        
        docs = load_knowledge_base(str(tmp_path))
        assert len(docs) == 0

    def test_load_knowledge_base_sorted_order(self, tmp_path):
        """Test that files are loaded in sorted order."""
        # Create multiple files (using .csv which is in the supported extensions)
        for name in ["b.csv", "a.csv", "c.csv"]:
            (tmp_path / name).write_text("test")
        
        mock_doc = Document(page_content="test", metadata={})
        
        with patch.object(
            __import__('app.rag.loaders', fromlist=['load_document']),
            'load_document',
            return_value=[mock_doc]
        ) as mock_load:
            docs = load_knowledge_base(str(tmp_path))
        
        # Verify files were called in sorted order
        assert mock_load.call_count == 3
        calls = [call[0][0] for call in mock_load.call_args_list]
        assert calls == sorted(calls)
