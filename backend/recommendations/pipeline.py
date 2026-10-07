import os
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

try:
    from mlxtend.frequent_patterns import apriori, association_rules
    HAS_MLXTEND = True
except ImportError:
    HAS_MLXTEND = False

RAW_SALES_PATH = os.path.join("data", "processed", "clean_sales_data.csv")
MATRIX_CSV_PATH = os.path.join("data", "processed", "customer_product_matrix.csv")


def load_sales_data(filepath: str = RAW_SALES_PATH) -> pd.DataFrame:
    """Load and validate cleaned sales transaction data."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Sales data file not found at {filepath}")
    df = pd.read_csv(filepath)
    if "total_amount" not in df.columns:
        df["total_amount"] = df["quantity"] * df["unit_price"]
    return df


def build_customer_product_matrix(sales_df: pd.DataFrame, persist_path: Optional[str] = MATRIX_CSV_PATH) -> pd.DataFrame:
    """
    Build customer-product matrix:
    - Rows: customer_id
    - Columns: product_name
    - Values: quantity (sum)
    - Fill missing: 0
    """
    if sales_df.empty:
        return pd.DataFrame()

    df = sales_df.copy()
    df["quantity"] = df["quantity"].astype(float)
    matrix = df.pivot_table(
        index="customer_id",
        columns="product_name",
        values="quantity",
        aggfunc="sum",
        fill_value=0.0
    )

    if persist_path:
        os.makedirs(os.path.dirname(persist_path), exist_ok=True)
        matrix.to_csv(persist_path)

    return matrix


def calculate_customer_similarity(matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate pairwise cosine similarity between customers based on product purchase quantities.
    Returns square DataFrame indexed and columned by customer_id with values in [0, 1].
    """
    if matrix.empty:
        return pd.DataFrame()

    sim_values = cosine_similarity(matrix.values)
    sim_df = pd.DataFrame(
        sim_values,
        index=matrix.index,
        columns=matrix.index
    )
    return sim_df


