from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from typing import List, Dict

from app.models.event_model import Event, OutboundEmail

def get_lead_score_distribution(db: Session) -> List[Dict[str, any]]:
    """Agrega pontuações de leads em faixas para o histograma."""
    bins = [(0, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 60), (61, 70), (71, 80), (81, 90), (91, 100)]

    score_expression = Event.event_data['score'].as_integer()

    query = db.query(
        *[func.sum(case((score_expression.between(low, high), 1), else_=0)).label(f"{low}-{high}") for low, high in bins]
    ).filter(Event.event_type == 'score_calculated')

    counts = query.one()

    distribution = [{"bin": label, "count": count or 0} for label, count in zip([f"{l}-{h}" for l,h in bins], counts)]
    return distribution

def get_top_leads(db: Session, limit: int = 5) -> List[Dict[str, any]]:
    """Retorna os top N leads com base na pontuação mais recente."""
    latest_event_subquery = db.query(
        func.max(Event.id).label("max_id")
    ).filter(
        Event.event_type == 'score_calculated'
    ).group_by(Event.company_id).subquery()

    top_events = db.query(Event).join(
        latest_event_subquery, Event.id == latest_event_subquery.c.max_id
    ).order_by(
        Event.event_data['score'].as_integer().desc()
    ).limit(limit).all()

    top_leads = [{
        "company_id": event.company_id,
        "company_name": event.event_data.get("company_name", "N/A"),
        "score": event.event_data.get("score")
    } for event in top_events]

    return top_leads

def get_activation_funnel(db: Session) -> List[Dict[str, any]]:
    """Calcula a contagem de usuários únicos para cada passo do funil de ativação."""
    step_expression = Event.event_data['step'].as_string()

    query_result = db.query(
        step_expression,
        func.count(distinct(Event.user_id))
    ).filter(
        Event.event_type == 'activation_step_completed'
    ).group_by(
        step_expression
    ).all()

    step_order = ['file_upload', 'result_viewed', 'share_step_reached']
    result_dict = {step: count for step, count in query_result}

    funnel_data = [{"step_name": step, "user_count": result_dict.get(step, 0)} for step in step_order]
    return funnel_data

def get_email_performance(db: Session) -> List[Dict[str, any]]:
    """Conta o número de e-mails gerados para cada variante."""
    query_result = db.query(
        OutboundEmail.variant_name,
        func.count(OutboundEmail.id)
    ).group_by(OutboundEmail.variant_name).all()

    performance_data = [{"variant_name": variant, "count": count} for variant, count in query_result]
    return performance_data