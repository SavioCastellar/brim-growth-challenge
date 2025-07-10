from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct, and_, select, text
from typing import List, Dict
from datetime import date, timedelta
import random
from collections import defaultdict

from app.models.event_model import Event, OutboundEmail


def get_lead_score_distribution(db: Session) -> List[Dict[str, any]]:
    bins = [
        (0, 10),
        (11, 20),
        (21, 30),
        (31, 40),
        (41, 50),
        (51, 60),
        (61, 70),
        (71, 80),
        (81, 90),
        (91, 100),
    ]

    score_expression = Event.event_data["score"].as_integer()

    print(f"Score Expression: {score_expression}")

    query = db.query(
        *[
            func.sum(case((score_expression.between(low, high), 1), else_=0)).label(
                f"{low}-{high}"
            )
            for low, high in bins
        ]
    ).filter(Event.event_type == "score_calculated")

    counts = query.one()

    distribution = [
        {"bin": label, "count": count or 0}
        for label, count in zip([f"{l}-{h}" for l, h in bins], counts)
    ]
    return distribution


def get_top_leads(db: Session, limit: int = 5) -> List[Dict[str, any]]:
    latest_event_subquery = (
        db.query(func.max(Event.id).label("max_id"))
        .filter(Event.event_type == "score_calculated")
        .group_by(Event.company_id)
        .subquery()
    )

    top_events = (
        db.query(Event)
        .join(latest_event_subquery, Event.id == latest_event_subquery.c.max_id)
        .order_by(Event.event_data["score"].as_integer().desc())
        .limit(limit)
        .all()
    )

    top_leads = [
        {
            "company_id": event.company_id,
            "company_name": event.event_data.get("company_name", "N/A"),
            "score": event.event_data.get("score"),
        }
        for event in top_events
    ]

    return top_leads


def get_activation_funnel(db: Session) -> List[Dict[str, any]]:
    step_expression = Event.event_data["step"].as_string()

    query_result = (
        db.query(step_expression, func.count(distinct(Event.user_id)))
        .filter(Event.event_type == "activation_step_completed")
        .group_by(step_expression)
        .all()
    )

    step_order = ["file_upload", "result_viewed", "share_step_reached"]
    result_dict = {step: count for step, count in query_result}

    funnel_data = [
        {"step_name": step, "user_count": result_dict.get(step, 0)}
        for step in step_order
    ]
    return funnel_data


def get_email_performance(db: Session) -> List[Dict[str, any]]:
    query_result = (
        db.query(OutboundEmail.variant_name, func.count(OutboundEmail.id))
        .group_by(OutboundEmail.variant_name)
        .all()
    )

    performance_data = [
        {"variant_name": variant, "count": count} for variant, count in query_result
    ]
    return performance_data


def get_qualified_leads_kpi(db: Session, start_date: date, end_date: date) -> dict:
    """
    Calculates the number of qualified leads (score > 75) for a given period
    and compares it to the previous period.
    """
    period_duration_days = (end_date - start_date).days + 1
    previous_start_date = start_date - timedelta(days=period_duration_days)
    previous_end_date = start_date - timedelta(days=1)  # FIX: End one day before

    score_threshold = 75
    score_expression = Event.event_data["score"].as_integer()

    print(f"Current period: {start_date} to {end_date}")

    current_period_count = (
        db.query(func.count(distinct(Event.company_id)))
        .filter(
            and_(
                Event.event_type == "score_calculated",
                Event.timestamp.between(start_date, end_date),
                score_expression > score_threshold,
            )
        )
        .scalar()
        or 0
    )

    print(f"Current Period Count: {current_period_count}")

    previous_period_count = (
        db.query(func.count(distinct(Event.company_id)))
        .filter(
            and_(
                Event.event_type == "score_calculated",
                Event.timestamp.between(previous_start_date, previous_end_date),
                score_expression > score_threshold,
            )
        )
        .scalar()
        or 0
    )

    if previous_period_count > 0:
        percentage_change = (
            (current_period_count - previous_period_count) / previous_period_count
        ) * 100
    elif current_period_count > 0:
        percentage_change = 100.0
    else:
        percentage_change = 0.0

    return {
        "metric_name": "Qualified Leads",
        "current_value": current_period_count,
        "percentage_change": round(percentage_change, 2),
        "description": f"Leads with score > {score_threshold}",
    }


