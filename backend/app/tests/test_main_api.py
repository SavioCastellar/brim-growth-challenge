from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.event_model import Event

def test_score_company_endpoint_success(client: TestClient, db_session: Session):
    """
    Tests a successful request to the /api/score-company endpoint.
    """
    response = client.post(
        "/api/score-company?model=aggressive",
        json={"company_name": "API Test Corp", "employee_count": 50}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] is not None
    assert data["total_score"] >= 0

def test_score_company_logs_event(client: TestClient, db_session: Session):
    """
    Tests whether an event is correctly logged to the database after an API call.
    """
    initial_event_count = db_session.query(Event).count()

    client.post(
        "/api/score-company",
        json={"company_name": "Event Logger Inc."}
    )

    final_event_count = db_session.query(Event).count()
    assert final_event_count == initial_event_count + 1

    new_event = db_session.query(Event).order_by(Event.id.desc()).first()
    assert new_event.event_type == "score_calculated"

def test_score_company_bad_input(client: TestClient):
    """
    Tests the API response to malformed input (missing required field).
    """
    response = client.post("/api/score-company", json={"employee_count": 100})
    assert response.status_code == 422