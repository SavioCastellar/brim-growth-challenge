import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.orm import Session

from app.services import email_generation_service, email_sending_service, event_service
from app.models.schemas import CompanyInput, ScoringOutput, ActivationEventInput
from app.models.event_model import OutboundEmail, Event

MOCK_GEMINI_RESPONSE = {
    "variant_name": "problem_focused",
    "subject": "Mocked Subject for TestCorp",
    "body": "This is the mocked email body.",
}


@pytest.mark.asyncio
async def test_generate_and_save_email_content(db_session: Session, mocker):
    company_data = CompanyInput(
        company_name="TestCorp", employee_count=100, industry="SaaS"
    )
    scoring_data = ScoringOutput(
        company_id="test_company_123",
        total_score=85,
        fit_score=80,
        intent_score=90,
        confidence=0.9,
        reasoning={},
        action="high_priority_outreach",
    )

    mock_api_call = mocker.patch(
        "app.services.email_generation_service.genai.GenerativeModel.generate_content_async",
        new_callable=AsyncMock,
    )
    mock_api_call.return_value.text = json.dumps(MOCK_GEMINI_RESPONSE)
    mock_log_event = mocker.patch(
        "app.services.event_service.log_email_generated_event"
    )

    # ACT
    await email_generation_service.generate_and_save_email_content(
        db_provider=lambda: db_session, company_data=company_data, scoring=scoring_data
    )

    # ASSERT
    mock_api_call.assert_awaited_once()
    saved_email = (
        db_session.query(OutboundEmail).filter_by(company_id="test_company_123").one()
    )
    assert saved_email is not None
    assert saved_email.email_subject == "Mocked Subject for TestCorp"
    assert saved_email.score == 85
    mock_log_event.assert_called_once()


def test_send_prioritized_emails_sends_in_order(db_session: Session):
    db_session.add(
        OutboundEmail(company_id="C001", score=70, is_sent=False, send_attempts=0)
    )
    db_session.add(
        OutboundEmail(company_id="C002", score=95, is_sent=False, send_attempts=0)
    )
    db_session.add(
        OutboundEmail(company_id="C003", score=50, is_sent=False, send_attempts=0)
    )
    db_session.commit()

    email_sending_service.send_prioritized_emails(db=db_session)

    sent_emails = db_session.query(OutboundEmail).filter_by(is_sent=True).all()
    assert len(sent_emails) == 3

    highest_priority_email = (
        db_session.query(OutboundEmail).filter_by(company_id="C002").one()
    )
    assert highest_priority_email.is_sent is True
    assert highest_priority_email.send_attempts == 1


def test_send_emails_respects_limit(db_session: Session):
    for i in range(7):
        db_session.add(
            OutboundEmail(company_id=f"L{i}", score=80, is_sent=False, send_attempts=0)
        )
    db_session.commit()

    # ACT
    email_sending_service.send_prioritized_emails(db=db_session)

    # ASSERT
    sent_emails_count = db_session.query(OutboundEmail).filter_by(is_sent=True).count()
    unsent_emails_count = (
        db_session.query(OutboundEmail).filter_by(is_sent=False).count()
    )

    assert sent_emails_count == 5
    assert unsent_emails_count == 2


def test_send_emails_when_queue_is_empty(db_session: Session):
    try:
        email_sending_service.send_prioritized_emails(db=db_session)
    except Exception as e:
        pytest.fail(
            f"Unexpected Exception: {e}"
        )


@pytest.fixture
def mock_db_session():
    return MagicMock()


def test_log_score_calculated_event(mock_db_session):
    score_output = ScoringOutput(
        company_id="comp-123",
        fit_score=80,
        intent_score=90,
        total_score=85,
        confidence=0.9,
        reasoning={"positive": [], "negative": [], "missing": []},
        action="high_priority_outreach",
    )
    company_input = CompanyInput(
        company_name="Test Corp", employee_count=100, industry="SaaS"
    )

    # ACT
    event_service.log_score_calculated_event(
        mock_db_session, score_output, "v1.0", company_input
    )

    # ASSERT
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

    added_event = mock_db_session.add.call_args[0][0]
    assert isinstance(added_event, Event)
    assert added_event.event_type == "score_calculated"
    assert added_event.company_id == "comp-123"
    assert added_event.event_data["score"] == 85
    assert added_event.event_data["company_name"] == "Test Corp"


def test_log_email_generated_event(mock_db_session):
    email_record = OutboundEmail(company_id="comp-456")

    # ACT
    event_service.log_email_generated_event(mock_db_session, email_record)

    # ASSERT
    mock_db_session.add.assert_called_once()
    added_event = mock_db_session.add.call_args[0][0]
    assert added_event.event_type == "email_generated"


def test_log_activation_event(mock_db_session):
    activation_data = ActivationEventInput(
        user_id="user-789",
        step_name="file_upload",
        metadata={"filename": "test.csv", "size": 1024},
    )

    # ACT
    event_service.log_activation_event(mock_db_session, activation_data)

    # ASSERT
    mock_db_session.add.assert_called_once()
    added_event = mock_db_session.add.call_args[0][0]
    assert added_event.event_type == "activation_step_completed"
    assert added_event.user_id == "user-789"