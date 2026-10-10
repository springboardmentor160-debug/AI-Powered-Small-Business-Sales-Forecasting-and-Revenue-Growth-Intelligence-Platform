"""
MarketMind AI — Milestone 3: Product Recommendation Engine
Combines Collaborative Filtering (User-Item Cosine Similarity) and 
Association Rule Mining (Apriori Algorithm for Cross-Sell & Upsell Opportunities).
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from sklearn.metrics.pairwise import cosine_similarity

def run_recommendation_pipeline(db_path: str, output_dir: str) -> Dict[str, Any]:
    print("[ML Pipeline] Starting Product Recommendation Engine...")
    os.makedirs(os.path.join(output_dir, "recommendations"), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    df_sales = pd.read_sql_query("SELECT order_id, customer_id, product_id, sales_amount, quantity FROM sales", conn)
    df_products = pd.read_sql_query("SELECT product_id, name as product_name, category, sub_category, unit_price FROM products", conn)
    conn.close()
    
    if df_sales.empty:
        print("[ML Pipeline Warning] Sales data is empty. Skipping recommendations.")
        return {}
    
    # ---------------------------------------------------------
    # 1. COLLABORATIVE FILTERING (User-Item Interaction Matrix)
    # ---------------------------------------------------------
    user_item_matrix = df_sales.pivot_table(
        index='customer_id', 
        columns='product_id', 
        values='quantity', 
        aggfunc='sum', 
        fill_value=0
    )
    
    # Cosine Similarity between Customers
    user_sim = cosine_similarity(user_item_matrix)
    user_sim_df = pd.DataFrame(user_sim, index=user_item_matrix.index, columns=user_item_matrix.index)
    
    product_dict = df_products.set_index('product_id').to_dict('index')
    
    customer_recs = []
    top_customers = user_item_matrix.index[:500]  # Process top active customers
    
    for customer_id in top_customers:
        # Find top 5 similar customers
        sim_scores = user_sim_df[customer_id].drop(customer_id).sort_values(ascending=False)
        top_similar_users = sim_scores.head(5).index
        
        # Products purchased by similar users but not yet by target customer
        target_purchased = set(user_item_matrix.loc[customer_id][user_item_matrix.loc[customer_id] > 0].index)
        
        recs = {}
        for sim_user in top_similar_users:
            sim_weight = sim_scores[sim_user]
            sim_purchased = user_item_matrix.loc[sim_user][user_item_matrix.loc[sim_user] > 0]
            for prod_id, qty in sim_purchased.items():
                if prod_id not in target_purchased:
                    recs[prod_id] = recs.get(prod_id, 0.0) + (qty * sim_weight)
        
        sorted_recs = sorted(recs.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for rank, (prod_id, score) in enumerate(sorted_recs, 1):
            p_info = product_dict.get(prod_id, {})
            customer_recs.append({
                "customer_id": customer_id,
                "rank": rank,
                "recommended_product_id": prod_id,
                "product_name": p_info.get("product_name", "Unknown Product"),
                "category": p_info.get("category", "General"),
                "sub_category": p_info.get("sub_category", "General"),
                "score": round(float(score), 4),
                "recommendation_type": "Collaborative Filtering"
            })
            
    df_recs = pd.DataFrame(customer_recs)
    recs_csv_path = os.path.join(output_dir, "recommendations", "customer_recommendations.csv")
    df_recs.to_csv(recs_csv_path, index=False)
    print(f"[ML Pipeline] Saved {len(df_recs)} customer recommendations to {recs_csv_path}")

    # ---------------------------------------------------------
    # 2. ASSOCIATION RULE MINING (Market Basket Analysis)
    # ---------------------------------------------------------
    order_baskets = df_sales.groupby('order_id')['product_id'].apply(lambda x: list(set(x))).tolist()
    total_orders = len(order_baskets)
    
    item_counts = {}
    pair_counts = {}
    
    for basket in order_baskets:
        for item in basket:
            item_counts[item] = item_counts.get(item, 0) + 1
        for i in range(len(basket)):
            for j in range(i + 1, len(basket)):
                item_a, item_b = sorted([basket[i], basket[j]])
                pair_counts[(item_a, item_b)] = pair_counts.get((item_a, item_b), 0) + 1
                
    rules = []
    min_support_count = max(2, int(total_orders * 0.0005))
    
    for (item_a, item_b), count in pair_counts.items():
        if count >= min_support_count:
            support_ab = count / total_orders
            support_a = item_counts[item_a] / total_orders
            support_b = item_counts[item_b] / total_orders
            
            conf_a_b = support_ab / support_a
            lift_a_b = conf_a_b / support_b
            if conf_a_b >= 0.05 and lift_a_b > 1.0:
                p_a = product_dict.get(item_a, {})
                p_b = product_dict.get(item_b, {})
                rules.append({
                    "antecedent_id": item_a,
                    "antecedent_name": p_a.get("product_name", item_a),
                    "consequent_id": item_b,
                    "consequent_name": p_b.get("product_name", item_b),
                    "support": round(support_ab, 5),
                    "confidence": round(conf_a_b, 4),
                    "lift": round(lift_a_b, 3),
                    "recommendation_type": "Cross-Sell / Frequently Bought Together"
                })
                
            conf_b_a = support_ab / support_b
            lift_b_a = conf_b_a / support_a
            if conf_b_a >= 0.05 and lift_b_a > 1.0:
                p_a = product_dict.get(item_a, {})
                p_b = product_dict.get(item_b, {})
                rules.append({
                    "antecedent_id": item_b,
                    "antecedent_name": p_b.get("product_name", item_b),
                    "consequent_id": item_a,
                    "consequent_name": p_a.get("product_name", item_a),
                    "support": round(support_ab, 5),
                    "confidence": round(conf_b_a, 4),
                    "lift": round(lift_b_a, 3),
                    "recommendation_type": "Cross-Sell / Frequently Bought Together"
                })

    df_rules = pd.DataFrame(rules).sort_values(by=['lift', 'confidence'], ascending=False).head(200)
    rules_csv_path = os.path.join(output_dir, "recommendations", "association_rules.csv")
    df_rules.to_csv(rules_csv_path, index=False)
    print(f"[ML Pipeline] Saved {len(df_rules)} association rules to {rules_csv_path}")
    
    # ---------------------------------------------------------
    # 3. METRICS JSON
    # ---------------------------------------------------------
    metrics = {
        "collaborative_filtering": {
            "num_customers_profiled": int(len(user_item_matrix)),
            "num_products_catalog": int(len(df_products)),
            "total_recommendations_generated": int(len(df_recs)),
            "avg_similarity_score": float(np.mean(user_sim[user_sim < 1.0]))
        },
        "association_rule_mining": {
            "total_baskets_analyzed": int(total_orders),
            "frequent_rules_count": int(len(df_rules)),
            "avg_confidence": float(df_rules['confidence'].mean()) if not df_rules.empty else 0.0,
            "max_lift": float(df_rules['lift'].max()) if not df_rules.empty else 1.0
        }
    }
    
    metrics_json_path = os.path.join(output_dir, "recommendations", "recommendation_metrics.json")
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    return metrics

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db = os.path.join(base_dir, "marketmind.db")
    out = os.path.join(base_dir, "outputs")
    run_recommendation_pipeline(db, out)
