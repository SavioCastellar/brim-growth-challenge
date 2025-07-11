import pytest
from unittest.mock import MagicMock
from datetime import date, timedelta
import random
from collections import namedtuple

from app.services import analytics_service
from app.models.event_model import Event, OutboundEmail


@pytest.fixture
def mock_db_session():
    return MagicMock()


def test_get_lead_score_distribution(mock_db_session):
    mock_counts = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    mock_db_session.query.return_value.filter.return_value.one.return_value = (
        mock_counts
    )
    result = analytics_service.get_lead_score_distribution(mock_db_session)
    assert len(result) == 10


def test_get_top_leads(mock_db_session):
    mock_event_1 = MagicMock(
        spec=Event,
        company_id="comp-1",
        event_data={"company_name": "Company A", "score": 95},
    )
    mock_event_2 = MagicMock(
        spec=Event,
        company_id="comp-2",
        event_data={"company_name": "Company B", "score": 92},
    )
    mock_db_session.query.return_value.join.return_value.order_by.return_value.limit.return_value.all.return_value = [
        mock_event_1,
        mock_event_2,
    ]
    result = analytics_service.get_top_leads(mock_db_session, limit=2)
    assert len(result) == 2


def test_get_activation_funnel(mock_db_session):
    query_result = [("file_upload", 100), ("result_viewed", 50)]
    mock_db_session.query.return_value.filter.return_value.group_by.return_value.all.return_value = (
        query_result
    )
    result = analytics_service.get_activation_funnel(mock_db_session)
    assert len(result) == 3


def test_get_email_performance(mock_db_session):
    query_result = [("feature_focused", 200), ("roi_focused", 150)]
    mock_db_session.query.return_value.group_by.return_value.all.return_value = (
        query_result
    )
    result = analytics_service.get_email_performance(mock_db_session)
    assert len(result) == 2


def test_get_qualified_leads_kpi(mock_db_session):
    end_date = date.today()
    start_date = end_date - timedelta(days=29)
    mock_db_session.query.return_value.filter.return_value.scalar.side_effect = [15, 10]
    result = analytics_service.get_qualified_leads_kpi(
        mock_db_session, start_date, end_date
    )
    assert result["current_value"] == 15


def test_get_new_activations_kpi(mock_db_session):
    end_date = date.today()
    start_date = end_date - timedelta(days=29)
    mock_db_session.query.return_value.filter.return_value.scalar.side_effect = [5, 5]
    result = analytics_service.get_new_activations_kpi(
        mock_db_session, start_date, end_date
    )
    assert result["current_value"] == 5


def test_get_email_engagement_kpi(mock_db_session, mocker):
    end_date = date.today()
    start_date = end_date - timedelta(days=29)
    mocker.patch("random.random", side_effect=[0.1, 0.9, 0.1, 0.9])
    current_emails = [
        MagicMock(spec=OutboundEmail, score=80, variant_name="roi_focused"),
        MagicMock(spec=OutboundEmail, score=50, variant_name="feature_focused"),
    ]
    previous_emails = [
        MagicMock(spec=OutboundEmail, score=70, variant_name="roi_focused"),
        MagicMock(spec=OutboundEmail, score=40, variant_name="feature_focused"),
    ]
    mock_db_session.query.return_value.filter.return_value.all.side_effect = [
        current_emails,
        previous_emails,
    ]
    result = analytics_service.get_email_engagement_kpi(
        mock_db_session, start_date, end_date
    )
    assert result["current_value"] == 50.0


def test_get_funnel_over_time(mock_db_session):
    end_date = date(2023, 1, 3)
    start_date = date(2023, 1, 1)
    lead_events = [("2023-01-01", "comp-1"), ("2023-01-02", "comp-2")]
    activation_events = [("2023-01-01", "user-a"), ("2023-01-03", "user-b")]
    mock_db_session.query.return_value.filter.return_value.all.side_effect = [
        lead_events,
        activation_events,
    ]
    result = analytics_service.get_funnel_over_time(
        mock_db_session, start_date, end_date
    )
    assert result[0] == {"date": "2023-01-01", "qualified_leads": 1, "activations": 1}


def test_get_scored_leads_table_data(mock_db_session):
    Row = namedtuple(
        "Row", ["company_id", "company_name", "score", "email_variant_sent"]
    )
    mock_results = [
        Row("comp-1", "Company A", 95, "roi_focused"),
        Row("comp-2", "Company B", 85, None),
    ]
    mock_db_session.query.return_value.join.return_value.outerjoin.return_value.order_by.return_value.all.return_value = (
        mock_results
    )
    result = analytics_service.get_scored_leads_table_data(mock_db_session)
    assert len(result) == 2