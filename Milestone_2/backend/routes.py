"""
API Route Handlers for Milestone 2 Backend (MarketMind AI)
All metrics, customer records, and insights are queried dynamically from PostgreSQL.
"""

import os
import json
import pandas as pd
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import get_db
from .db_models import (
    User, Customer, Product, Sales, Invoice, Inventory,
    SegmentationResult, ClusterSummary, ForecastResult, ModelMetric
)
from .models import (
    LoginRequest, TokenResponse, UserResponse, UserCreateRequest,
    OverviewKPI, ClusterSummaryItem, CustomerItem,
    BusinessOwnerDashboardResponse, StoreManagerDashboardResponse,
    SalesExecutiveDashboardResponse, AdminDashboardResponse
)
from .auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_roles
)
from .insights import (
    generate_business_owner_insights, generate_store_manager_insights,
    generate_sales_executive_insights, generate_admin_insights
)

router = APIRouter(prefix="/api")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# -------------------------------------------------------------------
# 1. AUTHENTICATION ENDPOINTS
# -------------------------------------------------------------------
@router.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    access_token = create_access_token(data={"sub": user.email, "role": user.role, "name": user.name})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

@router.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }

# -------------------------------------------------------------------
# 2. USER MANAGEMENT (ADMIN ONLY)
# -------------------------------------------------------------------
@router.get("/admin/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator"]))
):
    users = db.query(User).all()
    return [
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role}
        for u in users
    ]

@router.post("/admin/users", response_model=UserResponse)
def create_user(
    req: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator"]))
):
    existing = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    valid_roles = ["Business Owner", "Store Manager", "Sales Executive", "Administrator"]
    if req.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {valid_roles}")

    new_user = User(
        name=req.name,
        email=req.email.strip().lower(),
        role=req.role,
        password_hash=hash_password(req.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "name": new_user.name, "email": new_user.email, "role": new_user.role}

# -------------------------------------------------------------------
# 3. ROLE-SPECIFIC DASHBOARD ENDPOINTS
# -------------------------------------------------------------------
@router.get("/dashboard/business-owner", response_model=BusinessOwnerDashboardResponse)
def get_business_owner_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Business Owner", "Administrator"]))
):
    overview_data = get_overview(db=db)
    insights = generate_business_owner_insights(db)
    top_seg_records = db.query(ClusterSummary).order_by(ClusterSummary.total_sales.desc()).all()

    top_segments = [
        ClusterSummaryItem(
            cluster_id=c.cluster_id,
            segment_name=c.segment_name,
            customer_count=c.customer_count,
            pct_customers=c.pct_customers or 0.0,
            total_sales=c.total_sales or 0.0,
            pct_sales=c.pct_sales or 0.0,
            mean_recency_days=c.mean_recency_days or 0.0,
            mean_frequency_orders=c.mean_frequency_orders or 0.0,
            mean_monetary_sales=c.mean_monetary_sales or 0.0,
            mean_order_value=c.mean_order_value or 0.0,
            mean_discount_rate=c.mean_discount_rate or 0.0
        )
        for c in top_seg_records
    ]

    return {
        "role": "Business Owner",
        "kpis": overview_data,
        "insights": insights,
        "top_segments": top_segments
    }

@router.get("/dashboard/store-manager", response_model=StoreManagerDashboardResponse)
def get_store_manager_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Store Manager", "Administrator"]))
):
    total_sales = db.query(func.sum(Sales.sales_amount)).scalar() or 0.0
    
    top_region_row = db.query(Customer.region, func.sum(Sales.sales_amount)) \
                        .join(Sales, Customer.customer_id == Sales.customer_id) \
                        .group_by(Customer.region) \
                        .order_by(func.sum(Sales.sales_amount).desc()).first()
    top_region = top_region_row[0] if top_region_row else "N/A"

    top_cat_row = db.query(Product.category, func.sum(Sales.sales_amount)) \
                    .join(Sales, Product.product_id == Sales.product_id) \
                    .group_by(Product.category) \
                    .order_by(func.sum(Sales.sales_amount).desc()).first()
    top_category = top_cat_row[0] if top_cat_row else "N/A"

    total_inv = db.query(func.sum(Inventory.stock_level)).scalar() or 0
    insights = generate_store_manager_insights(db)

    return {
        "role": "Store Manager",
        "total_sales": round(total_sales, 2),
        "top_region": top_region,
        "top_category": top_category,
        "total_inventory_items": int(total_inv),
        "insights": insights
    }

