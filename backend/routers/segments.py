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

    try:
        # Fast path for default K=4 global view if cached
        if k == 4 and store_id is None and not force_recompute and os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data["segments"]

        # Dynamic calculation from live data
        cf = build_customer_features(store_id=store_id)
        res = run_segmentation(cf, n_clusters=k, artifacts_dir=artifacts_dir)
        return res["segment_summary"].to_dict(orient="records")
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Customer segmentation data temporarily unavailable: {str(e)}"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error retrieving customer segments: {str(e)}")

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

    try:
        if k == 4 and store_id is None and os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            cf = build_customer_features(store_id=store_id)
            res = run_segmentation(cf, n_clusters=k, artifacts_dir=artifacts_dir)
            df = res["customer_features"]
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Customer dataset temporarily unavailable: {str(e)}"
        )

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

@router.get("/segments/customers/{customer_id}", dependencies=[Depends(all_roles)])
@router.get("/api/v1/segments/customers/{customer_id}", dependencies=[Depends(all_roles)])
@router.get("/api/v1/customers/{customer_id}", dependencies=[Depends(all_roles)])
def get_customer_by_id(customer_id: str) -> Dict[str, Any]:
    """
    Look up an individual customer profile by customer ID.
    Returns 404 if customer ID does not exist.
    """
    artifacts_dir = get_artifacts_dir()
    csv_path = os.path.join(artifacts_dir, "customers_segmented.csv")

    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            cf = build_customer_features()
            res = run_segmentation(cf, n_clusters=4, artifacts_dir=artifacts_dir)
            df = res["customer_features"]
    except (FileNotFoundError, pd.errors.EmptyDataError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Customer dataset temporarily unavailable: {str(e)}"
        )

    clean_id = customer_id.strip().lower()
    matches = df[df["customer_id"].astype(str).str.strip().str.lower() == clean_id]

    if matches.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Customer ID '{customer_id}' not found in active records."
        )

    record = matches.iloc[0].to_dict()
    # Clean any NaN values for valid JSON response
    return {k: (None if pd.isna(v) else v) for k, v in record.items()}
