from datetime import datetime, time, timedelta, timezone
from typing import Literal
from zoneinfo import ZoneInfo


def is_valid_date_format(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_month_format(month_str: str) -> bool:
    try:
        datetime.strptime(month_str, "%Y-%m")
        return True
    except ValueError:
        return False


def get_datetime_range(date_str=None):
    tz = timezone(timedelta(hours=7))

    if date_str is None:
        now = datetime.now(tz)
        date_obj = now.date()
    else:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

    from_dt = datetime.combine(date_obj, time(0, 0, 0), tzinfo=tz)
    to_dt = datetime.combine(date_obj, time(23, 59, 59), tzinfo=tz)

    return from_dt.strftime("%Y-%m-%dT%H:%M:%S%z"), to_dt.strftime(
        "%Y-%m-%dT%H:%M:%S%z"
    )


def get_date_now():
    tz = timezone(timedelta(hours=7))
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d")


def get_datetime_now():
    tz = timezone(timedelta(hours=7))
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%dT%H:%M:%S%z")


def combine_date_with_current_time(date_str_ddmmyyyy):
    tz = timezone(timedelta(hours=7))

    try:
        date_part = datetime.strptime(date_str_ddmmyyyy, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError("Invalid date format. Expected dd/mm/yyyy.")

    now_time = datetime.now(tz).time()
    combined_dt = datetime.combine(date_part, now_time, tzinfo=tz)

    return combined_dt.strftime("%Y-%m-%dT%H:%M:%S%z")


def combine_date_with_specific_time(date_str_ddmmyyyy: str, time_obj: time) -> str:
    tz = timezone(timedelta(hours=7))

    try:
        date_part = datetime.strptime(date_str_ddmmyyyy, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError("Invalid date format. Expected dd/mm/yyyy.")

    combined_dt = datetime.combine(date_part, time_obj, tzinfo=tz)

    return combined_dt.strftime("%Y-%m-%dT%H:%M:%S%z")


def compare_date_with_today(date_str: str) -> Literal["past", "future", "today"]:
    try:
        today = datetime.now(timezone(timedelta(hours=7))).date()
        date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError("Invalid date format. Expected dd/mm/yyyy.")

    if date_obj < today:
        return "past"
    elif date_obj > today:
        return "future"
    else:
        return "today"


def convert_to_bangkok(dt_utc: datetime) -> datetime:
    if dt_utc.tzinfo is None:
        raise ValueError("Input datetime must be timezone-aware (UTC).")

    return dt_utc.astimezone(ZoneInfo("Asia/Bangkok"))

def combine_date_with_start_time(date_str_ddmmyyyy: str) -> str:
    tz = timezone(timedelta(hours=7))

    try:
        date_part = datetime.strptime(date_str_ddmmyyyy, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError("Invalid date format. Expected dd/mm/yyyy.")

    start_time = time(0, 0, 0)
    combined_dt = datetime.combine(date_part, start_time, tzinfo=tz)

    return combined_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
