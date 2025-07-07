from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, func
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True, nullable=False)
    company_id = Column(String, index=True, nullable=False)
    model = Column(String)
    total_score = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class OutboundEmail(Base):
    __tablename__ = "outbound_emails"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, index=True, nullable=False)
    score = Column(Integer, index=True)

    email_subject = Column(Text)
    email_body = Column(Text)
    variant_name = Column(String, default="problem_focused")

    is_sent = Column(Boolean, default=False)
    send_attempts = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_attempt_at = Column(DateTime(timezone=True), onupdate=func.now())