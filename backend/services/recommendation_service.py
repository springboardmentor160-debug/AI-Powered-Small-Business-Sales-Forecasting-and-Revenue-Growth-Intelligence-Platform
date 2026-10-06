"""Generate actual MarketMind collaborative-filtering recommendations."""

from pathlib import Path
from typing import Any

import pandas as pd

from backend.models.recommendation.association_rules import (
    RULE_COLUMNS,
    AssociationRuleMiner,
    build_transaction_product_matrix,
)
from backend.models.recommendation.collaborative_filtering import (
    CollaborativeFilteringModel,
    build_customer_product_matrix,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SALES_PATH = PROJECT_ROOT / "data" / "processed" / "sales" / "cleaned_sales.csv"
CUSTOMERS_PATH = PROJECT_ROOT / "data" / "processed" / "customers" / "cleaned_customers.csv"
RECOMMENDATIONS_DIR = PROJECT_ROOT / "data" / "processed" / "recommendations"
MATRIX_PATH = RECOMMENDATIONS_DIR / "customer_product_matrix.csv"
SIMILARITY_PATH = RECOMMENDATIONS_DIR / "customer_similarity.csv"
RECOMMENDATIONS_PATH = RECOMMENDATIONS_DIR / "collaborative_recommendations.csv"
TRANSACTION_MATRIX_PATH = RECOMMENDATIONS_DIR / "transaction_product_matrix.csv"
FREQUENT_ITEMSETS_PATH = RECOMMENDATIONS_DIR / "frequent_itemsets.csv"
ASSOCIATION_RULES_PATH = RECOMMENDATIONS_DIR / "association_rules.csv"
CROSS_SELL_PATH = RECOMMENDATIONS_DIR / "cross_sell_recommendations.csv"
UPSELL_PATH = RECOMMENDATIONS_DIR / "upsell_opportunities.csv"
COMBINED_PATH = RECOMMENDATIONS_DIR / "combined_recommendations.csv"


def load_processed_sales() -> pd.DataFrame:
    """Load the existing cleaned Sales dataset without modifying it."""
    if not SALES_PATH.exists():
        raise FileNotFoundError(f"Processed sales dataset not found: {SALES_PATH}")
    sales = pd.read_csv(SALES_PATH)
    required_columns = {"customer_id", "product_name", "quantity"}
    missing_columns = required_columns.difference(sales.columns)
    if missing_columns:
        raise ValueError(f"Sales data is missing required columns: {sorted(missing_columns)}")
    return sales


def load_processed_customer_ids() -> pd.Index:
    """Load customer identifiers so customers without purchases remain representable."""
    if not CUSTOMERS_PATH.exists():
        raise FileNotFoundError(f"Processed customer dataset not found: {CUSTOMERS_PATH}")
    customers = pd.read_csv(CUSTOMERS_PATH)
    if "customer_id" not in customers.columns:
        raise ValueError("Customer data is missing required column: customer_id")
    return pd.Index(customers["customer_id"].dropna().astype(str).unique(), name="customer_id")


def build_model(
    sales: pd.DataFrame,
    customer_ids: pd.Index | list[str] | None = None,
) -> CollaborativeFilteringModel:
    """Build the customer-product matrix and fit cosine similarity."""
    matrix = build_customer_product_matrix(sales, customer_ids=customer_ids)
    return CollaborativeFilteringModel.fit(matrix)


def _write_model_outputs(model: CollaborativeFilteringModel) -> None:
    RECOMMENDATIONS_DIR.mkdir(parents=True, exist_ok=True)
    model.matrix.to_csv(MATRIX_PATH, index_label="customer_id")
    model.similarity.to_csv(SIMILARITY_PATH, index_label="customer_id")


def _empty_cross_sell() -> pd.DataFrame:
    return pd.DataFrame(
        columns=["customer_id", "rank", "recommended_product", "antecedents", "support", "confidence", "lift"]
    )


def _empty_upsell() -> pd.DataFrame:
    return pd.DataFrame(
        columns=["antecedents", "recommended_product", "antecedent_average_price", "recommended_average_price", "support", "confidence", "lift"]
    )


def _build_upsell_opportunities(sales: pd.DataFrame, rules: pd.DataFrame) -> pd.DataFrame:
    """Keep only rule consequents with a genuinely higher observed average price."""
    if rules.empty:
        return _empty_upsell()
    average_prices = sales.groupby("product_name")["unit_price"].mean().to_dict()
    opportunities = []
    for _, rule in rules.iterrows():
        antecedent_products = str(rule["antecedents"]).split(" + ")
        consequent_products = str(rule["consequents"]).split(" + ")
        antecedent_price = sum(average_prices.get(product, 0) for product in antecedent_products) / len(antecedent_products)
        for product in consequent_products:
            recommended_price = average_prices.get(product, 0)
            if recommended_price > antecedent_price:
                opportunities.append(
                    {
                        "antecedents": rule["antecedents"],
                        "recommended_product": product,
                        "antecedent_average_price": round(antecedent_price, 2),
                        "recommended_average_price": round(recommended_price, 2),
                        "support": rule["support"],
                        "confidence": rule["confidence"],
                        "lift": rule["lift"],
                    }
                )
    return pd.DataFrame(opportunities, columns=_empty_upsell().columns)


def generate_recommendations(top_n: int = 3) -> dict[str, Any]:
    """Generate collaborative, association-rule, cross-sell, and upsell outputs."""
    sales = load_processed_sales()
    customer_ids = load_processed_customer_ids()
    model = build_model(sales, customer_ids=customer_ids)
    _write_model_outputs(model)

    transaction_matrix = build_transaction_product_matrix(sales)
    rule_miner = AssociationRuleMiner()
    frequent_itemsets, rules = rule_miner.fit(transaction_matrix)
    TRANSACTION_MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    transaction_matrix.to_csv(TRANSACTION_MATRIX_PATH, index_label="transaction_id")
    frequent_itemsets.to_csv(FREQUENT_ITEMSETS_PATH, index=False)
    rules.to_csv(ASSOCIATION_RULES_PATH, index=False, columns=RULE_COLUMNS)

    recommendation_rows = []
    combined_rows = []
    cross_sell_rows = []
    customers_with_recommendations = 0
    for customer_id in model.matrix.index:
        customer_id = str(customer_id)
        recommendations = model.recommend_products(customer_id, top_n=top_n)
        if recommendations:
            customers_with_recommendations += 1
        for recommendation in recommendations:
            recommendation_row = {"customer_id": customer_id, **recommendation}
            recommendation_rows.append(recommendation_row)
            combined_rows.append(
                {
                    "customer_id": customer_id,
                    "recommendation_type": "personalized_collaborative",
                    **recommendation,
                    "antecedents": "",
                    "support": None,
                    "confidence": None,
                    "lift": None,
                }
            )
        purchased_products = model.matrix.loc[customer_id]
        purchased = purchased_products[purchased_products > 0].index
        cross_sell = rule_miner.cross_sell(purchased, rules, top_n=top_n)
        for rank, recommendation in enumerate(cross_sell, start=1):
            cross_sell_row = {"customer_id": customer_id, "rank": rank, **recommendation}
            cross_sell_rows.append(cross_sell_row)
            combined_rows.append(
                {
                    "customer_id": customer_id,
                    "recommendation_type": "association_cross_sell",
                    "recommended_product": recommendation["recommended_product"],
                    "rank": rank,
                    "recommendation_score": None,
                    "supporting_customer_count": None,
                    "antecedents": recommendation["antecedents"],
                    "support": recommendation["support"],
                    "confidence": recommendation["confidence"],
                    "lift": recommendation["lift"],
                }
            )

    recommendations = pd.DataFrame(
        recommendation_rows,
        columns=[
            "customer_id",
            "rank",
            "recommended_product",
            "recommendation_score",
            "supporting_customer_count",
        ],
    )
    recommendations.to_csv(RECOMMENDATIONS_PATH, index=False)
    cross_sell_output = pd.DataFrame(
        cross_sell_rows,
        columns=_empty_cross_sell().columns,
    )
    cross_sell_output.to_csv(CROSS_SELL_PATH, index=False)
    upsell_output = _build_upsell_opportunities(sales, rules)
    upsell_output.to_csv(UPSELL_PATH, index=False)
    combined_output = pd.DataFrame(
        combined_rows,
        columns=[
            "customer_id",
            "recommendation_type",
            "rank",
            "recommended_product",
            "recommendation_score",
            "supporting_customer_count",
            "antecedents",
            "support",
            "confidence",
            "lift",
        ],
    )
    combined_output.to_csv(COMBINED_PATH, index=False)

    target_customer_id = str(model.matrix.index[0])
    target_products = model.matrix.loc[target_customer_id]
    purchased_products = target_products[target_products > 0].sort_values(ascending=False)
    similar_customers = model.similar_customers(target_customer_id, top_n=5)
    target_recommendations = model.recommend_products(target_customer_id, top_n=top_n)

    return {
        "customers_processed": len(model.matrix.index),
        "products_in_matrix": len(model.matrix.columns),
        "matrix_shape": model.matrix.shape,
        "transactions_processed": len(transaction_matrix),
        "multi_product_transactions": int((transaction_matrix.sum(axis=1) > 1).sum()),
        "frequent_itemsets": len(frequent_itemsets),
        "association_rules": len(rules),
        "cross_sell_rows": len(cross_sell_output),
        "upsell_rows": len(upsell_output),
        "customers_with_recommendations": customers_with_recommendations,
        "target_customer_id": target_customer_id,
        "purchased_products": [str(product) for product in purchased_products.index],
        "similar_customers": similar_customers,
        "recommendations": target_recommendations,
        "output_paths": [
            MATRIX_PATH,
            SIMILARITY_PATH,
            RECOMMENDATIONS_PATH,
            TRANSACTION_MATRIX_PATH,
            FREQUENT_ITEMSETS_PATH,
            ASSOCIATION_RULES_PATH,
            CROSS_SELL_PATH,
            UPSELL_PATH,
            COMBINED_PATH,
        ],
    }


def main() -> None:
    """Run the recommender and print the actual example requested by the milestone."""
    result = generate_recommendations()
    print(f"Customers processed: {result['customers_processed']:,}")
    print(f"Products in matrix: {result['products_in_matrix']:,}")
    print(f"Customer-product matrix shape: {result['matrix_shape']}")
    print(f"Transactions processed: {result['transactions_processed']:,}")
    print(f"Multi-product transactions: {result['multi_product_transactions']:,}")
    print(f"Frequent itemsets: {result['frequent_itemsets']:,}")
    print(f"Association rules (lift > 1): {result['association_rules']:,}")
    print(f"Cross-sell rows: {result['cross_sell_rows']:,}")
    print(f"Upsell rows: {result['upsell_rows']:,}")
    print(f"Customers with recommendations: {result['customers_with_recommendations']:,}")
    print(f"Customer ID: {result['target_customer_id']}")
    print(f"Products already purchased: {result['purchased_products']}")
    print(f"Most similar customers: {result['similar_customers']}")
    print(f"Recommended products: {result['recommendations']}")
    for output_path in result["output_paths"]:
        print(f"Output: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