def get_email_engagement_kpi(db: Session, start_date: date, end_date: date) -> dict:
    """
    Calculates a simulated Click-Through Rate (CTR) for sent emails based on lead score.
    """

    def _simulate_clicks(emails):
        clicks = 0
        for email in emails:
            click_probability = (email.score or 0) / 150.0
            if email.variant_name == "roi_focused":
                click_probability *= 1.2

            if random.random() < click_probability:
                clicks += 1
        return clicks

    period_duration_days = (end_date - start_date).days + 1
    previous_start_date = start_date - timedelta(days=period_duration_days)
    previous_end_date = start_date - timedelta(days=1)

    current_period_emails = (
        db.query(OutboundEmail)
        .filter(
            and_(
                OutboundEmail.is_sent == True,
                OutboundEmail.created_at.between(start_date, end_date),
            )
        )
        .all()
    )

    previous_period_emails = (
        db.query(OutboundEmail)
        .filter(
            and_(
                OutboundEmail.is_sent == True,
                OutboundEmail.created_at.between(
                    previous_start_date, previous_end_date
                ),
            )
        )
        .all()
    )

    current_period_clicks = _simulate_clicks(current_period_emails)
    previous_period_clicks = _simulate_clicks(previous_period_emails)

    current_ctr = (
        (current_period_clicks / len(current_period_emails) * 100)
        if current_period_emails
        else 0
    )
    previous_ctr = (
        (previous_period_clicks / len(previous_period_emails) * 100)
        if previous_period_emails
        else 0
    )

    if previous_ctr > 0:
        percentage_change = ((current_ctr - previous_ctr) / previous_ctr) * 100
    elif current_ctr > 0:
        percentage_change = 100.0
    else:
        percentage_change = 0.0

    return {
        "metric_name": "Email Click-Through Rate (Simulated)",
        "current_value": round(current_ctr, 2),
        "percentage_change": round(percentage_change, 2),
        "description": "Based on lead score and A/B variant",
    }


def get_new_activations_kpi(db: Session, start_date: date, end_date: date) -> dict:
    """
    Calculates the number of unique users who were activated (viewed results)
    and compares it to the previous period.
    """
    period_duration_days = (end_date - start_date).days + 1
    previous_start_date = start_date - timedelta(days=period_duration_days)
    previous_end_date = start_date - timedelta(days=1)

    def _count_activations(start: date, end: date) -> int:
        count = (
            db.query(func.count(distinct(Event.user_id)))
            .filter(
                and_(
                    Event.event_type == "activation_step_completed",
                    Event.event_data["step"].as_string() == "result_viewed",
                    Event.timestamp.between(start, end),
                )
            )
            .scalar()
        )
        return count or 0

    current_period_count = _count_activations(start_date, end_date)
    previous_period_count = _count_activations(previous_start_date, previous_end_date)

    if previous_period_count > 0:
        percentage_change = (
            (current_period_count - previous_period_count) / previous_period_count
        ) * 100
    elif current_period_count > 0:
        percentage_change = 100.0
    else:
        percentage_change = 0.0

    return {
        "metric_name": "New Activations",
        "current_value": current_period_count,
        "percentage_change": round(percentage_change, 2),
        "description": "Unique users who tested our solution",
    }


