from app.services import scoring_service
from app.models.schemas import CompanyInput, ScoringModel
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_calculate_scores_happy_path():
    """Testa o cenário ideal com dados completos."""
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
    """Testa se o serviço lida com dados ausentes sem erros."""
    company = CompanyInput(company_name="Empty Corp") # Apenas o campo obrigatório

    # Este teste passa se nenhuma exceção for levantada
    result = scoring_service.calculate_scores(company, ScoringModel.BALANCED)
    assert result.confidence < 0.3
    assert "funding_stage" in result.reasoning["missing"]

def test_different_scoring_models():
    """Testa se os diferentes modelos de pontuação produzem resultados diferentes."""
    company = CompanyInput(
        company_name="Model Test Inc.",
        employee_count=150,
        industry="Technology",
        tech_stack=["AWS", "Slack"]
    )
    balanced_result = scoring_service.calculate_scores(company, ScoringModel.BALANCED)
    aggressive_result = scoring_service.calculate_scores(company, ScoringModel.AGGRESSIVE)

    assert balanced_result.total_score != aggressive_result.total_score