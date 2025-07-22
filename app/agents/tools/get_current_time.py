from datetime import datetime, timedelta
import pytz
import dateparser

def get_current_time(timezone: str = "America/Sao_Paulo", lang: str = "pt") -> dict:
    """
    Retorna a hora atual de forma estruturada.
    """
    now = datetime.now(pytz.timezone(timezone))
    return {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "weekday": now.strftime("%A"),  # Ainda em inglês
        "timezone": now.strftime("%Z"),
        "iso": now.isoformat()
    }

def calculate_future_date(days: int = 0, weeks: int = 0, timezone: str = "America/Sao_Paulo", lang: str = "pt") -> dict:
    """
    Soma dias/semanas à data atual e retorna a nova data de forma estruturada.
    """
    now = datetime.now(pytz.timezone(timezone))
    future = now + timedelta(days=days + weeks * 7)
    return {
        "year": future.year,
        "month": future.month,
        "day": future.day,
        "hour": future.hour,
        "minute": future.minute,
        "weekday": future.strftime("%A"),
        "timezone": future.strftime("%Z"),
        "iso": future.isoformat()
    }

def parse_date_query(question: str, timezone: str = "America/Sao_Paulo", lang: str = "pt") -> dict:
    """
    Interpreta uma string como "daqui a 2 semanas" e retorna a data interpretada.
    """
    settings = {"PREFER_DATES_FROM": "future", "TIMEZONE": timezone}
    parsed = dateparser.parse(question, settings=settings)
    if not parsed:
        return {"error": "Could not parse date."}

    localized = pytz.timezone(timezone).localize(parsed)
    return {
        "year": localized.year,
        "month": localized.month,
        "day": localized.day,
        "hour": localized.hour,
        "minute": localized.minute,
        "weekday": localized.strftime("%A"),
        "timezone": localized.strftime("%Z"),
        "iso": localized.isoformat()
    }

def get_day_of_week(date_str: str, lang: str = "pt") -> dict:
    """
    Retorna o dia da semana de uma data YYYY-MM-DD.
    """
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return {
            "year": date.year,
            "month": date.month,
            "day": date.day,
            "weekday": date.strftime("%A"),
            "iso": date.date().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}
