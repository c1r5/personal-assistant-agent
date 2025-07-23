# type: ignore
import sys
import pytz
import dateparser
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DEFAULT_TIMEZONE = 'America/Sao_Paulo'

def test_parse_date_query():
    from app.agents.tools.get_current_time import parse_date_query

    settings = {"PREFER_DATES_FROM": "future", "TIMEZONE": DEFAULT_TIMEZONE}
    question = "in 10 days"

    parsed = dateparser.parse(question, settings=settings)
    if not parsed:
        return {"error": "Could not parse date."}

    localized = pytz.timezone(DEFAULT_TIMEZONE).localize(parsed)

    assert parse_date_query(
        question=question,
        timezone=DEFAULT_TIMEZONE
    ) == {
        "year": localized.year,
        "month": localized.month,
        "day": localized.day,
        "hour": localized.hour,
        "minute": localized.minute,
        "weekday": localized.strftime("%A"),
        "timezone": localized.strftime("%Z"),
    }

def test_calculate_future_date():
    from app.agents.tools.get_current_time import calculate_future_date

    days = 10
    weeks = 2

    now = datetime.now(pytz.timezone(DEFAULT_TIMEZONE))
    future = now + timedelta(days=days + weeks * 7)

    assert calculate_future_date(days = days, weeks = weeks) == {
        "year": future.year,
        "month": future.month,
        "day": future.day,
        "hour": future.hour,
        "minute": future.minute,
        "weekday": future.strftime("%A"),
        "timezone": future.strftime("%Z"),
    }

def test_get_current_time():
    from app.agents.tools.get_current_time import get_current_time

    now = datetime.now(pytz.timezone(DEFAULT_TIMEZONE))

    assert get_current_time() == {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "weekday": now.strftime("%A"),
        "timezone": now.strftime("%Z"),
    }
