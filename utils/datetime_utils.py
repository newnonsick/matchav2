import calendar
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from zoneinfo import ZoneInfo


def is_valid_date_format(date_str: str):
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


def get_datetime_range(date: date | None = None) -> tuple[datetime, datetime]:
    tz = timezone(timedelta(hours=7))

    if not date:
        now = datetime.now(tz)
        date = now.date()

    from_dt = datetime.combine(date, time(0, 0, 0), tzinfo=tz)
    to_dt = datetime.combine(date, time(23, 59, 59), tzinfo=tz)

    return from_dt, to_dt


def get_date_now() -> date:
    tz = timezone(timedelta(hours=7))
    now = datetime.now(tz).date()
    return now


def get_datetime_now() -> datetime:
    tz = timezone(timedelta(hours=7))
    now = datetime.now(tz)
    return now


def get_monthstr_now():
    tz = timezone(timedelta(hours=7))
    now = datetime.now(tz)
    return now.strftime("%Y-%m")


def combine_date_with_current_time(target_date: date) -> datetime:
    tz = timezone(timedelta(hours=7))

    now_time = datetime.now(tz).time()
    combined_dt = datetime.combine(target_date, now_time, tzinfo=tz)

    return combined_dt


def combine_date_with_specific_time(target_date: date, time_obj: time) -> datetime:
    tz = timezone(timedelta(hours=7))

    combined_dt = datetime.combine(target_date, time_obj, tzinfo=tz)

    return combined_dt


def compare_date_with_today(target_date: date) -> Literal["past", "future", "today"]:
    today = datetime.now(timezone(timedelta(hours=7))).date()

    if target_date < today:
        return "past"
    elif target_date > today:
        return "future"
    else:
        return "today"


def convert_to_bangkok(dt_utc: datetime) -> datetime:
    if dt_utc.tzinfo is None:
        raise ValueError("Input datetime must be timezone-aware (UTC).")

    return dt_utc.astimezone(ZoneInfo("Asia/Bangkok"))


def combine_date_with_start_time(target_date: date) -> datetime:
    tz = timezone(timedelta(hours=7))
    start_time = time(0, 0, 0)
    combined_dt = datetime.combine(target_date, start_time, tzinfo=tz)

    return combined_dt


def get_weekdays_in_month(yyyy_mm: str) -> list[date]:
    try:
        datetime.strptime(yyyy_mm, "%Y-%m")
    except ValueError:
        raise ValueError("Invalid month format. Expected YYYY-MM.")

    year, month = map(int, yyyy_mm.split("-"))

    first_day = datetime(year, month, 1)
    _, num_days = calendar.monthrange(year, month)

    weekdays: list[date] = []
    for day in range(num_days):
        current_day = first_day + timedelta(days=day)
        if current_day.weekday() < 5:
            weekdays.append(current_day.date())

    return weekdays


def get_month_range(
    month_str: str, timezone_str: str = "Asia/Bangkok"
) -> tuple[datetime, datetime]:
    tz = ZoneInfo(timezone_str)
    try:
        month_start = datetime.strptime(month_str, "%Y-%m").replace(tzinfo=tz)
    except ValueError:
        raise ValueError("Invalid month format. Expected YYYY-MM.")

    if month_start.month == 12:
        next_month = datetime(month_start.year + 1, 1, 1, tzinfo=tz)
    else:
        next_month = datetime(month_start.year, month_start.month + 1, 1, tzinfo=tz)

    month_end = next_month - timedelta(days=1)
    month_end = month_end.replace(hour=23, minute=59, second=59)

    return month_start, month_end


def get_previous_weekdays(current_date: date, num_days: int = 5) -> list[datetime]:
    weekdays: list[datetime] = []

    while len(weekdays) < num_days:
        if current_date.weekday() < 5:
            tz = timezone(timedelta(hours=7))
            weekdays.append(datetime.combine(current_date, time(0, 0, 0), tzinfo=tz))
        current_date -= timedelta(days=1)

    return weekdays
