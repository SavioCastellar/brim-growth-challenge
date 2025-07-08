from sqlalchemy.orm import Session
from app.models.event_model import Event, OutboundEmail
from app.models.schemas import ScoringOutput, ActivationEventInput, CompanyInput


def log_score_calculated_event(db: Session, score_output: ScoringOutput, model: str, company_input: CompanyInput):
    """Creates and saves a 'score_calculated' event to the database."""
    event = Event(
        event_type="score_calculated",
        company_id=score_output.company_id,
        event_data={
            "model_used": model,
            "score": score_output.total_score,
            "company_name": company_input.company_name
        }
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


def log_activation_event(db: Session, event_data: ActivationEventInput):
    """Creates and saves an activation event to the database."""
    new_event = Event(
        event_type="activation_step_completed",
        user_id=event_data.user_id,
        event_data={
            "step": event_data.step_name,
            **(event_data.metadata or {})
        }
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    print(f"Activation event registered: {event_data.step_name} for user: {event_data.user_id}")
    return new_event