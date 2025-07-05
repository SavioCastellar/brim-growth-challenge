from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True, nullable=False)
    company_id = Column(String, index=True, nullable=False)
    model = Column(String)
    total_score = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())