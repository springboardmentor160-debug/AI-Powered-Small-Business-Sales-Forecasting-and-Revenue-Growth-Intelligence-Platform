"""Pure date helpers for the dashboard's range selector and the 'show the data as recent' option.
No FastAPI / SQLAlchemy imports here, so this module is trivially unit-testable.

The sample dataset ends on a fixed historical day. 'Rebasing' moves every date shown to the user forward by a constant
number of days so that the newest record is today. Filtering still happens on the ORIGINAL dates in the database."""
from datetime import date, timedelta

RANGE_PATTERN = r"^(7d|30d|90d|365d|all)$"
RANGE_DAYS = {"7d": 7, "30d": 30, "90d": 90, "365d": 365, "all": None}


def window_start(last, days):
    """First day of a window of `days` days ending on `last` (inclusive). None = no lower bound (all time)."""
    if last is None or days is None:
        return None
    return last - timedelta(days=days - 1)


def previous_window(last, days):
    """(start, end) of the equally long window immediately before the current one, or None for 'all time'."""
    start = window_start(last, days)
    if start is None:
        return None
    end = start - timedelta(days=1)
    return end - timedelta(days=days - 1), end


def shift_days(last, today, enabled=True):
    """How many days to add to every displayed date so that `last` shows up as `today`."""
    return (today - last).days if enabled and last is not None else 0


def shift_str(d, shift):
    """'YYYY-MM-DD' (or a date) + shift days -> 'YYYY-MM-DD'."""
    d = d if isinstance(d, date) else date.fromisoformat(str(d)[:10])
    return (d + timedelta(days=shift)).isoformat()


def shift_dates_deep(obj, shift):
    """Copy of a JSON-like structure where every value stored under a 'date' key is shifted (used for the forecast file)."""
    if shift == 0:
        return obj
    if isinstance(obj, dict):
        return {k: (shift_str(v, shift) if k == "date" and isinstance(v, str) else shift_dates_deep(v, shift)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [shift_dates_deep(v, shift) for v in obj]
    return obj
