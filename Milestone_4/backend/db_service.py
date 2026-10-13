"""
Database Service Engine for Milestone 3 (MarketMind AI)
Handles creation of ORM tables, default demo user seeding, and persisting ML outputs into SQLite.
"""

import os
import json
import pandas as pd
from sqlalchemy.orm import Session
from .database import engine
from .db_models import (
    Base, User, CustomerRecommendation, AssociationRule, 
    CustomerChurnPrediction, TransactionAnomaly
)
from .auth import hash_password

def init_db_tables():
    """Ensure database tables exist."""
    Base.metadata.create_all(bind=engine)

def seed_demo_users(db: Session):
    """Seed default demo accounts across the 4 roles."""
    demo_users = [
        {"name": "Executive Owner", "email": "owner@marketmind.ai", "role": "Business Owner", "pass": "OwnerPass123!"},
        {"name": "Operations Manager", "email": "manager@marketmind.ai", "role": "Store Manager", "pass": "ManagerPass123!"},
        {"name": "Sales Executive", "email": "sales@marketmind.ai", "role": "Sales Executive", "pass": "SalesPass123!"},
        {"name": "Platform Admin", "email": "admin@marketmind.ai", "role": "Administrator", "pass": "AdminPass123!"}
    ]
    
    for u in demo_users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            new_user = User(
                name=u["name"],
                email=u["email"],
                role=u["role"],
                password_hash=hash_password(u["pass"])
            )
            db.add(new_user)
    db.commit()

def populate_milestone3_results(db: Session, outputs_dir: str):
    """Load generated CSVs from outputs/ into SQLite tables if empty."""
    try:
        # 1. Customer Recommendations
        recs_csv = os.path.join(outputs_dir, "recommendations", "customer_recommendations.csv")
        if os.path.exists(recs_csv) and db.query(CustomerRecommendation).count() == 0:
            df = pd.read_csv(recs_csv)
            records = [
                CustomerRecommendation(
                    customer_id=row['customer_id'],
                    rank=row['rank'],
                    recommended_product_id=row['recommended_product_id'],
                    product_name=row['product_name'],
                    category=row.get('category'),
                    sub_category=row.get('sub_category'),
                    score=float(row['score']),
                    recommendation_type=row.get('recommendation_type', 'Collaborative Filtering')
                )
                for _, row in df.iterrows()
            ]
            db.bulk_save_objects(records)
            db.commit()
            print(f"[DB Service] Persisted {len(records)} recommendations to SQLite.")

        # 2. Association Rules
        rules_csv = os.path.join(outputs_dir, "recommendations", "association_rules.csv")
        if os.path.exists(rules_csv) and db.query(AssociationRule).count() == 0:
            df = pd.read_csv(rules_csv)
            records = [
                AssociationRule(
                    antecedent_id=row['antecedent_id'],
                    antecedent_name=row['antecedent_name'],
                    consequent_id=row['consequent_id'],
                    consequent_name=row['consequent_name'],
                    support=float(row['support']),
                    confidence=float(row['confidence']),
                    lift=float(row['lift']),
                    recommendation_type=row.get('recommendation_type', 'Cross-Sell / Frequently Bought Together')
                )
                for _, row in df.iterrows()
            ]
            db.bulk_save_objects(records)
            db.commit()
            print(f"[DB Service] Persisted {len(records)} association rules to SQLite.")

        # 3. Customer Churn Predictions
        churn_csv = os.path.join(outputs_dir, "churn", "customer_churn_predictions.csv")
        if os.path.exists(churn_csv) and db.query(CustomerChurnPrediction).count() == 0:
            df = pd.read_csv(churn_csv)
            records = [
                CustomerChurnPrediction(
                    customer_id=row['customer_id'],
                    customer_name=row['customer_name'],
                    segment_name=row.get('segment_name'),
                    region=row.get('region'),
                    recency_days=int(row['recency_days']),
                    frequency=int(row['frequency']),
                    monetary=float(row['monetary']),
                    avg_order_value=float(row['avg_order_value']),
                    churn_probability=float(row['churn_probability']),
                    risk_category=row['risk_category']
                )
                for _, row in df.iterrows()
            ]
            db.bulk_save_objects(records)
            db.commit()
            print(f"[DB Service] Persisted {len(records)} churn predictions to SQLite.")

        # 4. Transaction Anomalies
        anom_csv = os.path.join(outputs_dir, "anomalies", "transaction_anomalies.csv")
        if os.path.exists(anom_csv) and db.query(TransactionAnomaly).count() == 0:
            df = pd.read_csv(anom_csv)
            records = [
                TransactionAnomaly(
                    order_id=str(row['order_id']),
                    order_date=str(row.get('order_date', '')),
                    customer_name=row.get('customer_name'),
                    region=row.get('region'),
                    product_name=row.get('product_name'),
                    category=row.get('category'),
                    sales_amount=float(row['sales_amount']),
                    quantity=int(row['quantity']),
                    discount_pct=float(row.get('discount_pct', 0.0)),
                    profit=float(row.get('profit', 0.0)),
                    anomaly_score=float(row['anomaly_score']),
                    anomaly_reason=str(row['anomaly_reason'])
                )
                for _, row in df.iterrows()
            ]
            db.bulk_save_objects(records)
            db.commit()
            print(f"[DB Service] Persisted {len(records)} transaction anomalies to SQLite.")
            
    except Exception as e:
        print(f"[DB Service Error] Could not populate Milestone 3 outputs: {e}")
