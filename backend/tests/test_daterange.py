"""Pure unit tests (no database / web server needed):  python -m pytest tests/test_daterange.py"""
from datetime import date

from daterange import RANGE_DAYS, previous_window, shift_dates_deep, shift_days, shift_str, window_start

LAST = date(2024, 1, 1)


def test_window_start_is_inclusive_and_all_time_is_unbounded():
    assert window_start(LAST, 30) == date(2023, 12, 3)            # 30 days: Dec 3 ... Jan 1
    assert window_start(LAST, 1) == LAST
    assert window_start(LAST, RANGE_DAYS["all"]) is None
    assert window_start(None, 30) is None


def test_previous_window_is_adjacent_and_equally_long():
    s, e = previous_window(LAST, 30)
    assert e == date(2023, 12, 2) and s == date(2023, 11, 3) and (e - s).days == 29
    assert previous_window(LAST, None) is None


def test_shift_days_moves_last_record_to_today():
    today = date(2026, 10, 15)
    n = shift_days(LAST, today)
    assert n == 1018 and shift_str(LAST, n) == "2026-10-15"
    assert shift_days(LAST, today, enabled=False) == 0 and shift_days(None, today) == 0


def test_shift_str_accepts_strings_and_dates():
    assert shift_str("2024-01-01", 1) == "2024-01-02" and shift_str(date(2024, 12, 31), 1) == "2025-01-01"
    assert shift_str("2024-01-01 00:00:00", 0) == "2024-01-01"


def test_shift_dates_deep_only_touches_date_fields():
    src = {"period": "Next 30 Days", "history": [{"date": "2023-12-31", "revenue": 1.0}], "daily": [{"date": "2024-01-02", "revenue": 2.0, "lower": 1}],
           "evaluation": {"train_start": "2022-01-31"}}
    out = shift_dates_deep(src, 10)
    assert out["history"][0]["date"] == "2024-01-10" and out["daily"][0]["date"] == "2024-01-12" and out["daily"][0]["revenue"] == 2.0
    assert out["evaluation"]["train_start"] == "2022-01-31"        # not a 'date' key -> untouched
    assert src["history"][0]["date"] == "2023-12-31"               # original not mutated
    assert shift_dates_deep(src, 0) is src
