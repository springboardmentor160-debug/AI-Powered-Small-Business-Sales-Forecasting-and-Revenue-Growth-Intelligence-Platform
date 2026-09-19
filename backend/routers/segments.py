import os
import json
import math
import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List, Dict, Any

from auth import require_role, get_current_user
import models

router = APIRouter(tags=["Customer Segments"])
all_roles = require_role(["business_owner", "store_manager", "sales_executive", "administrator", "admin"])

def get_artifacts_dir() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, "artifacts")

@router.get("/segments", dependencies=[Depends(all_roles)])
@router.get("/api/v1/segments", dependencies=[Depends(all_roles)])
def get_segments() -> List[Dict[str, Any]]:
    """
    Returns the executive customer segmentation breakdown.
    Each segment contains customer count, average order value, average frequency,
    percentage share, and actionable business description.
    """
    artifacts_dir = get_artifacts_dir()
    summary_path = os.path.join(artifacts_dir, "segmentation_summary.json")

    if not os.path.exists(summary_path):
        from backend.ml.train import train_all_artifacts
        train_all_artifacts()

    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["segments"]

@router.get("/segments/customers", dependencies=[Depends(all_roles)])
@router.get("/api/v1/segments/customers", dependencies=[Depends(all_roles)])
def get_segmented_customers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    segment: Optional[str] = Query(None, description="Filter by segment name")
) -> Dict[str, Any]:
    """
    Paginated list of individual customer records with RFM metrics, assigned cluster,
    and named business segment.
    """
    artifacts_dir = get_artifacts_dir()
    csv_path = os.path.join(artifacts_dir, "customers_segmented.csv")

    if not os.path.exists(csv_path):
        from backend.ml.train import train_all_artifacts
        train_all_artifacts()

    df = pd.read_csv(csv_path)

    if segment:
        df = df[df["segment"].str.lower() == segment.lower().strip()]

    total = len(df)
    pages = max(1, math.ceil(total / limit))
    start = (page - 1) * limit
    end = start + limit

    paged_df = df.iloc[start:end]
    items = paged_df.to_dict(orient="records")

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }
