import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from typing import Optional

from auth import require_role

router = APIRouter(tags=["Reports"])

# Per the Access Matrix: Business Owner, Store Manager, Admin only. Sales Executive receives 403.
report_authorized = require_role(["business_owner", "store_manager", "administrator", "admin"])

def get_artifacts_dir() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, "artifacts")

@router.get("/reports/business", dependencies=[Depends(report_authorized)])
@router.get("/api/v1/reports/business", dependencies=[Depends(report_authorized)])
def download_business_report(
    periods: int = Query(30, ge=7, le=180, description="Forecast horizon in days"),
    k: int = Query(4, ge=2, le=6, description="Number of segments K"),
    store_id: Optional[str] = Query(None, description="Optional store filter"),
    model: Optional[str] = Query(None, description="Model selection")
):
    """
    Downloads the formatted multi-sheet Excel business report containing
    Customer Segments and Sales Forecast projections.
    Supports dynamic horizon and store scope parameters.
    Access Matrix: Business Owner, Store Manager, Admin only. Sales Executive receives 403.
    """
    artifacts_dir = get_artifacts_dir()
    default_report_path = os.path.join(artifacts_dir, "business_report.xlsx")

    # Fast path: serve default cached report if parameters match default
    if periods == 30 and k == 4 and store_id is None and model is None and os.path.exists(default_report_path):
        return FileResponse(
            path=default_report_path,
            filename="business_report.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Dynamic generation
    from backend.ml.segmentation import build_customer_features, run_segmentation
    from backend.ml.forecasting import prepare_daily_revenue, evaluate_models, run_recursive_forecast
    from backend.ml.reporting import generate_business_report

    cf = build_customer_features(store_id=store_id)
    seg_res = run_segmentation(cf, n_clusters=k)
    daily, _, _ = prepare_daily_revenue(store_id=store_id)
    eval_res = evaluate_models(daily)
    fc_res = run_recursive_forecast(daily, eval_res, periods=periods, selected_model=model)

    temp_fd, temp_path = tempfile.mkstemp(suffix=".xlsx")
    os.close(temp_fd)

    generate_business_report(seg_res["segment_summary"], fc_res, output_path=temp_path)

    scope_suffix = f"_{store_id}" if store_id else "_Global"
    filename = f"MarketMind_Report_{periods}d{scope_suffix}.xlsx"

    return FileResponse(
        path=temp_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
