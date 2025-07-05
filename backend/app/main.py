from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.schemas import CompanyInput, ScoringOutput, ScoringModel
from app.services import scoring_service, event_service
from app.database import engine, get_db
from app.models import event_model

event_model.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Brim Growth Challenge API")

@app.get("/")
def read_root():
    return {"message": "Brim Growth Engineering Challenge API is running!"}

@app.post("/api/score-company", response_model=ScoringOutput, tags=["Scoring"])
def score_company(
    company_input: CompanyInput,
    model: ScoringModel = ScoringModel.BALANCED,
    db: Session = Depends(get_db)
):
    """
    Receives company data, returns score and logs the event.
    """
    try:
        score_result = scoring_service.calculate_scores(company_input, model)
        event_service.log_score_calculated_event(db, score_result, model.value)
        return score_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))