from datetime import datetime, time, timedelta, timezone


def is_valid_date_format(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
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
