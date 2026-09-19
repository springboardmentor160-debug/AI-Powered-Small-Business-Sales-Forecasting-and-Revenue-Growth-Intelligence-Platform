import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_business_report(segment_summary_df: pd.DataFrame, forecast_result: dict, output_path: str = None) -> str:
    """
    Generates a professionally styled business report in Excel (.xlsx) format.
    Sheets:
      1. 'Customer Segments': Segment breakdown, customer counts, average spend, and business strategies.
      2. 'Sales Forecast': Executive forecast KPIs, model accuracy, and 30-day daily projected revenues.
    Uses clean business terminology (no raw machine learning jargon) and Rupee (₹) currency formatting.
    """
    if output_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        output_path = os.path.join(base_dir, "artifacts", "business_report.xlsx")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Styling constants
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid") # Dark slate/navy
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=15, bold=True, color="1E293B")
    subtitle_font = Font(name="Calibri", size=10, italic=True, color="64748B")
    section_font = Font(name="Calibri", size=12, bold=True, color="1E293B")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=11)
    
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )
    
    card_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active

    # ==========================================
    # Sheet 1: Customer Segments
    # ==========================================
    ws_seg = wb.create_sheet(title="Customer Segments")
    
    # Title Block
    ws_seg["A1"] = "MarketMind AI — Customer Segmentation & Behavioral Intelligence"
    ws_seg["A1"].font = title_font
    ws_seg["A2"] = f"Executive briefing on customer spending cohorts and retention priorities | Generated: {pd.Timestamp.now().strftime('%Y-%m-%d')}"
    ws_seg["A2"].font = subtitle_font

    # Headers
    headers_seg = [
        "Customer Segment",
        "Customer Count",
        "Average Order Value",
        "Customer Base Share",
        "Average Inactivity (Days)",
        "Strategic Business Recommendation"
    ]
    start_row = 4
    for col_idx, h in enumerate(headers_seg, 1):
        cell = ws_seg.cell(row=start_row, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center" if col_idx in [2, 4, 5] else "left", vertical="center", wrap_text=True)
        cell.border = thin_border

    # Data Rows
    for r_idx, row in segment_summary_df.iterrows():
        cur_row = start_row + 1 + r_idx
        
        c1 = ws_seg.cell(row=cur_row, column=1, value=row["segment"])
        c1.font = bold_font
        c1.border = thin_border

        c2 = ws_seg.cell(row=cur_row, column=2, value=int(row["customer_count"]))
        c2.font = regular_font
        c2.alignment = Alignment(horizontal="center")
        c2.number_format = "#,##0"
        c2.border = thin_border

        c3 = ws_seg.cell(row=cur_row, column=3, value=float(row["avg_purchase_value"]))
        c3.font = regular_font
        c3.number_format = '"₹"#,##0.00'
        c3.alignment = Alignment(horizontal="right")
        c3.border = thin_border

        c4 = ws_seg.cell(row=cur_row, column=4, value=float(row.get("percentage", 0)) / 100.0)
        c4.font = regular_font
        c4.number_format = "0.0%"
        c4.alignment = Alignment(horizontal="center")
        c4.border = thin_border

        c5 = ws_seg.cell(row=cur_row, column=5, value=float(row.get("avg_activity_days", 0)))
        c5.font = regular_font
        c5.alignment = Alignment(horizontal="center")
        c5.number_format = "0.0"
        c5.border = thin_border

        strategy = row.get("description", "")
        c6 = ws_seg.cell(row=cur_row, column=6, value=strategy)
        c6.font = regular_font
        c6.border = thin_border

    # Total / Summary Row
    tot_row = start_row + 1 + len(segment_summary_df)
    ws_seg.cell(row=tot_row, column=1, value="Total Customers").font = bold_font
    ws_seg.cell(row=tot_row, column=1).border = thin_border
    
    tot_cust = ws_seg.cell(row=tot_row, column=2, value=int(segment_summary_df["customer_count"].sum()))
    tot_cust.font = bold_font
    tot_cust.alignment = Alignment(horizontal="center")
    tot_cust.number_format = "#,##0"
    tot_cust.border = thin_border

    avg_all_val = ws_seg.cell(row=tot_row, column=3, value=float(segment_summary_df["avg_purchase_value"].mean()))
    avg_all_val.font = bold_font
    avg_all_val.number_format = '"₹"#,##0.00'
    avg_all_val.alignment = Alignment(horizontal="right")
    avg_all_val.border = thin_border

    tot_pct = ws_seg.cell(row=tot_row, column=4, value=1.0)
    tot_pct.font = bold_font
    tot_pct.number_format = "0.0%"
    tot_pct.alignment = Alignment(horizontal="center")
    tot_pct.border = thin_border

    ws_seg.cell(row=tot_row, column=5, value="").border = thin_border
    ws_seg.cell(row=tot_row, column=6, value="Full retail client portfolio").font = subtitle_font
    ws_seg.cell(row=tot_row, column=6).border = thin_border

    # ==========================================
    # Sheet 2: Sales Forecast
    # ==========================================
    ws_fc = wb.create_sheet(title="Sales Forecast")
    
    # Title Block
    ws_fc["A1"] = "MarketMind AI — 30-Day Sales Revenue Projections"
    ws_fc["A1"].font = title_font
    ws_fc["A2"] = "Predictive cash flow estimates and daily store demand outlook"
    ws_fc["A2"].font = subtitle_font

    # Executive Summary Card
    ws_fc["A4"] = "Executive Forecast Summary"
    ws_fc["A4"].font = section_font

    summary_cards = [
        ("Forecast Horizon", forecast_result.get("period", "Next 30 Days")),
        ("Projected Total Revenue", f"₹{forecast_result.get('predicted_revenue', 0):,.2f}"),
        ("Forecasting Engine Selected", forecast_result.get("model_used", "Prophet")),
        ("Historical Prediction Error (MAE)", f"₹{forecast_result.get('metrics', {}).get(forecast_result.get('model_used'), {}).get('mae', 0):,.2f}")
    ]

    for idx, (lbl, val) in enumerate(summary_cards):
        r = 5 + idx
        ws_fc.cell(row=r, column=1, value=lbl).font = bold_font
        ws_fc.cell(row=r, column=1).fill = card_fill
        ws_fc.cell(row=r, column=1).border = thin_border

        ws_fc.cell(row=r, column=2, value=val).font = regular_font
        ws_fc.cell(row=r, column=2).fill = card_fill
        ws_fc.cell(row=r, column=2).border = thin_border

    # Daily Table Header
    headers_fc = [
        "Projection Date",
        "Day of Week",
        "Predicted Daily Revenue",
        "Conservative Estimate",
        "Optimistic Estimate"
    ]
    daily_start_row = 11
    for col_idx, h in enumerate(headers_fc, 1):
        cell = ws_fc.cell(row=daily_start_row, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    # Daily Data Rows
    daily_forecast = forecast_result.get("daily_forecast", [])
    for r_idx, row in enumerate(daily_forecast):
        cur_row = daily_start_row + 1 + r_idx

        c1 = ws_fc.cell(row=cur_row, column=1, value=row["date"])
        c1.font = regular_font
        c1.alignment = Alignment(horizontal="center")
        c1.border = thin_border

        c2 = ws_fc.cell(row=cur_row, column=2, value=row["day_of_week"])
        c2.font = regular_font
        c2.alignment = Alignment(horizontal="center")
        c2.border = thin_border

        c3 = ws_fc.cell(row=cur_row, column=3, value=float(row["predicted_revenue"]))
        c3.font = bold_font
        c3.number_format = '"₹"#,##0.00'
        c3.alignment = Alignment(horizontal="right")
        c3.border = thin_border

        c4 = ws_fc.cell(row=cur_row, column=4, value=float(row["lower_bound"]))
        c4.font = regular_font
        c4.number_format = '"₹"#,##0.00'
        c4.alignment = Alignment(horizontal="right")
        c4.border = thin_border

        c5 = ws_fc.cell(row=cur_row, column=5, value=float(row["upper_bound"]))
        c5.font = regular_font
        c5.number_format = '"₹"#,##0.00'
        c5.alignment = Alignment(horizontal="right")
        c5.border = thin_border

    # Total Sum Row
    tot_fc_row = daily_start_row + 1 + len(daily_forecast)
    ws_fc.cell(row=tot_fc_row, column=1, value="Projected 30-Day Sum").font = bold_font
    ws_fc.cell(row=tot_fc_row, column=1).border = thin_border
    ws_fc.cell(row=tot_fc_row, column=2, value=f"{len(daily_forecast)} Days").font = bold_font
    ws_fc.cell(row=tot_fc_row, column=2).alignment = Alignment(horizontal="center")
    ws_fc.cell(row=tot_fc_row, column=2).border = thin_border

    tot_val = ws_fc.cell(row=tot_fc_row, column=3, value=float(forecast_result.get("predicted_revenue", 0)))
    tot_val.font = bold_font
    tot_val.number_format = '"₹"#,##0.00'
    tot_val.alignment = Alignment(horizontal="right")
    tot_val.border = thin_border

    tot_low = ws_fc.cell(row=tot_fc_row, column=4, value=float(sum(r["lower_bound"] for r in daily_forecast)))
    tot_low.font = bold_font
    tot_low.number_format = '"₹"#,##0.00'
    tot_low.alignment = Alignment(horizontal="right")
    tot_low.border = thin_border

    tot_high = ws_fc.cell(row=tot_fc_row, column=5, value=float(sum(r["upper_bound"] for r in daily_forecast)))
    tot_high.font = bold_font
    tot_high.number_format = '"₹"#,##0.00'
    tot_high.alignment = Alignment(horizontal="right")
    tot_high.border = thin_border

    # Auto-fit column widths on both sheets
    for ws in [ws_seg, ws_fc]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len and cell.row > 2:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    # Remove initial empty sheet
    if default_sheet in wb.worksheets and len(wb.worksheets) > 1:
        wb.remove(default_sheet)

    wb.save(output_path)
    return output_path
