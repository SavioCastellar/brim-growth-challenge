import hashlib
from sqlalchemy.orm import Session
from typing import List
import asyncio

from app.models.schemas import CompanyInput, ScoringOutput, ScoringModel
from app.database import SessionLocal
from app.services import event_service, email_generation_service

MODEL_WEIGHTS = {
    "balanced": {"employee_count": 0.2, "industry": 0.3, "tech_stack": 0.5},
    "aggressive": {"employee_count": 0.1, "industry": 0.2, "tech_stack": 0.7},
    "conservative": {"employee_count": 0.4, "industry": 0.4, "tech_stack": 0.2},
}


async def process_batch_scoring(companies: List[CompanyInput]):
    """
    Processes a list of companies by creating its own database session.
    """
    db: Session = SessionLocal()

    print(f"--- BATCH JOB: Starting to process {len(companies)} companies. ---")

    tasks = []
    for company_data in companies:
        try:
            company_input = CompanyInput(**company_data)

            score_result = calculate_scores(company_input, model=ScoringModel.BALANCED)

            event_service.log_score_calculated_event(
                db, score_result, "balanced", company_input
            )

            task = email_generation_service.generate_and_save_email_content(
                lambda: SessionLocal(), company_input, score_result
            )
            tasks.append(task)

        except Exception as e:
            print(
                f"--- BATCH JOB SETUP ERROR: Failed to prepare company. Data: {company_data}. Error: {e} ---"
            )

    print(
        f"--- BATCH JOB: Running {len(tasks)} email generation tasks concurrently... ---"
    )
    await asyncio.gather(*tasks)

    db.close()
    print(f"--- BATCH JOB: Finished processing all tasks. ---")


def calculate_scores(company: CompanyInput, model: ScoringModel) -> ScoringOutput:
    """
    Calculates fit and intent scores for a company based on a defined Ideal Customer Profile.
    """
    fit_score_signals = []
    intent_score_signals = []
    reasons = {"positive": [], "negative": [], "missing": []}

    # --- Fit Score Signals (How well do they match our ICP?) ---

    # 1. Employee Count (Source: firmographics)
    if company.employee_count:
        if 30 <= company.employee_count <= 300:
            fit_score_signals.append(100)
            reasons["positive"].append(f"Ideal company size ({company.employee_count} employees).")
        elif 301 <= company.employee_count <= 500 or 15 <= company.employee_count <= 29:
            fit_score_signals.append(50)
        else:
            fit_score_signals.append(0)
            reasons["negative"].append("Company size is outside target range.")
    else:
        reasons["missing"].append("employee_count")

    # 2. Industry (Source: firmographics)
    ideal_industries = ["saas", "fintech", "ai", "technology"]
    good_industries = ["e-commerce", "biotech", "education"]
    if company.industry:
        if company.industry.lower() in ideal_industries:
            fit_score_signals.append(100)
            reasons["positive"].append(f"Ideal industry: {company.industry}.")
        elif company.industry.lower() in good_industries:
            fit_score_signals.append(60)
    else:
        reasons["missing"].append("industry")

    # --- Intent Score Signals (Are they showing buying signals now?) ---

    # 3. Automation Tech Stack (Source: technographics)
    automation_tools = ["zapier", "make", "workato", "hubspot"]
    if company.tech_stack:
        used_tools = [tool for tool in automation_tools if tool in [t.lower() for t in company.tech_stack]]
        if used_tools:
            intent_score_signals.append(100)
            reasons["positive"].append(f"Uses automation tools: {', '.join(used_tools)}.")
        else:
            intent_score_signals.append(20) # Low score but not zero, as they use some tech
    else:
        reasons["missing"].append("tech_stack")

    # 4. Hiring for Operations (Source: intent signals)
    ops_roles = ["operations", "ops", "automation engineer"]
    if company.recent_job_posts:
        if any(role in post.lower() for post in company.recent_job_posts for role in ops_roles):
            intent_score_signals.append(100)
            reasons["positive"].append("Hiring for operations or automation roles.")
    else:
        reasons["missing"].append("recent_job_posts")

    # --- Final Score Calculation ---

    fit_score = int(sum(fit_score_signals) / len(fit_score_signals)) if fit_score_signals else 0
    intent_score = int(sum(intent_score_signals) / len(intent_score_signals)) if intent_score_signals else 0

    total_score = int((fit_score * 0.6) + (intent_score * 0.4))

    total_fields = len(CompanyInput.__fields__)
    provided_fields = sum(1 for field_name, value in company.dict().items() if value and field_name not in reasons["missing"])
    confidence = round(provided_fields / total_fields, 2)

    if total_score > 80:
        action = "high_priority_outreach"
    elif total_score > 60:
        action = "medium_priority_outreach"
    else:
        action = "low_priority_monitoring"

    company_id = hashlib.sha1(company.company_name.encode()).hexdigest()[:15]

    return ScoringOutput(
        company_id=company_id,
        fit_score=fit_score,
        intent_score=intent_score,
        total_score=total_score,
        confidence=confidence,
        reasoning=reasons,
        action=action
    )
