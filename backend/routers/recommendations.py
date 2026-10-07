from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from backend.models import User
from backend.dependencies import require_roles
from backend.recommendations.pipeline import (
    recommend_products,
    recommend_products_collaborative,
    recommend_products_association,
    mine_association_rules,
    load_sales_data,
    build_customer_product_matrix,
    calculate_customer_similarity
)

router = APIRouter(prefix="/api/v1/recommendations", tags=["Product Recommendations"])


@router.get("/{customer_id}", response_model=Dict[str, Any])
def get_customer_recommendations_combined(
    customer_id: str,
    top_n: int = Query(default=3, ge=1, le=10),
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get combined hybrid product recommendations (Collaborative Filtering + Association Rules)
    for a target customer.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        top_val = top_n if isinstance(top_n, int) else 3
        result = recommend_products(customer_id=customer_id, top_n=top_val)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate hybrid recommendations: {str(e)}")


@router.get("/{customer_id}/collaborative", response_model=Dict[str, Any])
def get_customer_recommendations_collaborative(
    customer_id: str,
    top_n: int = Query(default=3, ge=1, le=10),
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get user-based collaborative filtering product recommendations based on customer cosine similarity.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        top_val = top_n if isinstance(top_n, int) else 3
        result = recommend_products_collaborative(customer_id=customer_id, top_n=top_val)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate collaborative recommendations: {str(e)}")


@router.get("/{customer_id}/association", response_model=Dict[str, Any])
def get_customer_recommendations_association(
    customer_id: str,
    top_n: int = Query(default=3, ge=1, le=10),
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get market basket association rule product recommendations based on items frequently bought together.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        top_val = top_n if isinstance(top_n, int) else 3
        result = recommend_products_association(customer_id=customer_id, top_n=top_val)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate association recommendations: {str(e)}")


@router.get("/overview/matrix", response_model=Dict[str, Any])
def get_customer_product_matrix_view(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    """
    Get overview of customer-product purchase matrix and cosine similarities.
    Protected endpoint: Owner, Manager, Admin only.
    """
    try:
        sales_df = load_sales_data()
        matrix = build_customer_product_matrix(sales_df)
        sim_df = calculate_customer_similarity(matrix)

        matrix_records = matrix.reset_index().to_dict(orient="records")
        sim_records = sim_df.round(4).reset_index().to_dict(orient="records")

        return {
            "customer_ids": list(matrix.index),
            "products": list(matrix.columns),
            "matrix": matrix_records,
            "similarities": sim_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve customer product matrix: {str(e)}")
