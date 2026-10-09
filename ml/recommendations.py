"""
Product Recommendations -- MarketMind AI
Milestone 3, Day 1-2: Collaborative Filtering

Builds a customer-product matrix from online_retail_prepped.csv and
recommends products to a customer based on what similar customers bought.

    python recommendations.py
"""
from pathlib import Path

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

ML_DIR = Path(__file__).resolve().parent
DATA_FILE = ML_DIR.parent / "datasets" / "processed" / "online_retail_prepped.csv"

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
df = pd.read_csv(DATA_FILE)

# Description (human-readable) is used instead of StockCode (opaque ID).
# FIX: 700+ names have trailing spaces, which creates "duplicate" products
# ("X" vs "X ") -- strip them so each product appears once.
df["Description"] = df["Description"].astype(str).str.strip()

# ---------------------------------------------------------------------------
# 2. Customer-product matrix (4,338 customers x ~3,800 products)
# ---------------------------------------------------------------------------
customer_product_matrix = df.pivot_table(
    index="CustomerID",
    columns="Description",
    values="Quantity",
    aggfunc="sum",
    fill_value=0,
)
print(f"Matrix shape: {customer_product_matrix.shape}")

# ---------------------------------------------------------------------------
# 3. Similarity between customers
# ---------------------------------------------------------------------------
similarity_df = pd.DataFrame(
    cosine_similarity(customer_product_matrix),
    index=customer_product_matrix.index,
    columns=customer_product_matrix.index,
)


# ---------------------------------------------------------------------------
# 4. Recommend products for a customer
# ---------------------------------------------------------------------------
def recommend_products(customer_id, top_n=5, n_similar=5):
    if customer_id not in similarity_df.index:
        return pd.Series(dtype="int64")

    # FIX: drop the customer BY LABEL instead of skipping row 0 -- if another
    # customer has an identical basket (similarity 1.0), [1:] could skip the
    # wrong row and recommend from the customer themself.
    similar_ids = (
        similarity_df[customer_id].drop(customer_id)
        .sort_values(ascending=False).head(n_similar).index
    )
    bought_by_similar = customer_product_matrix.loc[similar_ids].sum()
    already_bought = customer_product_matrix.loc[customer_id]

    candidates = bought_by_similar[(already_bought == 0) & (bought_by_similar > 0)]
    return candidates.sort_values(ascending=False).head(top_n)


# ---------------------------------------------------------------------------
# 5. Demo (17850 is a typical customer; 12346 is the bulk-order outlier
#    excluded from segmentation in M2, so not a good demo)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_customer = 17850
    print(f"\nSample customer: {sample_customer}")
    print("Already bought (top 5 by quantity):")
    print(customer_product_matrix.loc[sample_customer].sort_values(ascending=False).head(5))
    print(f"\nRecommended products for {sample_customer}:")
    print(recommend_products(sample_customer))