
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules as generate_rules


DATA_PATH = "data/clean_retail_sales.csv"
OUTPUT_PATH = "data/association_recommendations.csv"
RULES_PATH = "data/product_association_rules.csv"


def load_sales_data():
    df = pd.read_csv(DATA_PATH)

    required = ["InvoiceNo", "StockCode", "Description", "Quantity"]
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.dropna(subset=["InvoiceNo", "StockCode", "Description"]).copy()
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df = df.dropna(subset=["Quantity"])

    # Exclude returns and cancelled/negative-quantity transactions.
    df = df[df["Quantity"] > 0]
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

    df["StockCode"] = df["StockCode"].astype(str)
    df["Description"] = df["Description"].astype(str).str.strip()

    return df


def build_basket_matrix(df):
    # Use invoices as baskets and product codes as columns.
    basket = df.pivot_table(
        index="InvoiceNo",
        columns="StockCode",
        values="Quantity",
        aggfunc="sum",
        fill_value=0,
    )

    # Apriori needs Boolean/presence data rather than quantities.
    basket = basket.gt(0)

    # Attach readable product names to product codes.
    product_names = (
        df.drop_duplicates("StockCode")
        .set_index("StockCode")["Description"]
        .to_dict()
    )

    return basket, product_names


def main():
    print("Loading sales data...")
    sales = load_sales_data()
    print(f"Usable sales rows: {len(sales):,}")

    print("Building invoice-product basket matrix...")
    basket, product_names = build_basket_matrix(sales)

    print(f"Invoices: {basket.shape[0]:,}")
    print(f"Products: {basket.shape[1]:,}")
    print(f"Basket matrix shape: {basket.shape}")

    # Remove products that occur in fewer than 0.5% of invoices.
    # This reduces computation on the large retail dataset.
    minimum_support = 0.005
    item_support = basket.mean(axis=0)
    selected_products = item_support[
        item_support >= minimum_support
    ].index

    basket = basket[selected_products]

    print(f"Products after support filtering: {basket.shape[1]:,}")

    print("Mining frequent itemsets...")
    itemsets = apriori(
        basket,
        min_support=minimum_support,
        use_colnames=True,
        max_len=3,
        low_memory=True,
    )

    if itemsets.empty:
        print("No frequent itemsets found. Try lowering minimum_support.")
        return

    itemsets["product_names"] = itemsets["itemsets"].apply(
        lambda items: [
            product_names.get(code, "Unknown product")
            for code in items
        ]
    )

    print(f"Frequent itemsets found: {len(itemsets):,}")

    print("Generating association rules...")
    rules = generate_rules(
        itemsets,
        metric="confidence",
        min_threshold=0.20,
    )

    if rules.empty:
        print("No association rules found with current thresholds.")
        return

    # Keep rules that recommend one product from a single product.
    rules = rules[
        rules["antecedents"].apply(len).eq(1)
        & rules["consequents"].apply(len).eq(1)
    ].copy()

    if rules.empty:
        print("No single-product-to-single-product rules found.")
        return

    rules["antecedent_code"] = rules["antecedents"].apply(
        lambda items: next(iter(items))
    )
    rules["consequent_code"] = rules["consequents"].apply(
        lambda items: next(iter(items))
    )

    rules["antecedent_product"] = rules["antecedent_code"].map(
        lambda code: product_names.get(code, "Unknown product")
    )
    rules["recommended_product"] = rules["consequent_code"].map(
        lambda code: product_names.get(code, "Unknown product")
    )

    # Rank rules by lift and confidence.
    rules = rules.sort_values(
        ["lift", "confidence", "support"],
        ascending=False,
    )

    display_columns = [
        "antecedent_code",
        "antecedent_product",
        "consequent_code",
        "recommended_product",
        "support",
        "confidence",
        "lift",
    ]

    rules[display_columns].to_csv(RULES_PATH, index=False)

    recommendations = rules[display_columns].rename(
        columns={
            "antecedent_code": "PurchasedStockCode",
            "antecedent_product": "PurchasedProduct",
            "consequent_code": "RecommendedStockCode",
            "recommended_product": "RecommendedProduct",
        }
    )

    recommendations.to_csv(OUTPUT_PATH, index=False)

    print("\nTop association rules:")
    print(recommendations.head(10).round(4).to_string(index=False))

    print(f"\nRules saved to: {RULES_PATH}")
    print(f"Cross-sell recommendations saved to: {OUTPUT_PATH}")
    print(f"Total rules saved: {len(recommendations):,}")


if __name__ == "__main__":
    main()
