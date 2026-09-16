from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from backend.models import User
from backend.dependencies import get_current_user, require_roles
from backend.segmentation.pipeline import run_segmentation_pipeline, OUTPUT_CSV_PATH
import os
import pandas as pd

router = APIRouter(prefix="/api/v1/segmentation", tags=["Customer Segmentation"])


@router.get("/summary", response_model=Dict[str, Any])
def get_segmentation_summary(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get summary of Customer Segmentation (K-Means and Hierarchical Clustering).
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        df, summary = run_segmentation_pipeline()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate customer segmentation summary: {str(e)}")


@router.get("/customers", response_model=List[Dict[str, Any]])
def get_segmented_customers(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get detailed customer list with K-Means and Hierarchical cluster assignments and named segments.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        if not os.path.exists(OUTPUT_CSV_PATH):
            df, _ = run_segmentation_pipeline()
        else:
            df = pd.read_csv(OUTPUT_CSV_PATH)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve segmented customer list: {str(e)}")
