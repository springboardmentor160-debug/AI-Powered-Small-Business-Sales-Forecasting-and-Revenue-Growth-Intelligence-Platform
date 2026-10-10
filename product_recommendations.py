
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix


DATA_PATH = "data/clean_retail_sales.csv"
OUTPUT_PATH = "data/product_recommendations.csv"


def load_sales_data():
    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "CustomerID",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceNo",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Remove rows without customer or product information.
    df = df.dropna(
        subset=["CustomerID", "StockCode", "Description"]
    ).copy()

    # Convert quantities to numeric and exclude returns/non-positive sales.
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )
    df = df.dropna(subset=["Quantity"])
    df = df[df["Quantity"] > 0]

    # Keep product identifiers consistent.
    df["CustomerID"] = df["CustomerID"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    df["Description"] = df["Description"].astype(str).str.strip()

    return df


def build_customer_product_matrix(df):
    # Aggregate quantity purchased by each customer for each product.
    matrix = df.pivot_table(
        index="CustomerID",
        columns="StockCode",
        values="Quantity",
        aggfunc="sum",
        fill_value=0,
    )

    # Keep the readable product descriptions for recommendation output.
    product_names = (
        df.drop_duplicates("StockCode")
        .set_index("StockCode")["Description"]
        .to_dict()
    )

    return matrix, product_names


def recommend_products(
    customer_id,
    matrix,
    product_names,
    top_n=5,
    neighbors=10,
):
    customer_id = str(customer_id)

    if customer_id not in matrix.index:
        return pd.DataFrame(
            columns=["StockCode", "Product", "RecommendationScore"]
        )

    # Calculate similarity for the target customer against all customers.
    customer_position = matrix.index.get_loc(customer_id)
    similarities = cosine_similarity(
        matrix.iloc[[customer_position]],
        matrix,
    )[0]

    similarity_series = pd.Series(
        similarities,
        index=matrix.index,
    ).drop(index=customer_id)

    similar_customers = similarity_series[
        similarity_series > 0
    ].nlargest(neighbors)

    if similar_customers.empty:
        return pd.DataFrame(
            columns=["StockCode", "Product", "RecommendationScore"]
        )

    # Weight neighbors' purchases by how similar they are to the target.
    neighbor_purchases = matrix.loc[
        similar_customers.index
    ].mul(similar_customers, axis=0)

    scores = neighbor_purchases.sum(axis=0)

    # Never recommend products the target customer already purchased.
    already_bought = matrix.loc[customer_id] > 0
    scores = scores[~already_bought]

    scores = scores[scores > 0].nlargest(top_n)

    recommendations = pd.DataFrame({
        "StockCode": scores.index,
        "Product": [
            product_names.get(code, "Unknown product")
            for code in scores.index
        ],
        "RecommendationScore": scores.values,
    })

    return recommendations.reset_index(drop=True)


def main():
    print("Loading sales data...")
    sales = load_sales_data()

    print(f"Usable sales rows: {len(sales):,}")

    print("Building customer-product matrix...")
    matrix, product_names = build_customer_product_matrix(sales)

    print(f"Customers: {matrix.shape[0]:,}")
    print(f"Products: {matrix.shape[1]:,}")
    print(f"Matrix shape: {matrix.shape}")

    # A sparse matrix avoids calculating a full customer-by-customer
    # similarity matrix, which would be too large for this dataset.
    customer_ids = matrix.index.tolist()
    sparse_matrix = csr_matrix(matrix.values)

    print("Generating recommendations for a sample customer...")
    sample_customer = customer_ids[0]

    recommendations = recommend_products(
        sample_customer,
        matrix,
        product_names,
        top_n=5,
        neighbors=10,
    )

    print(f"\nSample customer: {sample_customer}")
    print("\nRecommended products:")
    if recommendations.empty:
        print("No recommendations available for this customer.")
    else:
        print(recommendations.to_string(index=False))

    # Save recommendations for every customer.
    # Process one target at a time to avoid storing a huge similarity matrix.
    all_recommendations = []

    for i, customer_id in enumerate(customer_ids, start=1):
        scores = cosine_similarity(
            sparse_matrix.getrow(i - 1),
            sparse_matrix,
        ).ravel()

        scores[i - 1] = 0

        neighbor_positions = scores.argsort()[-10:][::-1]
        neighbor_positions = [
            pos for pos in neighbor_positions if scores[pos] > 0
        ]

        if not neighbor_positions:
            continue

        neighbor_ids = matrix.index[neighbor_positions]
        neighbor_weights = scores[neighbor_positions]

        weighted_purchases = matrix.loc[neighbor_ids].mul(
            neighbor_weights, axis=0
        ).sum(axis=0)

        purchased = matrix.loc[customer_id] > 0
        weighted_purchases = weighted_purchases[~purchased]
        weighted_purchases = weighted_purchases[
            weighted_purchases > 0
        ].nlargest(5)

        for stock_code, score in weighted_purchases.items():
            all_recommendations.append({
                "CustomerID": customer_id,
                "StockCode": stock_code,
                "Product": product_names.get(
                    stock_code, "Unknown product"
                ),
                "RecommendationScore": round(float(score), 4),
            })

        if i % 500 == 0:
            print(f"Processed {i:,}/{len(customer_ids):,} customers")

    output = pd.DataFrame(all_recommendations)
    output.to_csv(OUTPUT_PATH, index=False)

    print(f"\nRecommendations saved to {OUTPUT_PATH}")
    print(f"Total recommendations generated: {len(output):,}")


if __name__ == "__main__":
    main()
