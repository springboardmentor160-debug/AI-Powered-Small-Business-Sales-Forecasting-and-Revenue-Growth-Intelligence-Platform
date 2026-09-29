"""
Deterministic Natural Language Business Insights Generator (Milestone 2)
Generates dynamic business conclusions strictly from stored PostgreSQL/ML data.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from .db_models import Sales, Customer, Product, SegmentationResult, ClusterSummary, ForecastResult, ModelMetric, Inventory

def generate_business_owner_insights(db: Session) -> List[Dict[str, str]]:
    insights = []
    
    # Total Sales and Profit
    sales_profit = db.query(func.sum(Sales.sales_amount), func.sum(Sales.profit)).first()
    total_sales = sales_profit[0] or 0.0
    total_profit = sales_profit[1] or 0.0

    if total_profit < 0:
        insights.append({
            "type": "warning",
            "title": "Profitability Alert",
            "message": f"The business recorded an overall cumulative net loss of ${abs(total_profit):,.2f} over the analyzed historical period."
        })
    else:
        insights.append({
            "type": "success",
            "title": "Revenue & Profit Overview",
            "message": f"The business generated total cumulative revenue of ${total_sales:,.2f} with a net profit of ${total_profit:,.2f}."
        })

    # Forecast Growth Trend
    fcsts = db.query(ForecastResult).order_by(ForecastResult.ds.asc()).all()
    if fcsts:
        historical_sales = [f.actual_sales for f in fcsts if f.actual_sales is not None]
        future_forecasts = [f.prophet_yhat for f in fcsts if f.actual_sales is None and f.prophet_yhat is not None]

        if historical_sales and future_forecasts:
            recent_annual_sales = sum(historical_sales[-12:])
            projected_annual_sales = sum(future_forecasts[:12])

            diff = projected_annual_sales - recent_annual_sales
            pct_change = (diff / recent_annual_sales * 100) if recent_annual_sales > 0 else 0.0

            if diff > 0:
                insights.append({
                    "type": "positive",
                    "title": "Sales Forecast Projection",
                    "message": f"Sales are expected to increase compared with the previous period, projecting ${projected_annual_sales:,.2f} over the next 12 months (+{pct_change:.1f}% growth)."
                })
            else:
                insights.append({
                    "type": "caution",
                    "title": "Sales Forecast Projection",
                    "message": f"Sales are projected to contract by {abs(pct_change):.1f}% over the next 12 months, totaling ${projected_annual_sales:,.2f}."
                })

    # Top Customer Segment Contribution
    top_seg = db.query(ClusterSummary).order_by(ClusterSummary.total_sales.desc()).first()
    if top_seg:
        insights.append({
            "type": "info",
            "title": "Customer Concentration Insight",
            "message": f"The '{top_seg.segment_name}' segment represents {top_seg.pct_customers:.1f}% of all customers ({top_seg.customer_count} users) but generates {top_seg.pct_sales:.1f}% (${top_seg.total_sales:,.2f}) of total revenue."
        })

    return insights

def generate_store_manager_insights(db: Session) -> List[Dict[str, str]]:
    insights = []

    # Regional Performance
    reg_sales = db.query(Customer.region, func.sum(Sales.sales_amount).label("total_sales")) \
                  .join(Sales, Customer.customer_id == Sales.customer_id) \
                  .group_by(Customer.region) \
                  .order_by(func.sum(Sales.sales_amount).desc()).all()
    if reg_sales:
        top_region, top_rev = reg_sales[0][0], reg_sales[0][1]
        insights.append({
            "type": "info",
            "title": "Regional Sales Dominance",
            "message": f"The '{top_region}' region is the top-performing geographic market, leading sales with ${top_rev:,.2f}."
        })

    # Top Category
    cat_sales = db.query(Product.category, func.sum(Sales.sales_amount).label("total_sales"), func.sum(Sales.profit).label("total_profit")) \
                  .join(Sales, Product.product_id == Sales.product_id) \
                  .group_by(Product.category) \
                  .order_by(func.sum(Sales.sales_amount).desc()).all()
    if cat_sales:
        top_cat, cat_rev, cat_prof = cat_sales[0][0], cat_sales[0][1], cat_sales[0][2]
        insights.append({
            "type": "success",
            "title": "Category Sales Leader",
            "message": f"The '{top_cat}' category generated the highest sales of ${cat_rev:,.2f} with a net profit of ${cat_prof:,.2f}."
        })

    # Inventory Alignment
    total_inv = db.query(func.sum(Inventory.stock_level)).scalar() or 0
    insights.append({
        "type": "neutral",
        "title": "Inventory Management Status",
        "message": f"Total warehouse inventory currently stands at {total_inv:,} units across tracked store catalog products."
    })

    return insights

def generate_sales_executive_insights(db: Session) -> List[Dict[str, str]]:
    insights = []

    # At Risk / Low Activity Customers
    clusters = db.query(ClusterSummary).all()
    at_risk_cluster = next((c for c in clusters if "At-Risk" in c.segment_name or "Low-Activity" in c.segment_name), None)
    if at_risk_cluster:
        insights.append({
            "type": "warning",
            "title": "At-Risk Customer Alert",
            "message": f"There are {at_risk_cluster.customer_count} customers in the '{at_risk_cluster.segment_name}' cluster with an average recency of {at_risk_cluster.mean_recency_days:.1f} days without purchases."
        })

    # High Value Champions
    champion_cluster = next((c for c in clusters if "High-Value" in c.segment_name or "Champions" in c.segment_name), None)
    if champion_cluster:
        insights.append({
            "type": "success",
            "title": "VIP Account Retention Strategy",
            "message": f"Focus on retaining the {champion_cluster.customer_count} '{champion_cluster.segment_name}' accounts who average ${champion_cluster.mean_order_value:,.2f} per order."
        })

    return insights

def generate_admin_insights(db: Session) -> List[Dict[str, str]]:
    insights = []

    # Model Evaluation Winner
    best_metric = db.query(ModelMetric).filter(ModelMetric.is_best_model == True).first()
    if best_metric:
        insights.append({
            "type": "success",
            "title": "AI Forecasting Benchmark Result",
            "message": f"{best_metric.model_name} is the top-performing model with lowest RMSE of ${best_metric.rmse:,.2f} and R² score of {best_metric.r2_score:.4f}."
        })

    # Database Telemetry
    sales_cnt = db.query(Sales).count()
    cust_cnt = db.query(Customer).count()
    insights.append({
        "type": "info",
        "title": "Platform Database Health",
        "message": f"Database operating normally with {sales_cnt:,} transaction lines and {cust_cnt:,} customer records synced."
    })

    return insights
