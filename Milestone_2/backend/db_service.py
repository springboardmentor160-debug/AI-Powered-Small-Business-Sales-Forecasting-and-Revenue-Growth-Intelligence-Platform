"""
Database Persistence & Service Layer for Milestone 2 (MarketMind AI)
Keeps ML logic separate from database operations.
"""

import os
import json
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .db_models import (
    User, Customer, Product, Sales, Invoice, Inventory, Geography,
    SegmentationResult, ClusterSummary, ForecastResult, ModelMetric
)
from .auth import hash_password

def init_db_tables():
    """Create all tables in the database if they do not exist."""
    Base.metadata.create_all(bind=engine)

def save_segmentation_results_to_db(df_features: pd.DataFrame, cluster_profiles: pd.DataFrame, metrics: dict, db: Session):
    """Persist segmentation outputs and metrics into PostgreSQL tables."""
    init_db_tables()

    # Clear existing segmentation tables
    db.query(SegmentationResult).delete()
    db.query(ClusterSummary).delete()
    db.commit()

    # 1. Save Cluster Summaries
    for c_id, row in cluster_profiles.iterrows():
        cs = ClusterSummary(
            cluster_id=int(c_id),
            segment_name=str(row.get('segment_name', f'Cluster {c_id}')),
            customer_count=int(row['customer_count']),
            pct_customers=float(row['pct_customers']),
            total_sales=float(row['total_monetary']),
            pct_sales=float(row['pct_sales']),
            mean_recency_days=float(row['mean_recency']),
            mean_frequency_orders=float(row['mean_frequency']),
            mean_monetary_sales=float(row['mean_monetary']),
            mean_order_value=float(row['mean_aov']),
            mean_discount_rate=float(row['mean_discount'])
        )
        db.add(cs)

    # 2. Save Customer Segmentation Results
    for _, row in df_features.iterrows():
        sr = SegmentationResult(
            customer_id=str(row['customer_id']),
            recency_days=float(row['recency_days']),
            frequency_orders=int(row['frequency_orders']),
            monetary_sales=float(row['monetary_sales']),
            avg_order_value=float(row['avg_order_value']),
            total_profit=float(row['total_profit']),
            avg_discount=float(row['avg_discount']),
            kmeans_cluster=int(row['kmeans_cluster']),
            hierarchical_cluster=int(row['hierarchical_cluster']),
            segment_name=str(row['segment_name'])
        )
        db.add(sr)

    db.commit()
    print("[DB Service] Customer segmentation results successfully persisted to PostgreSQL.")

def save_forecasting_results_to_db(combined_df: pd.DataFrame, metrics_dict: dict, best_model_name: str, db: Session):
    """Persist forecasting predictions and evaluation metrics into PostgreSQL tables."""
    init_db_tables()

    db.query(ForecastResult).delete()
    db.query(ModelMetric).delete()
    db.commit()

    # 1. Save Forecast Results
    for _, row in combined_df.iterrows():
        fr = ForecastResult(
            ds=pd.to_datetime(row['ds']).date(),
            actual_sales=float(row['y']) if pd.notnull(row.get('y')) else None,
            profit=float(row['profit']) if pd.notnull(row.get('profit')) else None,
            prophet_yhat=float(row['prophet_yhat']) if pd.notnull(row.get('prophet_yhat')) else None,
            prophet_lower=float(row['prophet_lower']) if pd.notnull(row.get('prophet_lower')) else None,
            prophet_upper=float(row['prophet_upper']) if pd.notnull(row.get('prophet_upper')) else None,
            xgboost_yhat=float(row['xgboost_yhat']) if pd.notnull(row.get('xgboost_yhat')) else None,
            xgboost_lower=float(row['xgboost_lower']) if pd.notnull(row.get('xgboost_lower')) else None,
            xgboost_upper=float(row['xgboost_upper']) if pd.notnull(row.get('xgboost_upper')) else None,
            rf_yhat=float(row['rf_yhat']) if pd.notnull(row.get('rf_yhat')) else None,
            rf_lower=float(row['rf_lower']) if pd.notnull(row.get('rf_lower')) else None,
            rf_upper=float(row['rf_upper']) if pd.notnull(row.get('rf_upper')) else None
        )
        db.add(fr)

    # 2. Save Model Evaluation Metrics
    for model_name, m in metrics_dict.items():
        mm = ModelMetric(
            model_name=model_name,
            mae=float(m['MAE']),
            rmse=float(m['RMSE']),
            r2_score=float(m['R2']),
            mape_pct=float(m['MAPE_pct']),
            is_best_model=(model_name == best_model_name)
        )
        db.add(mm)

    db.commit()
    print("[DB Service] Sales forecasting predictions and model evaluation metrics successfully persisted to PostgreSQL.")

