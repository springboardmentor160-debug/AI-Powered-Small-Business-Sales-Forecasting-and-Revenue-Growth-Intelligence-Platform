import pytest
import os
import sys
import openpyxl
import json
from fastapi.testclient import TestClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(project_root, "backend")
for p in [project_root, backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.main import app

def test_excel_file_exists_and_opens():
    """Verify business_report.xlsx exists, is non-empty, and loads cleanly with openpyxl."""
    report_path = os.path.join(project_root, "artifacts", "business_report.xlsx")
    assert os.path.exists(report_path), f"Report not found at {report_path}"
    assert os.path.getsize(report_path) > 0, "Report file is 0 bytes"

    wb = openpyxl.load_workbook(report_path)
    assert len(wb.sheetnames) >= 2, "Workbook must contain at least 2 sheets"

def test_both_sheets_present_with_exact_names():
    """Verify sheets 'Customer Segments' and 'Sales Forecast' exist."""
    report_path = os.path.join(project_root, "artifacts", "business_report.xlsx")
    wb = openpyxl.load_workbook(report_path)
    
    assert "Customer Segments" in wb.sheetnames, "Sheet 'Customer Segments' is missing"
    assert "Sales Forecast" in wb.sheetnames, "Sheet 'Sales Forecast' is missing"

def test_excel_values_match_api_data():
    """Verify Excel values exactly match API responses from /segments and /forecast/revenue."""
    client = TestClient(app)
    
    # Login as owner
    login_resp = client.post("/api/v1/auth/login", data={"username": "owner", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch API data
    seg_api = client.get("/segments", headers=headers).json()
    fc_api = client.get("/forecast/revenue", headers=headers).json()

    report_path = os.path.join(project_root, "artifacts", "business_report.xlsx")
    wb = openpyxl.load_workbook(report_path)

    # 1. Check Customer Segments sheet
    ws_seg = wb["Customer Segments"]
    excel_segments = {}
    for r in range(5, 9): # 4 segment rows (starting at row 5)
        seg_name = ws_seg.cell(row=r, column=1).value
        cust_cnt = ws_seg.cell(row=r, column=2).value
        avg_val = ws_seg.cell(row=r, column=3).value
        excel_segments[seg_name] = {"count": cust_cnt, "avg_val": avg_val}

    for item in seg_api:
        name = item["segment"]
        assert name in excel_segments, f"Segment {name} missing from Excel sheet"
        assert excel_segments[name]["count"] == item["customer_count"]
        assert round(float(excel_segments[name]["avg_val"]), 2) == round(float(item["avg_purchase_value"]), 2)

    # 2. Check Sales Forecast sheet
    ws_fc = wb["Sales Forecast"]
    # Cell B6 has the projected revenue
    excel_total_rev_str = str(ws_fc.cell(row=6, column=2).value)
    # Strip currency symbol and commas
    clean_val = excel_total_rev_str.replace("₹", "").replace(",", "").strip()
    excel_total_rev = float(clean_val)
    api_total_rev = float(fc_api["predicted_revenue"])

    assert abs(excel_total_rev - api_total_rev) < 1.0, (
        f"Forecast mismatch: Excel has {excel_total_rev}, API has {api_total_rev}"
    )

    # Check daily rows count (should be 30 days starting at row 12)
    daily_count = 0
    for r in range(12, 50):
        if ws_fc.cell(row=r, column=1).value is not None and "Total" not in str(ws_fc.cell(row=r, column=1).value) and "Projected" not in str(ws_fc.cell(row=r, column=1).value):
            daily_count += 1
        else:
            break
    assert daily_count == 30, f"Expected 30 daily forecast rows, found {daily_count}"
