import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from auth import require_role

router = APIRouter(tags=["Reports"])

# Per the Access Matrix: Business Owner, Store Manager, Admin only. Sales Executive receives 403.
report_authorized = require_role(["business_owner", "store_manager", "administrator", "admin"])

def get_artifacts_dir() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, "artifacts")

@router.get("/reports/business", dependencies=[Depends(report_authorized)])
@router.get("/api/v1/reports/business", dependencies=[Depends(report_authorized)])
def download_business_report():
    """
    Downloads the formatted multi-sheet Excel business report containing
    Customer Segments and Sales Forecast projections.
    Access Matrix: Business Owner, Store Manager, Admin only. Sales Executive receives 403.
    """
    artifacts_dir = get_artifacts_dir()
    report_path = os.path.join(artifacts_dir, "business_report.xlsx")

    if not os.path.exists(report_path):
        from backend.ml.train import train_all_artifacts
        train_all_artifacts()

    if not os.path.exists(report_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Business report file could not be located or generated."
        )

    return FileResponse(
        path=report_path,
        filename="business_report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
