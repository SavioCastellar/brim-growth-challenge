from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.event_model import Event
from app.models.schemas import ScoringOutput, CompanyInput
from app.services import email_generation_service


def test_score_company_endpoint_and_background_task(client: TestClient, mocker):
    """
    Tests that the /api/score-company endpoint in main.py:
    1. Returns a successful response.
    2. Correctly schedules the email generation background task.
    """

    mock_input_data = {"company_name": "API Test Corp", "employee_count": 50}
    mock_score_result = ScoringOutput(
        company_id="test_id_123",
        fit_score=80,
        intent_score=70,
        total_score=76,
        confidence=1.0,
        reasoning={"positive": [], "negative": [], "missing": []},
        action="high_priority",
    )

    mocker.patch(
        "app.main.scoring_service.calculate_scores", return_value=mock_score_result
    )
    mocker.patch("app.main.event_service.log_score_calculated_event")

    mock_add_task = mocker.patch("fastapi.BackgroundTasks.add_task")

    response = client.post("/api/score-company", json=mock_input_data)

    assert response.status_code == 200
    assert response.json()["company_id"] == "test_id_123"

    mock_add_task.assert_called_once()

    args, _ = mock_add_task.call_args
    assert args[0] == email_generation_service.generate_and_save_email_content
    assert args[2].company_name == "API Test Corp"
    assert args[3].total_score == 76


def test_score_company_correctly_logs_event(client: TestClient, mocker):
    """
    Tests that the /api/score-company endpoint correctly calls the
    event logging service as a side effect.
    """

    mock_input_data = {"company_name": "Event Logger Inc.", "employee_count": 75}
    mock_score_result = ScoringOutput(
        company_id="event_test_id_456",
        fit_score=70,
        intent_score=70,
        total_score=70,
        confidence=1.0,
        reasoning={},
        action="medium_priority",
    )

    mocker.patch(
        "app.main.scoring_service.calculate_scores", return_value=mock_score_result
    )

    mock_log_event_func = mocker.patch(
        "app.main.event_service.log_score_calculated_event"
    )

    mocker.patch("fastapi.BackgroundTasks.add_task")

    response = client.post("/api/score-company", json=mock_input_data)

    assert response.status_code == 200

    mock_log_event_func.assert_called_once()

    args, _ = mock_log_event_func.call_args
    assert args[1].total_score == 70
    assert args[2] == "balanced"
    assert args[3].company_name == "Event Logger Inc."


def test_score_company_bad_input(client: TestClient):
    """
    Tests the API response to malformed input (missing required field).
    """
    response = client.post("/api/score-company", json={"employee_count": 100})
    assert response.status_code == 422


def test_get_analytics_kpi_endpoints(client: TestClient, mocker):
    """
    Tests the analytics KPI endpoints to ensure they run without error.
    """

    mocker.patch(
        "app.main.analytics_service.get_qualified_leads_kpi",
        return_value={
            "metric_name": "Test",
            "current_value": 1,
            "percentage_change": 1.0,
            "description": "d",
        },
    )
    mocker.patch("app.main.analytics_service.get_funnel_over_time", return_value=[])

    response_kpi = client.get("/api/analytics/kpi/qualified-leads")
    assert response_kpi.status_code == 200
    assert response_kpi.json()["current_value"] == 1

    response_trend = client.get("/api/analytics/funnel-over-time")
    assert response_trend.status_code == 200
    assert isinstance(response_trend.json(), list)