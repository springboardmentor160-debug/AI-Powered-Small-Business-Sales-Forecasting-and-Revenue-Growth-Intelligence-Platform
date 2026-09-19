import requests
import pandas as pd
import numpy as np

BASE = "http://localhost:8000"

def run_cross_checks():
    # 1. Load CSV directly
    csv_df = pd.read_csv("cleaned_sales_data.csv")
    csv_df["total"] = csv_df["quantity"] * csv_df["unit_price"]
    total_revenue_csv = round(float(csv_df["total"].sum()), 2)
    total_txns_csv = len(csv_df)
    print(f"CSV Direct: Total Revenue = INR {total_revenue_csv:,.2f}, Total Transactions = {total_txns_csv}")

    # 2. Authenticate as Owner
    owner_login = requests.post(f"{BASE}/api/v1/auth/login", data={"username": "owner", "password": "password123"}).json()
    owner_token = owner_login["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # 3. Check Analytics Summary
    summary = requests.get(f"{BASE}/api/v1/analytics/summary", headers=owner_headers).json()
    api_rev = float(summary["total_revenue"])
    api_txns = int(summary["total_transactions"])
    print(f"API Summary: Total Revenue = INR {api_rev:,.2f}, Total Transactions = {api_txns}")
    assert api_rev == total_revenue_csv, f"Revenue mismatch: {api_rev} vs {total_revenue_csv}"
    assert api_txns == total_txns_csv, f"Transactions mismatch: {api_txns} vs {total_txns_csv}"

    # 4. Check Segments
    segments = requests.get(f"{BASE}/segments", headers=owner_headers).json()
    total_segmented_cust = sum(s["customer_count"] for s in segments)
    unique_registered_cust = csv_df[csv_df["customer_id"] != "GUEST"]["customer_id"].nunique()
    print(f"Segments Count: {len(segments)}, Total Segmented Customers: {total_segmented_cust}, Unique Registered Customers in CSV: {unique_registered_cust}")
    assert total_segmented_cust == unique_registered_cust, f"Customer count mismatch: {total_segmented_cust} vs {unique_registered_cust}"

    # 5. Check Forecast
    forecast = requests.get(f"{BASE}/forecast/revenue", headers=owner_headers).json()
    series = requests.get(f"{BASE}/forecast/series", headers=owner_headers).json()
    daily_sum = round(sum(d["predicted_revenue"] for d in series["forecast"]), 2)
    api_fc_rev = float(forecast["predicted_revenue"])
    print(f"Forecast Revenue: INR {api_fc_rev:,.2f}, Daily Series Sum: INR {daily_sum:,.2f}, Winning Model: {forecast['model_used']}")
    assert api_fc_rev == daily_sum, f"Forecast sum mismatch: {api_fc_rev} vs {daily_sum}"
    assert len(series["forecast"]) == 30, f"Forecast horizon mismatch: {len(series['forecast'])}"

    # 6. Check Sales Exec 403 Forbidden
    exec_login = requests.post(f"{BASE}/api/v1/auth/login", data={"username": "exec", "password": "password123"}).json()
    exec_headers = {"Authorization": f"Bearer {exec_login['access_token']}"}
    fc_exec = requests.get(f"{BASE}/forecast/revenue", headers=exec_headers)
    rep_exec = requests.get(f"{BASE}/reports/business", headers=exec_headers)
    print(f"Exec /forecast/revenue status: {fc_exec.status_code}, /reports/business status: {rep_exec.status_code}")
    assert fc_exec.status_code == 403
    assert rep_exec.status_code == 403

    # 7. Check Excel Download
    rep_owner = requests.get(f"{BASE}/reports/business", headers=owner_headers)
    print(f"Owner /reports/business status: {rep_owner.status_code}, payload size: {len(rep_owner.content)} bytes")
    assert rep_owner.status_code == 200
    assert len(rep_owner.content) > 5000

    print(">>> SUCCESS: All cross-check validations and direct CSV assertions passed with 100% precision!")

if __name__ == "__main__":
    run_cross_checks()
