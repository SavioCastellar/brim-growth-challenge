from app.services import scoring_service
from app.models.schemas import CompanyInput, ScoringModel
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_calculate_scores_happy_path():
    """
    Test the ideal scenario with complete data.
    """
    company = CompanyInput(
        company_name="Test Corp",
        employee_count=100,
        industry="SaaS",
        tech_stack=["Zapier"],
        recent_job_posts=["Automation Engineer"]
    )
    result = scoring_service.calculate_scores(company, ScoringModel.BALANCED)
    assert result.total_score > 50
    assert result.confidence > 0.5

def test_calculate_scores_with_missing_data():
    """
    Tests whether the service handles missing data without errors.
    """
    company = CompanyInput(company_name="Empty Corp")

    result = scoring_service.calculate_scores(company, ScoringModel.BALANCED)
    assert result.confidence < 0.3
    assert "funding_stage" in result.reasoning["missing"]

def test_different_scoring_models():
    """
    Tests whether different scoring models produce different results.
    """
    company = CompanyInput(
        company_name="Model Test Inc.",
        employee_count=150,
        industry="Technology",
        tech_stack=["AWS", "Slack"]
    )
    balanced_result = scoring_service.calculate_scores(company, ScoringModel.BALANCED)
    aggressive_result = scoring_service.calculate_scores(company, ScoringModel.AGGRESSIVE)

    assert balanced_result.total_score != aggressive_result.total_score