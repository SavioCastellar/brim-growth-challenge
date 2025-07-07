from sqlalchemy.orm import Session
from app.models.event_model import Event, OutboundEmail
from app.models.schemas import ScoringOutput


def log_score_calculated_event(db: Session, score_output: ScoringOutput, model: str):
    """
    Creates and saves a 'score_calculated' event to the database.
    """
    event = Event(
        event_type="score_calculated",
        company_id=score_output.company_id,
        model=model,
        total_score=score_output.total_score,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    print("commit")
    return event


def log_email_generated_event(db: Session, email_record: OutboundEmail):
    """Creates and saves an 'email_generated' event to the database."""
    event = Event(
        event_type="email_generated",
        company_id=email_record.company_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
