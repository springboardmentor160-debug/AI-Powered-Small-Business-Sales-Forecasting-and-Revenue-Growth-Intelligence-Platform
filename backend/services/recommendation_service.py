"""Generate actual MarketMind collaborative-filtering recommendations."""

from pathlib import Path
from typing import Any

import pandas as pd

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


def generate_recommendations(top_n: int = 3) -> dict[str, Any]:
    """Generate recommendations for every known customer and print one actual example."""
    sales = load_processed_sales()
    customer_ids = load_processed_customer_ids()
    model = build_model(sales, customer_ids=customer_ids)
    _write_model_outputs(model)

    recommendation_rows = []
    customers_with_recommendations = 0
    for customer_id in model.matrix.index:
        recommendations = model.recommend_products(str(customer_id), top_n=top_n)
        if recommendations:
            customers_with_recommendations += 1
        for recommendation in recommendations:
            recommendation_rows.append(
                {
                    "customer_id": customer_id,
                    **recommendation,
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

    target_customer_id = str(model.matrix.index[0])
    target_products = model.matrix.loc[target_customer_id]
    purchased_products = target_products[target_products > 0].sort_values(ascending=False)
    similar_customers = model.similar_customers(target_customer_id, top_n=5)
    target_recommendations = model.recommend_products(target_customer_id, top_n=top_n)

    return {
        "customers_processed": len(model.matrix.index),
        "products_in_matrix": len(model.matrix.columns),
        "matrix_shape": model.matrix.shape,
        "customers_with_recommendations": customers_with_recommendations,
        "target_customer_id": target_customer_id,
        "purchased_products": [str(product) for product in purchased_products.index],
        "similar_customers": similar_customers,
        "recommendations": target_recommendations,
        "output_paths": [MATRIX_PATH, SIMILARITY_PATH, RECOMMENDATIONS_PATH],
    }


def main() -> None:
    """Run the recommender and print the actual example requested by the milestone."""
    result = generate_recommendations()
    print(f"Customers processed: {result['customers_processed']:,}")
    print(f"Products in matrix: {result['products_in_matrix']:,}")
    print(f"Customer-product matrix shape: {result['matrix_shape']}")
    print(f"Customers with recommendations: {result['customers_with_recommendations']:,}")
    print(f"Customer ID: {result['target_customer_id']}")
    print(f"Products already purchased: {result['purchased_products']}")
    print(f"Most similar customers: {result['similar_customers']}")
    print(f"Recommended products: {result['recommendations']}")
    for output_path in result["output_paths"]:
        print(f"Output: {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
