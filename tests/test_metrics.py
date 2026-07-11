"""Unit tests for eval.metrics module."""
import pytest
from unittest.mock import Mock, patch

from eval.metrics import (
    ScoreResult,
    EndToEndJudgment,
    judge_faithfulness,
    judge_answer_relevancy,
    judge_context_precision,
    judge_context_recall,
    judge_end_to_end,
)


class TestScoreResult:
    """Test ScoreResult model."""

    def test_score_result_creation(self):
        """Test creating a ScoreResult."""
        result = ScoreResult(score=0.85, reasoning="Good answer")
        assert result.score == 0.85
        assert result.reasoning == "Good answer"

    def test_score_result_score_range(self):
        """Test that score must be between 0 and 1."""
        with pytest.raises(Exception):  # Pydantic validation error
            ScoreResult(score=1.5, reasoning="Invalid")
        
        with pytest.raises(Exception):
            ScoreResult(score=-0.1, reasoning="Invalid")


class TestEndToEndJudgment:
    """Test EndToEndJudgment model."""

    def test_end_to_end_judgment_creation(self):
        """Test creating an EndToEndJudgment."""
        result = EndToEndJudgment(
            correctness=0.9,
            helpfulness=0.8,
            persona_adherence=0.95,
            safety=1.0,
            reasoning="Good response"
        )
        assert result.correctness == 0.9
        assert result.helpfulness == 0.8
        assert result.persona_adherence == 0.95
        assert result.safety == 1.0

    def test_end_to_end_overall_calculation(self):
        """Test that overall score is calculated correctly."""
        result = EndToEndJudgment(
            correctness=1.0,
            helpfulness=1.0,
            persona_adherence=1.0,
            safety=1.0,
            reasoning="Perfect"
        )
        assert result.overall == 1.0

    def test_end_to_end_overall_average(self):
        """Test that overall is average of four metrics."""
        result = EndToEndJudgment(
            correctness=0.8,
            helpfulness=0.6,
            persona_adherence=1.0,
            safety=0.4,
            reasoning="Mixed"
        )
        expected_overall = round((0.8 + 0.6 + 1.0 + 0.4) / 4, 3)
        assert result.overall == expected_overall


class TestJudgeFunctions:
    """Test judge functions with mocked LLM."""

    @patch('eval.metrics.get_llm')
    def test_judge_faithfulness(self, mock_get_llm):
        """Test judge_faithfulness function."""
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = ScoreResult(
            score=0.9,
            reasoning="Answer is faithful to context"
        )
        mock_get_llm.return_value = mock_llm
        
        result = judge_faithfulness("The answer", ["Context 1", "Context 2"])
        
        assert isinstance(result, ScoreResult)
        assert result.score == 0.9
        mock_llm.with_structured_output.assert_called_once()

    @patch('eval.metrics.get_llm')
    def test_judge_answer_relevancy(self, mock_get_llm):
        """Test judge_answer_relevancy function."""
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = ScoreResult(
            score=1.0,
            reasoning="Answer addresses question"
        )
        mock_get_llm.return_value = mock_llm
        
        result = judge_answer_relevancy("What is X?", "X is Y")
        
        assert isinstance(result, ScoreResult)
        assert result.score == 1.0

    @patch('eval.metrics.get_llm')
    def test_judge_context_precision(self, mock_get_llm):
        """Test judge_context_precision function."""
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = ScoreResult(
            score=0.85,
            reasoning="Good precision"
        )
        mock_get_llm.return_value = mock_llm
        
        result = judge_context_precision("Question", ["Context 1", "Context 2"])
        
        assert isinstance(result, ScoreResult)
        assert result.score == 0.85

    @patch('eval.metrics.get_llm')
    def test_judge_context_recall(self, mock_get_llm):
        """Test judge_context_recall function."""
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = ScoreResult(
            score=0.95,
            reasoning="Good recall"
        )
        mock_get_llm.return_value = mock_llm
        
        result = judge_context_recall("Question", "Ground truth", ["Context 1"])
        
        assert isinstance(result, ScoreResult)
        assert result.score == 0.95

    @patch('eval.metrics.get_llm')
    def test_judge_end_to_end(self, mock_get_llm):
        """Test judge_end_to_end function."""
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value.invoke.return_value = EndToEndJudgment(
            correctness=0.9,
            helpfulness=0.8,
            persona_adherence=0.95,
            safety=1.0,
            reasoning="Good response"
        )
        mock_get_llm.return_value = mock_llm
        
        result = judge_end_to_end("Question", "Ground truth", "Answer")
        
        assert isinstance(result, EndToEndJudgment)
        assert result.correctness == 0.9
        assert result.overall == 0.913  # Average of 0.9, 0.8, 0.95, 1.0 = 0.9125, rounded to 0.913