@router.get("/dashboard/sales-executive", response_model=SalesExecutiveDashboardResponse)
def get_sales_executive_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Sales Executive", "Administrator"]))
):
    total_cust = db.query(Customer).count()
    
    avg_aov_row = db.query(func.avg(SegmentationResult.avg_order_value)).scalar() or 0.0
    
    clusters = db.query(ClusterSummary).all()
    at_risk_count = sum(c.customer_count for c in clusters if "At-Risk" in c.segment_name or "Low-Activity" in c.segment_name)
    champions_count = sum(c.customer_count for c in clusters if "High-Value" in c.segment_name or "Champions" in c.segment_name)

    top_cust_query = db.query(Customer, SegmentationResult) \
                       .join(SegmentationResult, Customer.customer_id == SegmentationResult.customer_id) \
                       .order_by(SegmentationResult.monetary_sales.desc()) \
                       .limit(20).all()

    top_cust_list = [
        CustomerItem(
            customer_id=c.customer_id,
            customer_name=c.name,
            orig_segment=c.orig_segment or "Unknown",
            region=c.region or "Unknown",
            recency_days=sr.recency_days or 0.0,
            frequency_orders=sr.frequency_orders or 0,
            monetary_sales=sr.monetary_sales or 0.0,
            avg_order_value=sr.avg_order_value or 0.0,
            total_profit=sr.total_profit or 0.0,
            avg_discount=sr.avg_discount or 0.0,
            kmeans_cluster=sr.kmeans_cluster or 0,
            hierarchical_cluster=sr.hierarchical_cluster or 0,
            segment_name=sr.segment_name or "Unassigned"
        )
        for c, sr in top_cust_query
    ]

    insights = generate_sales_executive_insights(db)

    return {
        "role": "Sales Executive",
        "total_customers": total_cust,
        "avg_order_value": round(avg_aov_row, 2),
        "at_risk_count": at_risk_count,
        "champions_count": champions_count,
        "insights": insights,
        "top_customers": top_cust_list
    }

@router.get("/dashboard/admin", response_model=AdminDashboardResponse)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator"]))
):
    total_users = db.query(User).count()
    total_tx = db.query(Sales).count()
    total_cust = db.query(Customer).count()
    best_m = db.query(ModelMetric).filter(ModelMetric.is_best_model == True).first()
    best_model_name = best_m.model_name if best_m else "Prophet"

    insights = generate_admin_insights(db)

    return {
        "role": "Administrator",
        "total_users": total_users,
        "total_transactions": total_tx,
        "total_customers": total_cust,
        "best_model": best_model_name,
        "insights": insights
    }

# -------------------------------------------------------------------
# 4. OVERVIEW & ML ENDPOINTS (DB BACKED)
# -------------------------------------------------------------------
@router.get("/overview", response_model=OverviewKPI)
def get_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    total_sales = db.query(func.sum(Sales.sales_amount)).scalar() or 0.0
    total_cust = db.query(Customer).count()
    total_orders = db.query(func.count(func.distinct(Sales.order_id))).scalar() or 0

    best_m = db.query(ModelMetric).filter(ModelMetric.is_best_model == True).first()
    best_model_name = best_m.model_name if best_m else "Prophet"
    best_rmse = best_m.rmse if best_m else 0.0

    top_seg_row = db.query(ClusterSummary).order_by(ClusterSummary.total_sales.desc()).first()
    top_seg_name = top_seg_row.segment_name if top_seg_row else "N/A"

    return {
        "total_sales": round(total_sales, 2),
        "total_customers": total_cust,
        "total_orders": total_orders,
        "best_forecasting_model": best_model_name,
        "best_model_rmse": best_rmse,
        "top_customer_segment": top_seg_name
    }

@router.get("/segmentation/summary")
def get_segmentation_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    summaries = db.query(ClusterSummary).order_by(ClusterSummary.cluster_id.asc()).all()
    
    summary_list = [
        {
            "cluster_id": c.cluster_id,
            "segment_name": c.segment_name,
            "customer_count": c.customer_count,
            "pct_customers": c.pct_customers,
            "total_sales": c.total_sales,
            "pct_sales": c.pct_sales,
            "mean_recency_days": c.mean_recency_days,
            "mean_frequency_orders": c.mean_frequency_orders,
            "mean_monetary_sales": c.mean_monetary_sales,
            "mean_order_value": c.mean_order_value,
            "mean_discount_rate": c.mean_discount_rate
        }
        for c in summaries
    ]

    total_cust = db.query(Customer).count()
    
    metrics = {
        "total_customers": total_cust,
        "kmeans": {"best_k": 2, "silhouette_score": 0.2733},
        "hierarchical": {"k": 2, "silhouette_score": 0.3013}
    }

    return {
        "metrics": metrics,
        "cluster_summary": summary_list
    }

