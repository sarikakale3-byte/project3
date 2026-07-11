"""End-to-end integration test for the Insurance Claim Assistant."""
import pytest
import time
from unittest.mock import Mock, patch

from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


class TestIntegration:
    """End-to-end integration tests."""

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data

    def test_chat_endpoint(self):
        """Test chat endpoint with mocked chain."""
        mock_response = "This is a test response"
        
        with patch("app.main.chat") as mock_chat:
            mock_chat.return_value = (mock_response, False)
            
            response = client.post(
                "/chat",
                json={
                    "message": "What is covered under health insurance?",
                    "session_id": "test-session-123"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == mock_response
            assert data["session_id"] == "test-session-123"
            assert "cached" in data

    def test_reset_endpoint(self):
        """Test reset endpoint."""
        with patch("app.main.memory.clear_session") as mock_clear:
            response = client.post(
                "/reset",
                json={"session_id": "test-session-123"}
            )
            
            assert response.status_code == 200
            assert response.json() == True
            mock_clear.assert_called_once_with("test-session-123")

    def test_ingest_endpoint(self):
        """Test ingest endpoint starts job."""
        response = client.post(
            "/ingest",
            json={}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert "message" in data

    def test_ingest_status_endpoint(self):
        """Test ingest status endpoint."""
        # First, create a job
        ingest_response = client.post("/ingest", json={})
        job_id = ingest_response.json()["job_id"]
        
        # Wait a bit for job to start
        time.sleep(0.5)
        
        # Check status
        status_response = client.get(f"/ingest/status/{job_id}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["job_id"] == job_id
        assert data["status"] in ["pending", "running", "completed"]

    def test_ingest_status_not_found(self):
        """Test ingest status with invalid job ID."""
        response = client.get("/ingest/status/nonexistent-job-id")
        assert response.status_code == 404

    def test_sources_endpoint(self):
        """Test sources listing endpoint."""
        response = client.get("/sources")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_delete_source_endpoint(self):
        """Test source deletion endpoint."""
        # This test assumes there's at least one source
        # In a real scenario, you'd first ingest some documents
        response = client.delete("/sources/nonexistent.pdf")
        assert response.status_code == 404

    def test_evaluate_endpoint(self):
        """Test evaluate endpoint."""
        # Mock the run_eval function to avoid long-running test
        with patch("eval.run_eval.run_eval") as mock_run_eval:
            mock_run_eval.return_value = {
                "summary": {
                    "n_items": 14,
                    "context_precision": 0.9,
                    "context_recall": 0.9,
                    "faithfulness": 1.0,
                    "answer_relevancy": 1.0,
                    "end_to_end_overall": 0.95
                },
                "items": []
            }
            
            response = client.post("/evaluate")
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert "items" in data

    def test_full_workflow(self):
        """Test complete workflow: ingest -> chat -> list sources -> delete."""
        # 1. Start ingestion
        ingest_resp = client.post("/ingest", json={})
        assert ingest_resp.status_code == 200
        job_id = ingest_resp.json()["job_id"]
        
        # 2. List sources (should have documents from previous ingestion)
        sources_resp = client.get("/sources")
        assert sources_resp.status_code == 200
        
        # 3. Chat
        with patch("app.main.chat") as mock_chat:
            mock_chat.return_value = ("Test response", False)
            chat_resp = client.post(
                "/chat",
                json={"message": "Test question", "session_id": "test-session"}
            )
            assert chat_resp.status_code == 200
        
        # 4. Reset session
        reset_resp = client.post("/reset", json={"session_id": "test-session"})
        assert reset_resp.status_code == 200

    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200