def seed_database_from_sources(db: Session, data_dir: str):
    """Seed initial PostgreSQL database tables from source CSV files."""
    init_db_tables()

    # 1. Seed Initial Users (if empty)
    if db.query(User).count() == 0:
        default_users = [
            {"name": "Owner Admin", "email": "owner@marketmind.ai", "role": "Business Owner", "pass": "OwnerPass123!"},
            {"name": "Downtown Manager", "email": "manager@marketmind.ai", "role": "Store Manager", "pass": "ManagerPass123!"},
            {"name": "Sales Lead", "email": "sales@marketmind.ai", "role": "Sales Executive", "pass": "SalesPass123!"},
            {"name": "System Administrator", "email": "admin@marketmind.ai", "role": "Administrator", "pass": "AdminPass123!"}
        ]
        for u in default_users:
            user_obj = User(
                name=u["name"],
                email=u["email"],
                role=u["role"],
                password_hash=hash_password(u["pass"])
            )
            db.add(user_obj)
        db.commit()
        print("[DB Service] Default users seeded successfully with hashed passwords.")

    # 2. Seed Superstore Source Transactions
    cleaned_csv = os.path.join(data_dir, "cleaned_superstore.csv")
    if os.path.exists(cleaned_csv) and db.query(Customer).count() == 0:
        df_super = pd.read_csv(cleaned_csv)
        
        # Customers
        cust_df = df_super[['customer_id', 'customer_name', 'segment', 'country', 'city', 'state', 'postal_code', 'region']].drop_duplicates('customer_id')
        for _, r in cust_df.iterrows():
            db.add(Customer(
                customer_id=str(r['customer_id']),
                name=str(r['customer_name']),
                orig_segment=str(r['segment']),
                country=str(r['country']),
                city=str(r['city']),
                state=str(r['state']),
                postal_code=str(r['postal_code']),
                region=str(r['region'])
            ))
        db.commit()

        # Products
        prod_df = df_super[['product_id', 'product_name', 'category', 'sub_category', 'sales']].drop_duplicates('product_id')
        for _, r in prod_df.iterrows():
            db.add(Product(
                product_id=str(r['product_id']),
                name=str(r['product_name']),
                category=str(r['category']),
                sub_category=str(r['sub_category']),
                unit_price=float(r['sales'])
            ))
        db.commit()

        # Sales Records
        for _, r in df_super.iterrows():
            db.add(Sales(
                order_id=str(r['order_id']),
                order_date=pd.to_datetime(r['order_date']).date(),
                ship_date=pd.to_datetime(r['ship_date']).date() if pd.notnull(r.get('ship_date')) else None,
                ship_mode=str(r.get('ship_mode', '')),
                customer_id=str(r['customer_id']),
                product_id=str(r['product_id']),
                sales_amount=float(r['sales']),
                quantity=int(r['quantity']),
                discount=float(r.get('discount', 0.0)),
                profit=float(r.get('profit', 0.0))
            ))
        db.commit()

        # Invoices
        inv_csv = os.path.join(data_dir, "invoices.csv")
        if os.path.exists(inv_csv):
            df_inv = pd.read_csv(inv_csv)
            for _, r in df_inv.iterrows():
                db.add(Invoice(
                    id=int(r['id']),
                    sale_id=int(r['sale_id']),
                    amount=float(r['amount']),
                    payment_status=str(r.get('payment_status', 'Paid'))
                ))
            db.commit()

        # Inventory
        inv_prod = os.path.join(data_dir, "inventory.csv")
        if os.path.exists(inv_prod):
            df_inv_prod = pd.read_csv(inv_prod)
            for _, r in df_inv_prod.iterrows():
                db.add(Inventory(
                    product_id=str(r['product_id']),
                    stock_level=int(r['stock_level']),
                    reorder_point=int(r['reorder_point']),
                    warehouse_region=str(r.get('warehouse_region', 'Default'))
                ))
            db.commit()

        print("[DB Service] Seeded business tables (Customers, Products, Sales, Invoices, Inventory) from CSV sources.")