def recommend_products_collaborative(
    customer_id: str,
    top_n: int = 3,
    sales_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    User-based Collaborative Filtering Recommender:
    1. Identify target customer in matrix.
    2. Compute cosine similarity with other customers.
    3. Exclude the target customer and isolate peers with similarity > 0.
    4. Aggregate products purchased by similar peers, weighted by similarity.
    5. Filter out products already purchased by target customer.
    6. Rank remaining unseen products and return top N recommendations.
    """
    if sales_df is None:
        sales_df = load_sales_data()

    matrix = build_customer_product_matrix(sales_df)
    if matrix.empty:
        return {
            "customer_id": customer_id,
            "recommendations": [],
            "method": "collaborative_filtering",
            "message": "Sales dataset is empty."
        }

    if customer_id not in matrix.index:
        return {
            "customer_id": customer_id,
            "recommendations": [],
            "method": "collaborative_filtering",
            "message": f"Customer '{customer_id}' not found in purchase history."
        }

    target_history = matrix.loc[customer_id]
    already_purchased = set(target_history[target_history > 0].index)

    sim_df = calculate_customer_similarity(matrix)
    peer_similarities = sim_df.loc[customer_id].drop(index=customer_id)

    # Filter peers with strictly positive similarity
    valid_peers = peer_similarities[peer_similarities > 0.0].sort_values(ascending=False)

    if valid_peers.empty:
        return {
            "customer_id": customer_id,
            "recommendations": [],
            "method": "collaborative_filtering",
            "message": "No peer customers with similar buying patterns found (zero similarity).",
            "purchased_products": list(already_purchased)
        }

    # Aggregate products purchased by peers weighted by peer similarity
    candidate_scores: Dict[str, float] = {}
    supporting_details: Dict[str, Dict[str, Any]] = {}

    for peer_id, sim_weight in valid_peers.items():
        peer_purchases = matrix.loc[peer_id]
        for prod, qty in peer_purchases.items():
            if qty > 0 and prod not in already_purchased:
                weighted_score = float(qty * sim_weight)
                candidate_scores[prod] = candidate_scores.get(prod, 0.0) + weighted_score
                if prod not in supporting_details:
                    supporting_details[prod] = {
                        "supporting_quantity": float(qty),
                        "similar_customers": [peer_id],
                        "max_similarity": round(float(sim_weight), 4)
                    }
                else:
                    supporting_details[prod]["supporting_quantity"] += float(qty)
                    supporting_details[prod]["similar_customers"].append(peer_id)

    if not candidate_scores:
        return {
            "customer_id": customer_id,
            "recommendations": [],
            "method": "collaborative_filtering",
            "message": "Similar peers exist, but no unseen products remain to recommend.",
            "purchased_products": list(already_purchased),
            "similar_peers": valid_peers.to_dict()
        }

    # Sort descending by score
    sorted_candidates = sorted(candidate_scores.items(), key=lambda item: item[1], reverse=True)[:top_n]

    recommendations = [
        {
            "product_name": prod,
            "recommendation_score": round(score, 4),
            "supporting_quantity": supporting_details[prod]["supporting_quantity"],
            "supporting_peers": supporting_details[prod]["similar_customers"],
            "recommendation_method": "collaborative_filtering"
        }
        for prod, score in sorted_candidates
    ]

    return {
        "customer_id": customer_id,
        "recommendations": recommendations,
        "method": "collaborative_filtering",
        "purchased_products": list(already_purchased),
        "similar_peers": {p: round(float(s), 4) for p, s in valid_peers.items()}
    }


def mine_association_rules(
    sales_df: pd.DataFrame,
    min_support: float = 0.01,
    min_confidence: float = 0.1
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Mine association rules from order baskets using Apriori algorithm:
    1. Group products by order_id transaction identifier.
    2. Convert to binary basket indicator matrix.
    3. Execute Apriori to extract frequent itemsets.
    4. Derive association rules evaluated by support, confidence, and lift.
    5. Handle honest limitations if baskets contain only single items.
    """
    if not HAS_MLXTEND:
        return pd.DataFrame(), {
            "status": "unavailable",
            "message": "mlxtend is not installed."
        }

    if sales_df.empty:
        return pd.DataFrame(), {
            "status": "empty_data",
            "message": "Sales dataset is empty."
        }

    # Basket matrix: order_id x product_name
    basket = sales_df.groupby(["order_id", "product_name"])["quantity"].sum().unstack().fillna(0)
    basket_binary = (basket > 0).astype(bool)

    frequent_itemsets = apriori(basket_binary, min_support=min_support, use_colnames=True)

    if frequent_itemsets.empty:
        return pd.DataFrame(), {
            "status": "no_itemsets",
            "frequent_itemsets_count": 0,
            "rules_count": 0,
            "message": f"No frequent itemsets found at min_support={min_support}."
        }

    # Check if any itemset has length >= 2
    max_len = frequent_itemsets["itemsets"].apply(len).max()
    if max_len < 2:
        return pd.DataFrame(), {
            "status": "single_item_orders_only",
            "frequent_itemsets_count": len(frequent_itemsets),
            "rules_count": 0,
            "message": "All orders in current transaction dataset contain only 1 item. Association rules require multi-item baskets."
        }

    try:
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    except Exception as e:
        return pd.DataFrame(), {
            "status": "error",
            "rules_count": 0,
            "message": f"Rule mining error: {str(e)}"
        }

    return rules, {
        "status": "success",
        "frequent_itemsets_count": len(frequent_itemsets),
        "rules_count": len(rules),
        "min_support": min_support,
        "min_confidence": min_confidence
    }


def recommend_products_association(
    customer_id: str,
    top_n: int = 3,
    sales_df: Optional[pd.DataFrame] = None,
    min_support: float = 0.01,
    min_confidence: float = 0.1
) -> Dict[str, Any]:
    """
    Market Basket Association Rule Recommender:
    1. Determine products already purchased by target customer.
    2. Match purchased products against antecedents of mined association rules.
    3. Filter out consequents that target customer has already purchased.
    4. Rank remaining consequents by confidence and lift.
    5. Return top N recommendations.
    """
    if sales_df is None:
        sales_df = load_sales_data()

    if customer_id not in sales_df["customer_id"].values:
        return {
            "customer_id": customer_id,
            "recommendations": [],
            "method": "association_rules",
            "message": f"Customer '{customer_id}' not found in purchase history."
        }

    cust_sales = sales_df[sales_df["customer_id"] == customer_id]
    already_purchased = set(cust_sales["product_name"].unique())

    rules, metadata = mine_association_rules(sales_df, min_support=min_support, min_confidence=min_confidence)

    if rules.empty:
        return {
            "customer_id": customer_id,
            "recommendations": [],
            "method": "association_rules",
            "message": metadata.get("message", "No association rules available."),
            "purchased_products": list(already_purchased),
            "metadata": metadata
        }

    candidate_recs: Dict[str, Dict[str, Any]] = {}

    for _, rule in rules.iterrows():
        antecedents = set(rule["antecedents"])
        consequents = set(rule["consequents"])

        # If customer purchased any item in antecedent
        if antecedents.intersection(already_purchased):
            for item in consequents:
                if item not in already_purchased:
                    score = float(rule["confidence"] * rule.get("lift", 1.0))
                    if item not in candidate_recs or score > candidate_recs[item]["recommendation_score"]:
                        candidate_recs[item] = {
                            "product_name": item,
                            "recommendation_score": round(score, 4),
                            "confidence": round(float(rule["confidence"]), 4),
                            "lift": round(float(rule.get("lift", 1.0)), 4),
                            "antecedents": list(antecedents),
                            "recommendation_method": "association_rules"
                        }

    if not candidate_recs:
        return {
            "customer_id": customer_id,
            "recommendations": [],
            "method": "association_rules",
            "message": "No associated unseen products found for customer purchase history.",
            "purchased_products": list(already_purchased)
        }

    sorted_recs = sorted(candidate_recs.values(), key=lambda x: x["recommendation_score"], reverse=True)[:top_n]

    return {
        "customer_id": customer_id,
        "recommendations": sorted_recs,
        "method": "association_rules",
        "purchased_products": list(already_purchased),
        "metadata": metadata
    }


def recommend_products(
    customer_id: str,
    top_n: int = 3,
    sales_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Combined Hybrid Recommendation Engine:
    Integrates Collaborative Filtering ("Customers like you bought this") and
    Association Rules ("Frequently bought together"):
    1. Runs both algorithms on real transaction history.
    2. Combines candidate item sets transparently.
    3. If an item is identified by BOTH methods:
       - Marked method: 'both'
       - Combined score boosted with rank synergy.
    4. If identified by only one method:
       - Retains single-source method label ('collaborative_filtering' or 'association_rules').
    5. Sorts descending and returns top N recommendations.
    6. Excludes any product previously purchased by the target customer.
    """
    if sales_df is None:
        sales_df = load_sales_data()

    collab_result = recommend_products_collaborative(customer_id, top_n=top_n * 2, sales_df=sales_df)
    assoc_result = recommend_products_association(customer_id, top_n=top_n * 2, sales_df=sales_df)

    purchased_products = collab_result.get("purchased_products") or assoc_result.get("purchased_products") or []

    combined_map: Dict[str, Dict[str, Any]] = {}

    # Process Collaborative Filtering results
    collab_recs = collab_result.get("recommendations", [])
    max_collab_score = max([r["recommendation_score"] for r in collab_recs], default=1.0) or 1.0

    for r in collab_recs:
        prod = r["product_name"]
        norm_score = r["recommendation_score"] / max_collab_score
        combined_map[prod] = {
            "product_name": prod,
            "recommendation_score": round(norm_score, 4),
            "recommendation_method": "collaborative_filtering",
            "collaborative_score": r["recommendation_score"],
            "supporting_quantity": r.get("supporting_quantity", 0.0),
            "supporting_peers": r.get("supporting_peers", [])
        }

    # Process Association Rules results
    assoc_recs = assoc_result.get("recommendations", [])
    max_assoc_score = max([r["recommendation_score"] for r in assoc_recs], default=1.0) or 1.0

    for r in assoc_recs:
        prod = r["product_name"]
        norm_score = r["recommendation_score"] / max_assoc_score
        if prod in combined_map:
            # Item found by BOTH approaches: boost combined score and update method
            combined_map[prod]["recommendation_method"] = "both"
            combined_map[prod]["recommendation_score"] = round(
                combined_map[prod]["recommendation_score"] + norm_score + 0.5, 4
            )
            combined_map[prod]["association_confidence"] = r.get("confidence", 0.0)
            combined_map[prod]["association_lift"] = r.get("lift", 1.0)
        else:
            combined_map[prod] = {
                "product_name": prod,
                "recommendation_score": round(norm_score, 4),
                "recommendation_method": "association_rules",
                "association_confidence": r.get("confidence", 0.0),
                "association_lift": r.get("lift", 1.0),
                "antecedents": r.get("antecedents", [])
            }

    sorted_recs = sorted(combined_map.values(), key=lambda x: x["recommendation_score"], reverse=True)[:top_n]

    status_message = "Recommendations generated successfully."
    if not sorted_recs:
        if collab_result.get("message") and assoc_result.get("message"):
            status_message = f"CF: {collab_result['message']} | Association: {assoc_result['message']}"
        elif collab_result.get("message"):
            status_message = collab_result["message"]
        else:
            status_message = "No unseen recommendations available for this customer profile."

    return {
        "customer_id": customer_id,
        "recommendations": sorted_recs,
        "method": "combined",
        "purchased_products": purchased_products,
        "collaborative_summary": {
            "similar_peers": collab_result.get("similar_peers", {}),
            "recommendations_found": len(collab_recs)
        },
        "association_summary": {
            "rules_metadata": assoc_result.get("metadata", {}),
            "recommendations_found": len(assoc_recs)
        },
        "message": status_message
    }
