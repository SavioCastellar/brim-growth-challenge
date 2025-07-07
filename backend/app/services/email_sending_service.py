from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.event_model import OutboundEmail
from . import event_service

def send_prioritized_emails(db: Session):
    """
    Fetches and "sends" emails from the queue, prioritizing by highest score.
    This function will be called periodically by the scheduler.
    """
    print("--- EMAIL WORKER: Verifying emails to send. ---")

    emails_to_send = db.query(OutboundEmail).filter(
        OutboundEmail.is_sent == False
    ).order_by(OutboundEmail.score.desc()).limit(5).all()

    if not emails_to_send:
        print("--- EMAIL WORKER: No companies in the queue. ---")
        return

    for email in emails_to_send:
        print(f"--- EMAIL WORKER: Sending email to {email.company_id}, Variant: {email.variant_name} ---")
        email.is_sent = True
        email.send_attempts += 1

    db.commit()
    print(f"--- EMAIL WORKER: Cycle finished. {len(emails_to_send)} emails sent. ---")