"""Unit tests for app.rag.embeddings module."""
import pytest
from unittest.mock import Mock, patch

from app.rag.embeddings import get_embeddings


class TestGetEmbeddings:
    """Test get_embeddings function."""

    @patch('app.rag.embeddings.OpenAIEmbeddings')
    def test_get_embeddings_returns_openai_instance(self, mock_openai_embeddings):
        """Test that get_embeddings returns OpenAIEmbeddings instance."""
        mock_instance = Mock()
        mock_openai_embeddings.return_value = mock_instance
        
        result = get_embeddings()
        
        assert result == mock_instance
        mock_openai_embeddings.assert_called_once()

    @patch('app.rag.embeddings.OpenAIEmbeddings')
    def test_get_embeddings_with_custom_model(self, mock_openai_embeddings):
        """Test get_embeddings with custom model name."""
        mock_instance = Mock()
        mock_openai_embeddings.return_value = mock_instance
        
        with patch.dict('os.environ', {'EMBEDDING_MODEL': 'text-embedding-3-small'}):
            result = get_embeddings()
        
        assert result == mock_instance
        mock_openai_embeddings.assert_called_once()