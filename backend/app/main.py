import logging
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    BackgroundTasks,
    Query,
    UploadFile,
    File,
)
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from typing import List
from datetime import date, timedelta
import json

from app.models.schemas import (
    CompanyInput,
    ScoringOutput,
    ScoringModel,
    ActivationEventInput,
    ScoreDistributionItem,
    TopLeadItem,
    FunnelStep,
    EmailPerformanceItem,
    KpiCardData,
    FunnelTrendItem,
    ScoredLeadData,
)
from app.services import (
    scoring_service,
    event_service,
    email_generation_service,
    email_sending_service,
    analytics_service,
)
from app.database import engine, get_db, SessionLocal
from app.models import event_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

event_model.Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(run_email_worker_cycle, "interval", minutes=1)
    scheduler.start()
    print("Scheduler started...")
    yield
    print("Scheduler shutting down...")
    scheduler.shutdown()


app = FastAPI(title="Brim Growth Challenge API", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Brim Growth Engineering Challenge API is running!"}


@app.post("/api/score-company", response_model=ScoringOutput, tags=["Scoring"])
def score_company(
    company_input: CompanyInput,
    background_tasks: BackgroundTasks,
    model: ScoringModel = ScoringModel.BALANCED,
    db: Session = Depends(get_db),
):
    """Receives company data, returns score and logs the event."""
    try:
        score_result = scoring_service.calculate_scores(company_input, model)
        event_service.log_score_calculated_event(
            db, score_result, model.value, company_input
        )

        background_tasks.add_task(
            email_generation_service.generate_and_save_email_content,
            SessionLocal,
            company_input,
            score_result,
        )

        return score_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


def run_email_worker_cycle():
    """Creates a DB session, runs the email sending worker, and ensures the session is closed.
    This is the function that the scheduler will call periodically."""
    db = SessionLocal()
    try:
        email_sending_service.send_prioritized_emails(db)
    finally:
        db.close()


@app.post("/api/activation/log-event", status_code=201, tags=["Activation"])
def log_event_from_frontend(
    event_input: ActivationEventInput, db: Session = Depends(get_db)
):
    """Receives and registers an event from the activation flow."""
    event_service.log_activation_event(db, event_data=event_input)
    return {"message": "Event logged successfully"}


def get_tomorrow() -> date:
    return date.today() + timedelta(days=1)


@app.get(
    "/api/analytics/kpi/qualified-leads",
    response_model=KpiCardData,
    tags=["Analytics KPI"],
)
def get_qualified_leads_kpi_route(
    end_date: date = Query(default_factory=get_tomorrow),
    days: int = Query(default=30, ge=1),
    db: Session = Depends(get_db),
):
    """
    Provides KPI data for the number of qualified leads.
    Compares the last 'days' with the period immediately preceding it.
    """
    start_date = end_date - timedelta(days=days)
    return analytics_service.get_qualified_leads_kpi(
        db, start_date=start_date, end_date=end_date
    )


@app.get(
    "/api/analytics/kpi/email-engagement",
    response_model=KpiCardData,
    tags=["Analytics KPI"],
)
def get_email_engagement_kpi_route(
    end_date: date = Query(default_factory=get_tomorrow),
    days: int = Query(default=30, ge=1),
    db: Session = Depends(get_db),
):
    """
    Provides KPI data for simulated email engagement (CTR).
    """
    start_date = end_date - timedelta(days=days)
    return analytics_service.get_email_engagement_kpi(
        db, start_date=start_date, end_date=end_date
    )


@app.get(
    "/api/analytics/kpi/new-activations",
    response_model=KpiCardData,
    tags=["Analytics KPI"],
)
def get_new_activations_kpi_route(
    end_date: date = Query(default_factory=get_tomorrow),
    days: int = Query(default=30, ge=1),
    db: Session = Depends(get_db),
):
    """
    Provides KPI data for new user activations.
    """
    start_date = end_date - timedelta(days=days)
    return analytics_service.get_new_activations_kpi(
        db, start_date=start_date, end_date=end_date
    )


@app.get(
    "/api/analytics/kpi/funnel-conversion-rate",
    response_model=KpiCardData,
    tags=["Analytics KPI"],
)
def get_funnel_conversion_rate_kpi_route(
    end_date: date = Query(default_factory=get_tomorrow),
    days: int = Query(default=30, ge=1),
    db: Session = Depends(get_db),
):
    """
    Provides KPI data for the main funnel conversion rate (lead->activation).
    """
    start_date = end_date - timedelta(days=days)
    return analytics_service.get_funnel_conversion_rate_kpi(
        db, start_date=start_date, end_date=end_date
    )


@app.get(
    "/api/analytics/funnel-over-time",
    response_model=List[FunnelTrendItem],
    tags=["Analytics"],
)
def get_funnel_over_time_route(
    end_date: date = Query(default_factory=get_tomorrow),
    days: int = Query(default=30, ge=1),
    db: Session = Depends(get_db),
):
    """
    Provides time-series data for key funnel metrics.
    """
    start_date = end_date - timedelta(days=days)
    return analytics_service.get_funnel_over_time(
        db, start_date=start_date, end_date=end_date
    )


@app.get(
    "/api/analytics/scored-leads-table",
    response_model=List[ScoredLeadData],
    tags=["Analytics"],
)
def get_scored_leads_table_route(db: Session = Depends(get_db)):
    """
    Provides data for the main table of scored leads.
    """
    return analytics_service.get_scored_leads_table_data(db)


@app.post("/api/leads/batch-score", status_code=202, tags=["Leads"])
async def batch_score_leads(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Accepts a JSON file with a list of companies, and scores them
    asynchronously in the background.
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a JSON file."
        )

    contents = await file.read()
    try:
        companies_data = json.loads(contents)
        if not isinstance(companies_data, list):
            raise ValueError("JSON must be a list of company objects.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")

    background_tasks.add_task(scoring_service.process_batch_scoring, companies_data)

    return {
        "message": f"Accepted. Started scoring for {len(companies_data)} companies in the background."
    }
