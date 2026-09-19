import os
import json
import math
import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List, Dict, Any

from auth import require_role
from backend.ml.segmentation import build_customer_features, run_segmentation
import models

router = APIRouter(tags=["Customer Segments"])
all_roles = require_role(["business_owner", "store_manager", "sales_executive", "administrator", "admin"])

def get_artifacts_dir() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_dir, "artifacts")

@router.get("/segments", dependencies=[Depends(all_roles)])
@router.get("/api/v1/segments", dependencies=[Depends(all_roles)])
def get_segments(
    k: int = Query(4, ge=2, le=6, description="Number of customer segments K"),
    store_id: Optional[str] = Query(None, description="Optional store filter"),
    force_recompute: bool = Query(False, description="Force dynamic recalculation from live database")
) -> List[Dict[str, Any]]:
    """
    Returns the customer segmentation summary breakdown.
    Supports dynamic cluster count K (2 to 6), store filtering, and live database calculations.
    """
    artifacts_dir = get_artifacts_dir()
    summary_path = os.path.join(artifacts_dir, "segmentation_summary.json")

    # Fast path for default K=4 global view if cached
    if k == 4 and store_id is None and not force_recompute and os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["segments"]

    # Dynamic calculation from live data
    cf = build_customer_features(store_id=store_id)
    res = run_segmentation(cf, n_clusters=k, artifacts_dir=artifacts_dir)
    return res["segment_summary"].to_dict(orient="records")

@router.get("/segments/customers", dependencies=[Depends(all_roles)])
@router.get("/api/v1/segments/customers", dependencies=[Depends(all_roles)])
def get_segmented_customers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    segment: Optional[str] = Query(None, description="Filter by segment name"),
    search: Optional[str] = Query(None, description="Search by customer ID"),
    store_id: Optional[str] = Query(None, description="Optional store filter"),
    k: int = Query(4, ge=2, le=6, description="Number of clusters K")
) -> Dict[str, Any]:
    """
    Paginated, searchable list of customer profiles with RFM signals, cluster assignment,
    and named business segments.
    """
    artifacts_dir = get_artifacts_dir()
    csv_path = os.path.join(artifacts_dir, "customers_segmented.csv")

    if k == 4 and store_id is None and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        cf = build_customer_features(store_id=store_id)
        res = run_segmentation(cf, n_clusters=k, artifacts_dir=artifacts_dir)
        df = res["customer_features"]

    if segment:
        df = df[df["segment"].str.lower().str.contains(segment.lower().strip(), na=False)]

    if search:
        s = search.lower().strip()
        df = df[df["customer_id"].str.lower().str.contains(s, na=False) | df["segment"].str.lower().str.contains(s, na=False)]

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
