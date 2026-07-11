"""Unit tests for eval.dataset module."""
import pytest

from eval.dataset import EVAL_DATASET


class TestEvalDataset:
    """Test EVAL_DATASET structure and content."""

    def test_dataset_not_empty(self):
        """Test that dataset has items."""
        assert len(EVAL_DATASET) > 0

    def test_dataset_has_required_fields(self):
        """Test that each item has required fields."""
        required_fields = ["id", "category", "question", "ground_truth", "expected_source"]
        
        for item in EVAL_DATASET:
            for field in required_fields:
                assert field in item, f"Missing field '{field}' in item {item.get('id', 'unknown')}"

    def test_dataset_ids_unique(self):
        """Test that all item IDs are unique."""
        ids = [item["id"] for item in EVAL_DATASET]
        assert len(ids) == len(set(ids))

    def test_dataset_categories_valid(self):
        """Test that categories are from valid set."""
        valid_categories = {
            "claim_status", "claim_submission", "document_request",
            "policy_coverage", "claim_rejection", "reimbursement_query",
            "complaint", "general_faq"
        }
        
        for item in EVAL_DATASET:
            assert item["category"] in valid_categories, \
                f"Invalid category '{item['category']}' in item {item['id']}"

    def test_dataset_questions_not_empty(self):
        """Test that questions are not empty."""
        for item in EVAL_DATASET:
            assert len(item["question"]) > 0
            assert len(item["question"]) <= 2000  # Reasonable max length

    def test_dataset_ground_truth_not_empty(self):
        """Test that ground truth answers are not empty."""
        for item in EVAL_DATASET:
            assert len(item["ground_truth"]) > 0

    def test_dataset_expected_source_not_empty(self):
        """Test that expected sources are not empty."""
        for item in EVAL_DATASET:
            assert len(item["expected_source"]) > 0

    def test_dataset_coverage_all_categories(self):
        """Test that dataset covers multiple categories."""
        categories = set(item["category"] for item in EVAL_DATASET)
        assert len(categories) >= 3, "Dataset should cover at least 3 categories"