"""
MarketMind AI — Milestone 3: Customer Churn Prediction Engine
Trains and compares Random Forest, XGBoost / Gradient Boosting, and Logistic Regression models
to predict customer churn probability, assign retention risk categories (High, Medium, Low),
and map risk levels back to Milestone 2 Customer Segments.
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

def run_churn_pipeline(db_path: str, output_dir: str) -> Dict[str, Any]:
    print("[ML Pipeline] Starting Customer Churn Prediction Engine...")
    os.makedirs(os.path.join(output_dir, "churn"), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    df_sales = pd.read_sql_query("SELECT order_id, order_date, customer_id, sales_amount, quantity, discount FROM sales", conn)
    df_cust = pd.read_sql_query("""
        SELECT c.customer_id, c.name as customer_name, COALESCE(s.segment_name, 'Unassigned') as segment_name, c.region 
        FROM customers c 
        LEFT JOIN segmentation_results s ON c.customer_id = s.customer_id
    """, conn)
    conn.close()
    
    if df_sales.empty:
        print("[ML Pipeline Warning] Sales data is empty. Skipping churn prediction.")
        return {}
        
    df_sales['order_date'] = pd.to_datetime(df_sales['order_date'])
    max_date = df_sales['order_date'].max()
    
    # Aggregate customer features
    customer_agg = df_sales.groupby('customer_id').agg(
        last_purchase_date=('order_date', 'max'),
        frequency=('order_id', 'nunique'),
        monetary=('sales_amount', 'sum'),
        avg_order_value=('sales_amount', 'mean'),
        total_quantity=('quantity', 'sum'),
        avg_discount=('discount', 'mean')
    ).reset_index()
    
    # Recency in days relative to max_date
    customer_agg['recency_days'] = (max_date - customer_agg['last_purchase_date']).dt.days
    
    # Define Churn label: Inactive for top recency quartile
    churn_threshold = customer_agg['recency_days'].quantile(0.75)
    customer_agg['is_churned'] = (customer_agg['recency_days'] >= churn_threshold).astype(int)
    
    # Merge customer segment metadata
    df_dataset = pd.merge(customer_agg, df_cust, on='customer_id', how='left')
    
    features = ['recency_days', 'frequency', 'monetary', 'avg_order_value', 'total_quantity', 'avg_discount']
    X = df_dataset[features].fillna(0)
    y = df_dataset['is_churned']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_all_scaled = scaler.transform(X)
    
    # Define Candidate Models
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42)
    }
    
    if HAS_XGBOOST:
        models["XGBoost"] = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, eval_metric='logloss', random_state=42)
        
    model_evals = {}
    best_model_name = ""
    best_f1 = -1.0
    best_clf = None
    
    for name, clf in models.items():
        if name == "Logistic Regression":
            clf.fit(X_train_scaled, y_train)
            y_pred = clf.predict(X_test_scaled)
            y_prob = clf.predict_proba(X_test_scaled)[:, 1]
        else:
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            y_prob = clf.predict_proba(X_test)[:, 1]
            
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        try:
            auc = roc_auc_score(y_test, y_prob)
        except Exception:
            auc = 0.5
            
        model_evals[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4)
        }
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_clf = clf
            
    print(f"[ML Pipeline] Best Churn Model: {best_model_name} (F1 Score: {best_f1:.4f})")
    
    if best_model_name == "Logistic Regression":
        all_probs = best_clf.predict_proba(X_all_scaled)[:, 1]
    else:
        all_probs = best_clf.predict_proba(X)[:, 1]
        
    df_dataset['churn_probability'] = np.round(all_probs, 4)
    
    def assign_risk(prob):
        if prob >= 0.70:
            return "High Risk"
        elif prob >= 0.35:
            return "Medium Risk"
        return "Low Risk"
        
    df_dataset['risk_category'] = df_dataset['churn_probability'].apply(assign_risk)
    
    export_cols = [
        'customer_id', 'customer_name', 'segment_name', 'region', 
        'recency_days', 'frequency', 'monetary', 'avg_order_value', 
        'churn_probability', 'risk_category'
    ]
    df_export = df_dataset[export_cols].sort_values(by='churn_probability', ascending=False)
    
    churn_csv_path = os.path.join(output_dir, "churn", "customer_churn_predictions.csv")
    df_export.to_csv(churn_csv_path, index=False)
    print(f"[ML Pipeline] Saved churn predictions for {len(df_export)} customers to {churn_csv_path}")
    
    segment_risk_summary = df_dataset.groupby(['segment_name', 'risk_category']).size().unstack(fill_value=0).to_dict('index')
    
    metrics = {
        "best_performing_model": best_model_name,
        "model_evaluations": model_evals,
        "total_customers_evaluated": int(len(df_dataset)),
        "high_risk_count": int((df_dataset['risk_category'] == 'High Risk').sum()),
        "medium_risk_count": int((df_dataset['risk_category'] == 'Medium Risk').sum()),
        "low_risk_count": int((df_dataset['risk_category'] == 'Low Risk').sum()),
        "overall_churn_rate_pct": float(round((df_dataset['is_churned'].mean() * 100), 2)),
        "segment_risk_breakdown": segment_risk_summary
    }
    
    metrics_json_path = os.path.join(output_dir, "churn", "churn_model_metrics.json")
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    return metrics

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db = os.path.join(base_dir, "marketmind.db")
    out = os.path.join(base_dir, "outputs")
    run_churn_pipeline(db, out)
