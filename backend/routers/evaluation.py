import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any, List
import pandas as pd

from backend.models import User
from backend.dependencies import require_roles
from backend.services.model_evaluation import (
    run_all_evaluations,
    RESULTS_CSV_PATH
)

router = APIRouter(prefix="/api/v1/evaluation", tags=["Model Evaluation"])


@router.get("/summary", response_model=Dict[str, Any])
def get_evaluation_summary(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Retrieve comprehensive Milestone 4 AI evaluation metrics across all 5 modules:
    Forecasting (MAE, RMSE, R2), Segmentation (Silhouette Score), Churn (Accuracy, Precision, Recall, F1),
    Recommendations (Precision@K, Recall@K), and Anomaly Detection (Detection Accuracy, False Positive Rate).
    Protected: Owner, Manager, Admin.
    """
    try:
        if not os.path.exists(RESULTS_CSV_PATH):
            summary, _ = run_all_evaluations()
            return summary
        else:
            # Quick summary from CSV + full evaluation
            df = pd.read_csv(RESULTS_CSV_PATH)
            return {
                "status": "success",
                "results_file": RESULTS_CSV_PATH,
                "total_records": len(df),
                "modules_evaluated": df["module"].unique().tolist(),
                "records": df.to_dict(orient="records")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve evaluation summary: {str(e)}")


@router.post("/run", response_model=Dict[str, Any])
def execute_model_evaluations(
    current_user: User = Depends(require_roles(["owner", "admin"]))
):
    """
    Execute fresh end-to-end evaluation run and regenerate reports/milestone4_test_results.csv.
    Protected: Owner, Admin.
    """
    try:
        summary, _ = run_all_evaluations()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation execution failed: {str(e)}")


@router.get("/download-csv")
def download_evaluation_csv(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Download reports/milestone4_test_results.csv directly.
    Protected: Owner, Manager, Admin.
    """
    if not os.path.exists(RESULTS_CSV_PATH):
        run_all_evaluations()

    return FileResponse(
        RESULTS_CSV_PATH,
        media_type="text/csv",
        filename="milestone4_test_results.csv"
    )
