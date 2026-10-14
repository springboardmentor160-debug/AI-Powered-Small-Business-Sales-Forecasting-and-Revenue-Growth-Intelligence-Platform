"""
MarketMind AI — Milestone 3: Anomaly & Fraud Detection System
Combines Isolation Forest Machine Learning and Statistical Z-Score / IQR Outlier Detection
to identify suspicious sales transactions and warehouse inventory anomalies.
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.ensemble import IsolationForest
from scipy import stats

def run_anomaly_pipeline(db_path: str, output_dir: str) -> Dict[str, Any]:
    print("[ML Pipeline] Starting Anomaly & Fraud Detection Engine...")
    os.makedirs(os.path.join(output_dir, "anomalies"), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    df_sales = pd.read_sql_query("""
        SELECT s.id, s.order_id, s.order_date, s.customer_id, s.product_id, 
               s.sales_amount, s.quantity, s.discount, s.profit,
               c.name as customer_name, c.region, p.name as product_name, p.category, p.unit_price
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.customer_id
        LEFT JOIN products p ON s.product_id = p.product_id
    """, conn)
    
    df_inv = pd.read_sql_query("""
        SELECT i.inventory_id, i.product_id, i.stock_level, i.reorder_point,
               p.name as product_name, p.category, p.unit_price
        FROM inventory i
        LEFT JOIN products p ON i.product_id = p.product_id
    """, conn)
    conn.close()
    
    if df_sales.empty:
        print("[ML Pipeline Warning] Sales data is empty. Skipping anomaly detection.")
        return {}
        
    # ---------------------------------------------------------
    # 1. TRANSACTION ANOMALY DETECTION (Isolation Forest + Z-Score)
    # ---------------------------------------------------------
    df_sales['unit_price_calc'] = df_sales['sales_amount'] / np.maximum(1, df_sales['quantity'])
    df_sales['discount_pct'] = df_sales['discount'].fillna(0)
    
    features = ['sales_amount', 'quantity', 'discount_pct', 'profit', 'unit_price_calc']
    X_sales = df_sales[features].fillna(0)
    
    # Isolation Forest Model
    iso_forest = IsolationForest(contamination=0.03, random_state=42)
    df_sales['iso_forest_label'] = iso_forest.fit_predict(X_sales)
    df_sales['anomaly_score'] = np.round(-iso_forest.score_samples(X_sales), 4)
    
    # Statistical Z-Scores
    df_sales['sales_zscore'] = np.abs(stats.zscore(df_sales['sales_amount']))
    df_sales['discount_zscore'] = np.abs(stats.zscore(df_sales['discount_pct']))
    
    # Flag Anomalies
    df_sales['is_anomaly'] = (df_sales['iso_forest_label'] == -1) | (df_sales['sales_zscore'] > 3.0) | (df_sales['discount_zscore'] > 3.0)
    
    def generate_reason(row):
        reasons = []
        if row['sales_zscore'] > 3.0:
            reasons.append(f"Unusually high transaction value (${row['sales_amount']:,.2f}, Z-score: {row['sales_zscore']:.1f})")
        if row['discount_pct'] > 0.4:
            reasons.append(f"Excessive discount rate ({row['discount_pct']*100:.0f}%)")
        if row['profit'] < -500:
            reasons.append(f"Severe profit loss (${row['profit']:,.2f})")
        if row['quantity'] > 20:
            reasons.append(f"Bulk item order quantity ({row['quantity']} units)")
        if not reasons:
            reasons.append(f"High multi-dimensional Isolation Forest outlier score ({row['anomaly_score']:.3f})")
        return " | ".join(reasons)
        
    df_sales['anomaly_reason'] = df_sales.apply(generate_reason, axis=1)
    
    df_anomalies = df_sales[df_sales['is_anomaly'] == True].sort_values(by='anomaly_score', ascending=False)
    
    tx_anomaly_cols = [
        'id', 'order_id', 'order_date', 'customer_name', 'region', 
        'product_name', 'category', 'sales_amount', 'quantity', 
        'discount_pct', 'profit', 'anomaly_score', 'anomaly_reason'
    ]
    df_tx_export = df_anomalies[tx_anomaly_cols]
    tx_csv_path = os.path.join(output_dir, "anomalies", "transaction_anomalies.csv")
    df_tx_export.to_csv(tx_csv_path, index=False)
    print(f"[ML Pipeline] Flagged {len(df_tx_export)} transaction anomalies to {tx_csv_path}")

    # ---------------------------------------------------------
    # 2. INVENTORY ANOMALY DETECTION
    # ---------------------------------------------------------
    if not df_inv.empty:
        df_inv['stock_zscore'] = np.abs(stats.zscore(df_inv['stock_level']))
        df_inv['deficit'] = df_inv['reorder_point'] - df_inv['stock_level']
        
        df_inv['is_inv_anomaly'] = (df_inv['stock_level'] == 0) | (df_inv['deficit'] > 50) | (df_inv['stock_zscore'] > 3.0)
        
        def inv_reason(row):
            if row['stock_level'] == 0:
                return "Critical Out-of-Stock Deficit (0 units available)"
            if row['deficit'] > 50:
                return f"Severe Inventory Depletion (Stock: {row['stock_level']} vs Reorder Threshold: {row['reorder_point']})"
            if row['stock_zscore'] > 3.0:
                return f"Unusual Inventory Spike / Overstocking ({row['stock_level']} units)"
            return "Inventory Outlier Alert"
            
        df_inv['anomaly_reason'] = df_inv.apply(inv_reason, axis=1)
        df_inv_anomalies = df_inv[df_inv['is_inv_anomaly'] == True].sort_values(by='deficit', ascending=False)
        
        inv_csv_path = os.path.join(output_dir, "anomalies", "inventory_anomalies.csv")
        df_inv_anomalies.to_csv(inv_csv_path, index=False)
        print(f"[ML Pipeline] Flagged {len(df_inv_anomalies)} inventory anomalies to {inv_csv_path}")
    else:
        df_inv_anomalies = pd.DataFrame()

    # ---------------------------------------------------------
    # 3. METRICS JSON
    # ---------------------------------------------------------
    metrics = {
        "isolation_forest_model": {
            "contamination_rate": 0.03,
            "total_transactions_scanned": int(len(df_sales)),
            "flagged_transaction_anomalies": int(len(df_tx_export)),
            "anomaly_percentage": float(round((len(df_tx_export) / len(df_sales)) * 100, 2)),
            "total_at_risk_sales_amount": float(round(df_tx_export['sales_amount'].sum(), 2))
        },
        "inventory_anomalies": {
            "total_skus_scanned": int(len(df_inv)),
            "flagged_inventory_anomalies": int(len(df_inv_anomalies)),
            "critical_out_of_stock_count": int((df_inv['stock_level'] == 0).sum()) if not df_inv.empty else 0
        }
    }
    
    metrics_json_path = os.path.join(output_dir, "anomalies", "anomaly_metrics.json")
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    return metrics

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db = os.path.join(base_dir, "marketmind.db")
    out = os.path.join(base_dir, "outputs")
    run_anomaly_pipeline(db, out)
