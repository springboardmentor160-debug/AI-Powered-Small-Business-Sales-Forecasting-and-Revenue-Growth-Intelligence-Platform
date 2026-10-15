"""Date-range dropdown + 'show the data as recent'. The fixture data is 10 days (2024-01-01 .. 2024-01-10), 600 revenue per day."""
from datetime import date, timedelta

import pytest

import config


@pytest.fixture
def rebased(monkeypatch):
    monkeypatch.setattr(config, "REBASE_DATES_TO_TODAY", True)


def test_summary_respects_range(client, make_user):
    h = make_user("store_manager")
    a = client.get("/sales/summary", headers=h).json()                                   # default = all time (backwards compatible)
    w = client.get("/sales/summary?range=7d", headers=h).json()
    assert a["total_revenue"] == pytest.approx(6000) and a["range"] == "all" and a["change_pct"] is None
    assert w["total_revenue"] == pytest.approx(4200) and w["total_orders"] == 28 and w["range_days"] == 7
    assert w["range_start"] == "2024-01-04" and w["range_end"] == "2024-01-10"
    assert w["change_pct"] is None                       # the 7 days before Jan 4 are not fully in the data -> no misleading %
    assert w["sales_latest_day"] == pytest.approx(600) and w["low_stock_count"] == 1


def test_invalid_range_is_rejected(client, make_user):
    h = make_user("store_manager")
    for path in ("/sales/summary", "/sales/trend", "/sales/by-category", "/sales/by-store", "/sales/top-products", "/anomalies"):
        assert client.get(f"{path}?range=forever", headers=h).status_code == 422, path


def test_trend_and_breakdowns_follow_the_range(client, make_user):
    h = make_user("business_owner")
    assert len(client.get("/sales/trend?range=7d", headers=h).json()) == 7
    assert len(client.get("/sales/trend?range=all", headers=h).json()) == 10
    cats = {c["category"]: c["revenue"] for c in client.get("/sales/by-category?range=7d", headers=h).json()}
    assert cats["Toys"] == pytest.approx(2800) and cats["Groceries"] == pytest.approx(1400)
    assert client.get("/sales/top-products?limit=1&range=7d", headers=h).json()[0]["revenue"] == pytest.approx(2800)
    assert sum(s["revenue"] for s in client.get("/sales/by-store?range=7d", headers=h).json()) == pytest.approx(4200)


def test_dates_are_moved_forward_so_the_newest_record_is_today(client, make_user, rebased):
    h = make_user("business_owner")
    today = date.today()
    shift = (today - date(2024, 1, 10)).days
    s = client.get("/sales/summary?range=7d", headers=h).json()
    assert s["date_shift_days"] == shift and s["latest_date"] == today.isoformat() and s["range_start"] == (today - timedelta(days=6)).isoformat()
    assert s["source_end"] == "2024-01-10"                                               # the real range is still reported
    trend = client.get("/sales/trend?range=7d", headers=h).json()
    assert trend[-1]["date"] == today.isoformat() and trend[0]["date"] == (today - timedelta(days=6)).isoformat()
    assert client.get("/inventory/alerts", headers=h).json()["date"] == today.isoformat()


def test_forecast_dates_are_shifted_by_the_same_amount_as_sales(client, make_user, monkeypatch):
    h = make_user("business_owner")
    monkeypatch.setattr(config, "REBASE_DATES_TO_TODAY", False)
    raw = client.get("/forecast/revenue", headers=h)
    if raw.status_code == 503:
        pytest.skip("ml/outputs not generated")
    monkeypatch.setattr(config, "REBASE_DATES_TO_TODAY", True)
    moved = client.get("/forecast/revenue", headers=h).json()
    shift = timedelta(days=(date.today() - date(2024, 1, 10)).days)
    for key in ("history", "daily"):
        for before, after in zip(raw.json()[key], moved[key]):
            assert date.fromisoformat(after["date"]) == date.fromisoformat(before["date"]) + shift and after["revenue"] == before["revenue"]
    assert moved["evaluation"] == raw.json()["evaluation"]                                  # non-'date' keys are untouched


def test_anomalies_are_filtered_and_shifted(client, make_user, rebased):
    h = make_user("business_owner")
    everything = client.get("/anomalies?range=all&limit=200", headers=h)
    if everything.status_code == 503:
        pytest.skip("ml/outputs not generated")
    month = client.get("/anomalies?range=30d&limit=200", headers=h).json()
    assert month["total"] <= everything.json()["total"]
    today = date.today().isoformat()
    for a in month["alerts"]:
        assert (date.today() - timedelta(days=29)).isoformat() <= a["date"] <= today and a["message"].startswith(a["date"])
