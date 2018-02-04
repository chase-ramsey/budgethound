from calendar import monthcalendar
from datetime import datetime, time
from dateutil.parser import parse
from django.utils.timezone import get_current_timezone, localtime, make_aware, now


def get_local_today_min(datetime_str=None):
    """
    Returns a localized datetime object for the current day
    at midnight
    """
    if datetime_str:
        day = localtime(parse(datetime_str))
    else:
        day = localtime(now())

    today_min = make_aware(
        datetime.combine(day, time.min),
        timezone=get_current_timezone()
    )

    return today_min


def get_current_week():
    """
    Returns a list of days representing the current calendar
    week, where each item is a number for the calendar day
    """
    today = get_local_today_min()

    week = None
    cal = monthcalendar(today.year, today.month)
    for wk in cal:
        if today.day in wk:
            week = list(filter(lambda d: d > 0, wk))

    if not week:
        raise Exception('Error determining current week')

    return week


def get_start_day_for_week():
    """
    Returns a datetime object for the first day of the calendar week
    """
    today = get_local_today_min()
    week = get_current_week()

    first_day = datetime(today.year, today.month, week[0], tzinfo=get_current_timezone())
    return first_day
