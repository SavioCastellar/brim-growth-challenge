import json
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.models.event_model import OutboundEmail
from app.services import email_sending_service
from app.services import email_generation_service


def test_send_prioritized_emails_happy_path_and_priority(db_session: Session):
    """
    Test that the email worker sends emails in the correct priority order (highest score first)
    and updates their statuses correctly.
    """
    db_session.add(OutboundEmail(company_id="C001", score=70, is_sent=False))
    db_session.add(OutboundEmail(company_id="C002", score=95, is_sent=False))
    db_session.add(OutboundEmail(company_id="C003", score=50, is_sent=False))
    db_session.commit()

    email_sending_service.send_prioritized_emails(db_session)

    sent_email = db_session.query(OutboundEmail).filter_by(company_id="C002").one()
    assert sent_email.is_sent is True
    assert sent_email.send_attempts == 1

    sent_count = db_session.query(OutboundEmail).filter_by(is_sent=True).count()
    assert sent_count == 3


def test_send_emails_respects_limit(db_session: Session):
    """
    Tests whether the worker respects the limit of 5 emails per cycle.
    """
    for i in range(7):
        db_session.add(OutboundEmail(company_id=f"L{i}", score=80, is_sent=False))
    db_session.commit()

    email_sending_service.send_prioritized_emails(db_session)

    sent_emails = db_session.query(OutboundEmail).filter_by(is_sent=True).count()
    unsent_emails = db_session.query(OutboundEmail).filter_by(is_sent=False).count()

    assert sent_emails == 5
    assert unsent_emails == 2


def test_send_emails_when_queue_is_empty(db_session: Session):
    """
    Tests whether the function executes without errors when there are no emails to be sent.
    """
    email_sending_service.send_prioritized_emails(db_session)


MOCK_GEMINI_RESPONSE_SUCCESS = {
    "variants": [
        {
            "variant_name": "problem_focused",
            "subject": "Painful Workflows?",
            "body": "Is your team bogged down by repetitive tasks?",
        },
        {
            "variant_name": "roi_focused",
            "subject": "Save 10 hours/week",
            "body": "Automate your workflows and improve your ROI.",
        },
    ]
}


def test_generate_and_save_email_happy_path(db_session: Session, mocker):
    """
    Tests email generation in an ideal scenario by mocking the Gemini API call.
    """
    mock_model_instance = MagicMock()

    mock_model_instance.generate_content.return_value = MagicMock(
        text=json.dumps(MOCK_GEMINI_RESPONSE_SUCCESS)
    )

    mocker.patch(
        "google.generativeai.GenerativeModel", return_value=mock_model_instance
    )

    mock_log_event = mocker.patch(
        "app.services.event_service.log_email_generated_event"
    )

    db_provider = lambda: db_session
    email_generation_service.generate_and_save_email_content(
        db_provider, "C123", "TestCorp", 90
    )

    mock_model_instance.generate_content.assert_called_once()
    assert "TestCorp" in mock_model_instance.generate_content.call_args[0][0]

    saved_emails = db_session.query(OutboundEmail).filter_by(company_id="C123").all()
    assert len(saved_emails) == 2

    problem_email = next(e for e in saved_emails if e.variant_name == "problem_focused")
    assert problem_email.email_subject == "Painful Workflows?"
    assert problem_email.score == 90
    assert mock_log_event.call_count == 2


def test_generate_email_handles_invalid_json(db_session: Session, mocker):
    """
    Tests whether the service gracefully handles an API response that is not valid JSON.
    """
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = MagicMock(
        text="<This is not json>"
    )
    mocker.patch(
        "google.generativeai.GenerativeModel", return_value=mock_model_instance
    )

    db_provider = lambda: db_session
    email_generation_service.generate_and_save_email_content(
        db_provider, "C456", "BadJsonCorp", 85
    )

    count = db_session.query(OutboundEmail).filter_by(company_id="C456").count()
    assert count == 0