def get_funnel_conversion_rate_kpi(
    db: Session, start_date: date, end_date: date
) -> dict:
    """
    Calculates the funnel conversion rate from qualified lead to activated user.
    """
    score_threshold = 75
    score_expression = Event.event_data["score"].as_integer()

    def _get_counts(start: date, end: date) -> (int, int):
        leads_count = (
            db.query(func.count(distinct(Event.company_id)))
            .filter(
                and_(
                    Event.event_type == "score_calculated",
                    Event.timestamp.between(start, end),
                    score_expression > score_threshold,
                )
            )
            .scalar()
            or 0
        )

        activations_count = (
            db.query(func.count(distinct(Event.user_id)))
            .filter(
                and_(
                    Event.event_type == "activation_step_completed",
                    Event.event_data["step"].as_string() == "result_viewed",
                    Event.timestamp.between(start, end),
                )
            )
            .scalar()
            or 0
        )

        return leads_count, activations_count

    period_duration_days = (end_date - start_date).days + 1
    previous_start_date = start_date - timedelta(days=period_duration_days)
    previous_end_date = start_date - timedelta(days=1)

    current_leads, current_activations = _get_counts(start_date, end_date)
    previous_leads, previous_activations = _get_counts(
        previous_start_date, previous_end_date
    )

    print(f"Current Leads: {current_leads}, Current Activations: {current_activations}")

    current_conversion_rate = (
        (current_activations / current_leads * 100) if current_leads > 0 else 0
    )
    previous_conversion_rate = (
        (previous_activations / previous_leads * 100) if previous_leads > 0 else 0
    )

    if previous_conversion_rate > 0:
        percentage_change = (
            (current_conversion_rate - previous_conversion_rate)
            / previous_conversion_rate
        ) * 100
    elif current_conversion_rate > 0:
        percentage_change = 100.0
    else:
        percentage_change = 0.0

    subquery_qualified = (
        db.query(
            Event.company_id.label("company_id"),
            func.min(Event.timestamp).label("qualified_at"),
        )
        .filter(
            and_(
                Event.event_type == "score_calculated",
                Event.timestamp.between(start_date, end_date),
                score_expression > score_threshold,
            )
        )
        .group_by(Event.company_id)
        .subquery()
    )

    subquery_activated = (
        db.query(
            Event.company_id.label("company_id"),
            func.min(Event.timestamp).label("activated_at"),
        )
        .filter(
            and_(
                Event.event_type == "activation_step_completed",
                Event.event_data["step"].as_string() == "result_viewed",
                Event.timestamp.between(start_date, end_date),
            )
        )
        .group_by(Event.company_id)
        .subquery()
    )

    joined_query = (
        db.query(
            subquery_qualified.c.qualified_at,
            subquery_activated.c.activated_at,
        )
        .join(
            subquery_activated,
            subquery_qualified.c.company_id == subquery_activated.c.company_id,
        )
        .filter(subquery_activated.c.activated_at > subquery_qualified.c.qualified_at)
        .all()
    )

    if joined_query:
        durations = [
            (activation.activated_at - activation.qualified_at).days
            for activation in joined_query
        ]
        avg_time_to_convert = sum(durations) / len(durations)
    else:
        avg_time_to_convert = 0.0

    return {
        "metric_name": "Funnel Conversion Rate",
        "current_value": round(current_conversion_rate, 2),
        "percentage_change": round(percentage_change, 2),
        "description": f"Avg. {avg_time_to_convert} days from qualified to activated",
    }


def get_funnel_over_time(
    db: Session, start_date: date, end_date: date
) -> List[Dict[str, any]]:
    """
    Fetches daily counts for qualified leads and activations using Python-based date handling.
    """

    print(f"Fetching funnel data from {start_date} to {end_date}")

    date_range = [
        start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)
    ]

    score_threshold = 75

    lead_events = (
        db.query(func.date(Event.timestamp).label("day"), Event.company_id)
        .filter(
            Event.event_type == "score_calculated",
            Event.event_data["score"].as_integer() > score_threshold,
            Event.timestamp.between(start_date, end_date),
        )
        .all()
    )

    activation_events = (
        db.query(func.date(Event.timestamp).label("day"), Event.user_id)
        .filter(
            Event.event_type == "activation_step_completed",
            Event.event_data["step"].as_string() == "result_viewed",
            Event.timestamp.between(start_date, end_date),
        )
        .all()
    )

    leads_by_day = defaultdict(set)
    for day, company_id in lead_events:
        leads_by_day[day].add(company_id)

    activations_by_day = defaultdict(set)
    for day, user_id in activation_events:
        activations_by_day[day].add(user_id)

    formatted_results = []
    for day_object in date_range:
        date_key_string = day_object.strftime("%Y-%m-%d")
        formatted_results.append(
            {
                "date": date_key_string,
                "qualified_leads": len(leads_by_day.get(date_key_string, set())),
                "activations": len(activations_by_day.get(date_key_string, set())),
            }
        )

    return formatted_results


def get_scored_leads_table_data(db: Session) -> List[Dict[str, any]]:
    """
    Prepares data for the scored leads data table, combining scoring and email status info.
    """

    latest_score_cte = (
        db.query(Event.company_id, func.max(Event.id).label("max_id"))
        .filter(Event.event_type == "score_calculated")
        .group_by(Event.company_id)
        .cte("latest_score_cte")
    )

    sent_email_cte = (
        db.query(OutboundEmail.company_id, OutboundEmail.variant_name)
        .filter(OutboundEmail.is_sent == True)
        .cte("sent_email_cte")
    )

    results = (
        db.query(
            Event.company_id,
            Event.event_data["company_name"].as_string().label("company_name"),
            Event.event_data["score"].as_integer().label("score"),
            sent_email_cte.c.variant_name.label("email_variant_sent"),
        )
        .join(latest_score_cte, Event.id == latest_score_cte.c.max_id)
        .outerjoin(sent_email_cte, Event.company_id == sent_email_cte.c.company_id)
        .order_by(Event.event_data["score"].as_integer().desc())
        .all()
    )

    table_data = [
        {
            "company_id": r.company_id,
            "company_name": r.company_name,
            "score": r.score,
            "status": "Sent" if r.email_variant_sent else "Pending",
            "email_variant_sent": r.email_variant_sent,
        }
        for r in results
    ]

    return table_data