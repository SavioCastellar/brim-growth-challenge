from app.models.schemas import CompanyInput, ScoringOutput, ScoringModel
import hashlib

# Define weights for different models as a starting point
MODEL_WEIGHTS = {
    "balanced": {"employee_count": 0.2, "industry": 0.3, "tech_stack": 0.5},
    "aggressive": {"employee_count": 0.1, "industry": 0.2, "tech_stack": 0.7},
    "conservative": {"employee_count": 0.4, "industry": 0.4, "tech_stack": 0.2},
}

def calculate_scores(company: CompanyInput, model: ScoringModel) -> ScoringOutput:
    """Calculates fit, intent, and total scores for a given company."""

    weights = MODEL_WEIGHTS.get(model.value)

    fit_score = 0
    if company.employee_count and 30 <= company.employee_count <= 300:
        fit_score += 100 * weights.get("employee_count", 0.2)

    if company.industry in ["SaaS", "Fintech", "Technology"]:
        fit_score += 100 * weights.get("industry", 0.3)

    intent_score = 0
    if "Zapier" in company.tech_stack or "Salesforce" in company.tech_stack:
        intent_score += 100 * weights.get("tech_stack", 0.5)

    if any("Operations" in post or "Automation" in post for post in company.recent_job_posts):
        intent_score += 100 * weights.get("tech_stack", 0.5)

    fit_score = int(min(fit_score, 100))
    intent_score = int(min(intent_score, 100))
    total_score = int((fit_score * 0.6) + (intent_score * 0.4))

    total_fields = len(CompanyInput.model_fields)
    provided_fields = sum(1 for field in company.dict().values() if field)
    confidence = round(provided_fields / total_fields, 2)

    company_id = hashlib.sha1(company.company_name.encode()).hexdigest()[:15]
    reasoning = {"positive": ["Good industry fit"], "negative": [], "missing": []}
    if not company.funding_stage:
        reasoning["missing"].append("funding_stage")

    return ScoringOutput(
        company_id=company_id,
        fit_score=fit_score,
        intent_score=intent_score,
        total_score=total_score,
        confidence=confidence,
        reasoning=reasoning,
        action="medium_priority_outreach" if total_score < 75 else "high_priority_outreach"
    )