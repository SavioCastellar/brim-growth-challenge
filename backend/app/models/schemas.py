﻿from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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


class ActivationEventInput(BaseModel):
    user_id: str
    step_name: str
    metadata: Optional[Dict[str, Any]] = None


class ScoreDistributionItem(BaseModel):
    bin: str
    count: int


class TopLeadItem(BaseModel):
    company_id: str
    company_name: str
    score: int


class FunnelStep(BaseModel):
    step_name: str
    user_count: int


class EmailPerformanceItem(BaseModel):
    variant_name: str
    count: int


class KpiCardData(BaseModel):
    metric_name: str
    current_value: float
    percentage_change: float
    description: str


class FunnelTrendItem(BaseModel):
    date: str
    qualified_leads: int
    activations: int


class ScoredLeadData(BaseModel):
    company_id: str
    company_name: str
    status: str
    email_variant_sent: Optional[str] = None
    score: int
