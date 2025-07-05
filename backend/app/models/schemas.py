from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class ScoringModel(str, Enum):
    """Enum for the different scoring models available."""
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"

class CompanyInput(BaseModel):
    """Defines the structure for the company data input."""
    company_name: str
    employee_count: Optional[int] = None
    industry: Optional[str] = None
    funding_stage: Optional[str] = None
    tech_stack: Optional[List[str]] = []
    recent_job_posts: Optional[List[str]] = []
    news_mentions: Optional[List[str]] = []

class ScoringOutput(BaseModel):
    """Defines the structure for the scoring API response."""
    company_id: str
    fit_score: int = Field(..., ge=0, le=100)
    intent_score: int = Field(..., ge=0, le=100)
    total_score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    reasoning: Dict[str, List[str]]
    action: str