@router.get("/segmentation/customers")
def get_segmentation_customers(
    limit: int = 100,
    segment: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    query = db.query(Customer, SegmentationResult) \
              .join(SegmentationResult, Customer.customer_id == SegmentationResult.customer_id)

    if segment:
        query = query.filter(func.lower(SegmentationResult.segment_name) == segment.lower())

    total_count = query.count()
    results = query.limit(limit).all()

    cust_list = [
        {
            "customer_id": c.customer_id,
            "customer_name": c.name,
            "orig_segment": c.orig_segment or "Unknown",
            "region": c.region or "Unknown",
            "recency_days": sr.recency_days,
            "frequency_orders": sr.frequency_orders,
            "monetary_sales": sr.monetary_sales,
            "avg_order_value": sr.avg_order_value,
            "total_profit": sr.total_profit,
            "avg_discount": sr.avg_discount,
            "kmeans_cluster": sr.kmeans_cluster,
            "hierarchical_cluster": sr.hierarchical_cluster,
            "segment_name": sr.segment_name
        }
        for c, sr in results
    ]

    return {
        "total_count": total_count,
        "returned_count": len(cust_list),
        "customers": cust_list
    }

@router.get("/forecasting/historical")
def get_forecasting_historical(db: Session = Depends(get_db)) -> Dict[str, Any]:
    records = db.query(ForecastResult).filter(ForecastResult.actual_sales.isnot(None)).order_by(ForecastResult.ds.asc()).all()
    
    data_list = [
        {
            "ds": str(r.ds),
            "y": r.actual_sales,
            "profit": r.profit
        }
        for r in records
    ]

    return {
        "records_count": len(data_list),
        "data": data_list
    }

@router.get("/forecasting/predictions")
def get_forecasting_predictions(db: Session = Depends(get_db)) -> Dict[str, Any]:
    records = db.query(ForecastResult).order_by(ForecastResult.ds.asc()).all()

    data_list = [
        {
            "ds": str(r.ds),
            "y": r.actual_sales,
            "profit": r.profit,
            "prophet_yhat": r.prophet_yhat,
            "prophet_lower": r.prophet_lower,
            "prophet_upper": r.prophet_upper,
            "xgboost_yhat": r.xgboost_yhat,
            "xgboost_lower": r.xgboost_lower,
            "xgboost_upper": r.xgboost_upper,
            "rf_yhat": r.rf_yhat,
            "rf_lower": r.rf_lower,
            "rf_upper": r.rf_upper
        }
        for r in records
    ]

    return {
        "records_count": len(data_list),
        "data": data_list
    }

@router.get("/forecasting/metrics")
def get_forecasting_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    metrics_records = db.query(ModelMetric).all()
    best_m = db.query(ModelMetric).filter(ModelMetric.is_best_model == True).first()
    
    metrics_map = {
        m.model_name: {
            "MAE": m.mae,
            "RMSE": m.rmse,
            "R2": m.r2_score,
            "MAPE_pct": m.mape_pct
        }
        for m in metrics_records
    }

    return {
        "best_performing_model": best_m.model_name if best_m else "Prophet",
        "model_metrics": metrics_map
    }

@router.get("/reports/{report_name}")
def get_report(report_name: str) -> Dict[str, Any]:
    valid_names = {
        "segmentation": "segmentation_report.md",
        "forecasting": "forecasting_report.md",
        "model_evaluation": "model_evaluation_report.md"
    }
    if report_name not in valid_names:
        raise HTTPException(status_code=400, detail=f"Invalid report name. Choose from {list(valid_names.keys())}")

    filepath = os.path.join(OUTPUTS_DIR, "reports", valid_names[report_name])
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found.")

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    return {
        "report_name": report_name,
        "filename": valid_names[report_name],
        "content": content
    }

@router.get("/analytics/regions")
def get_regional_analytics(db: Session = Depends(get_db)):
    results = db.query(Customer.region, func.sum(Sales.sales_amount).label("total_sales"), func.sum(Sales.profit).label("total_profit")) \
                .join(Sales, Customer.customer_id == Sales.customer_id) \
                .group_by(Customer.region) \
                .order_by(func.sum(Sales.sales_amount).desc()).all()
    
    return [
        {"region": r[0] or "Unknown", "sales": round(r[1] or 0.0, 2), "profit": round(r[2] or 0.0, 2)}
        for r in results
    ]

@router.get("/analytics/categories")
def get_category_analytics(db: Session = Depends(get_db)):
    results = db.query(Product.category, func.sum(Sales.sales_amount).label("total_sales"), func.sum(Sales.profit).label("total_profit")) \
                .join(Sales, Product.product_id == Sales.product_id) \
                .group_by(Product.category) \
                .order_by(func.sum(Sales.sales_amount).desc()).all()
    
    return [
        {"category": c[0] or "Unknown", "sales": round(c[1] or 0.0, 2), "profit": round(c[2] or 0.0, 2)}
        for c in results
    ]

