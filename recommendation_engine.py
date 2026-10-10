
import pandas as pd
from pathlib import Path


DATA_DIR = Path("data")

COLLABORATIVE_FILE = DATA_DIR / "product_recommendations.csv"
ASSOCIATION_FILE = DATA_DIR / "association_recommendations.csv"


def load_recommendation_files():
    """Load and validate both recommendation outputs."""

    if not COLLABORATIVE_FILE.exists():
        raise FileNotFoundError(
            f"Missing file: {COLLABORATIVE_FILE}. "
            "Run product_recommendations.py first."
        )

    if not ASSOCIATION_FILE.exists():
        raise FileNotFoundError(
            f"Missing file: {ASSOCIATION_FILE}. "
            "Run association_rules.py first."
        )

    collaborative = pd.read_csv(COLLABORATIVE_FILE)
    association = pd.read_csv(ASSOCIATION_FILE)

    collaborative_columns = {
        "CustomerID",
        "StockCode",
        "Product",
        "RecommendationScore",
    }

    association_columns = {
        "PurchasedStockCode",
        "PurchasedProduct",
        "RecommendedStockCode",
        "RecommendedProduct",
        "support",
        "confidence",
        "lift",
    }

    if not collaborative_columns.issubset(collaborative.columns):
        raise ValueError(
            "Collaborative recommendations have unexpected columns."
        )

    if not association_columns.issubset(association.columns):
        raise ValueError(
            "Association recommendations have unexpected columns."
        )

    collaborative = collaborative.dropna(
        subset=["CustomerID", "StockCode", "Product"]
    ).copy()

    association = association.dropna(
        subset=[
            "PurchasedStockCode",
            "RecommendedStockCode",
            "RecommendedProduct",
        ]
    ).copy()

    collaborative["CustomerID"] = (
        collaborative["CustomerID"].astype(str)
    )

    collaborative["StockCode"] = collaborative["StockCode"].astype(str)
    association["PurchasedStockCode"] = (
        association["PurchasedStockCode"].astype(str)
    )
    association["RecommendedStockCode"] = (
        association["RecommendedStockCode"].astype(str)
    )

    for column in ["RecommendationScore"]:
        collaborative[column] = pd.to_numeric(
            collaborative[column], errors="coerce"
        )

    for column in ["support", "confidence", "lift"]:
        association[column] = pd.to_numeric(
            association[column], errors="coerce"
        )

    collaborative = collaborative.dropna(
        subset=["RecommendationScore"]
    )
    association = association.dropna(
        subset=["support", "confidence", "lift"]
    )

    return collaborative, association


def get_personalized_recommendations(
    customer_id,
    collaborative,
    top_n=5,
):
    """Return recommendations generated for one customer."""

    customer_id = str(customer_id)

    results = collaborative[
        collaborative["CustomerID"] == customer_id
    ].copy()

    if results.empty:
        return pd.DataFrame(
            columns=[
                "Product",
                "RecommendationScore",
                "Method",
            ]
        )

    results = results.sort_values(
        "RecommendationScore",
        ascending=False,
    ).head(top_n)

    results["Method"] = "Collaborative Filtering"

    return results[
        ["Product", "RecommendationScore", "Method"]
    ].reset_index(drop=True)


def get_frequently_bought_together(
    stock_code,
    association,
    top_n=5,
    min_confidence=0.20,
    min_support=0.005,
):
    """Recommend products associated with a purchased product."""

    stock_code = str(stock_code)

    results = association[
        (association["PurchasedStockCode"] == stock_code)
        & (association["confidence"] >= min_confidence)
        & (association["support"] >= min_support)
    ].copy()

    if results.empty:
        return pd.DataFrame(
            columns=[
                "Product",
                "Support",
                "Confidence",
                "Lift",
                "Method",
            ]
        )

    results = results.sort_values(
        ["lift", "confidence", "support"],
        ascending=False,
    ).head(top_n)

    results = results.rename(
        columns={
            "RecommendedProduct": "Product",
            "support": "Support",
            "confidence": "Confidence",
            "lift": "Lift",
        }
    )

    results["Method"] = "Association Rules"

    return results[
        ["Product", "Support", "Confidence", "Lift", "Method"]
    ].reset_index(drop=True)


def main():
    print("Loading recommendation files...")

    collaborative, association = load_recommendation_files()

    print(
        f"Collaborative recommendations loaded: "
        f"{len(collaborative):,}"
    )
    print(
        f"Association rules loaded: {len(association):,}"
    )

    # Test a customer present in the collaborative output.
    sample_customer = collaborative["CustomerID"].iloc[0]

    personalized = get_personalized_recommendations(
        sample_customer,
        collaborative,
        top_n=5,
    )

    print(f"\nPersonalized recommendations for customer {sample_customer}:")
    if personalized.empty:
        print("No recommendations available.")
    else:
        print(personalized.to_string(index=False))

    # Test association recommendations using a purchased product
    # from the association rules output.
    sample_stock_code = association["PurchasedStockCode"].iloc[0]

    frequently_bought = get_frequently_bought_together(
        sample_stock_code,
        association,
        top_n=5,
    )

    print(
        f"\nFrequently bought together with stock code "
        f"{sample_stock_code}:"
    )

    if frequently_bought.empty:
        print("No matching association recommendations.")
    else:
        print(frequently_bought.to_string(index=False))

    print("\nRecommendation engine test completed.")


if __name__ == "__main__":
    main()
