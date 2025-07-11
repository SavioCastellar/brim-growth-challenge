from app.services import scoring_service
from app.models.schemas import CompanyInput, ScoringModel


def test_calculates_high_score_for_ideal_company():
    """
    Tests that a company matching the Ideal Customer Profile (ICP) gets a high score.
    """

    company = CompanyInput(
        company_name="Perfect Fit Inc.",
        employee_count=150,
        industry="SaaS",
        tech_stack=["Zapier", "Salesforce"],
        recent_job_posts=["Head of Operations"],
    )

    result = scoring_service.calculate_scores(company, ScoringModel.BALANCED)

    assert result.total_score > 80

    positive_reasons_text = " | ".join(result.reasoning["positive"])

    assert "Ideal company size" in positive_reasons_text
    assert "Ideal industry" in positive_reasons_text
    assert "Uses automation tools" in positive_reasons_text
    assert "Hiring for operations" in positive_reasons_text


def test_calculates_low_score_for_bad_fit_company():
    """
    Tests that a company not matching the ICP gets a low score.
    """

    company = CompanyInput(
        company_name="Bad Fit LLC",
        employee_count=1000,
        industry="Government",
    )

    result = scoring_service.calculate_scores(company, ScoringModel.BALANCED)

    assert result.total_score < 40
    assert "Company size is outside target range." in result.reasoning["negative"]


def test_handles_missing_data_gracefully():
    """
    Tests that the service handles missing data without errors and correctly identifies it.
    """

    company = CompanyInput(company_name="Missing Data Corp")

    # ACT: Calculate the score
    result = scoring_service.calculate_scores(company, ScoringModel.BALANCED)

    assert result.confidence < 0.3
    assert "employee_count" in result.reasoning["missing"]
    assert "industry" in result.reasoning["missing"]