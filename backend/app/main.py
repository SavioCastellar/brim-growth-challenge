import logging
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

from app.models.schemas import CompanyInput, ScoringOutput, ScoringModel
from app.services import scoring_service, event_service, email_generation_service
from app.database import engine, get_db
from app.models import event_model
from app.database import SessionLocal
from app.services import email_sending_service

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
    """
    Receives company data, returns score and logs the event.
    """
    try:
        score_result = scoring_service.calculate_scores(company_input, model)
        event_service.log_score_calculated_event(db, score_result, model.value)

        background_tasks.add_task(
            email_generation_service.generate_and_save_email_content,
            SessionLocal,
            score_result.company_id,
            company_input.company_name,
            score_result.total_score,
        )

        return score_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


def run_email_worker_cycle():
    """
    Creates a DB session, runs the email sending worker, and ensures the session is closed.
    This is the function that the scheduler will call periodically.
    """
    db = SessionLocal()
    try:
        email_sending_service.send_prioritized_emails(db)
    finally:
        db.close()
