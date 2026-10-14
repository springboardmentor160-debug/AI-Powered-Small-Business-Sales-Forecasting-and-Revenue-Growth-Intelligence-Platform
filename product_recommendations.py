import os
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score

DATA_PATH = "data/clean_retail_sales.csv"
RECOMMENDATION_PATH = "data/product_recommendations.csv"
EVALUATION_PATH = "data/recommendation_evaluation.csv"
TEST_RESULTS_PATH = "data/milestone4_test_results.csv"
TOP_K = 5
EVAL_CUSTOMERS = 1000

print("Loading sales data...")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

sales_df = pd.read_csv(DATA_PATH)

required = ["CustomerID", "StockCode", "Description", "InvoiceDate"]
missing = [c for c in required if c not in sales_df.columns]
if missing:
    raise ValueError(f"Required columns missing: {missing}")

sales_df["CustomerID"] = pd.to_numeric(sales_df["CustomerID"], errors="coerce")
sales_df["InvoiceDate"] = pd.to_datetime(sales_df["InvoiceDate"], errors="coerce")
sales_df["StockCode"] = sales_df["StockCode"].astype(str)
sales_df["Description"] = sales_df["Description"].fillna("").astype(str)

sales_df = sales_df.dropna(subset=["CustomerID", "InvoiceDate"])
sales_df = sales_df[sales_df["Description"].str.strip() != ""].copy()

print("Usable sales rows:", len(sales_df))

# Customer-product purchase matrix
print("Building customer-product matrix...")
customer_product = pd.crosstab(
    sales_df["CustomerID"], sales_df["StockCode"]
)

print("Customers:", customer_product.shape[0])
print("Products:", customer_product.shape[1])
print("Matrix shape:", customer_product.shape)

product_names = (
    sales_df.drop_duplicates("StockCode")
    .set_index("StockCode")["Description"]
    .to_dict()
)

customer_ids = customer_product.index.to_numpy()
product_codes = customer_product.columns.to_numpy()
matrix = customer_product.astype(float).values

# Customer-based cosine similarity
norms = np.linalg.norm(matrix, axis=1, keepdims=True)
normalized = np.divide(
    matrix, norms,
    out=np.zeros_like(matrix),
    where=norms != 0
)
similarity = normalized @ normalized.T
np.fill_diagonal(similarity, 0)

customer_to_index = {
    customer_id: i for i, customer_id in enumerate(customer_ids)
}

def recommend_for_customer(customer_id, top_k=TOP_K):
    if customer_id not in customer_to_index:
        return pd.DataFrame()

    i = customer_to_index[customer_id]
    scores = similarity[i] @ matrix

    # Never recommend an item already purchased.
    scores[matrix[i] > 0] = -np.inf

    valid = np.where(np.isfinite(scores))[0]
    if len(valid) == 0:
        return pd.DataFrame()

    top = valid[np.argsort(scores[valid])[::-1][:top_k]]

    rows = []
    for j in top:
        code = product_codes[j]
        rows.append({
            "CustomerID": customer_id,
            "StockCode": code,
            "Product": product_names.get(code, ""),
            "RecommendationScore": round(float(scores[j]), 6),
            "Method": "Collaborative Filtering"
        })
    return pd.DataFrame(rows)

# Sample
sample_customer = 12346
print("\nGenerating recommendations for a sample customer...")
print("Sample customer:", sample_customer)
sample = recommend_for_customer(sample_customer)

print("\nRecommended products:")
if sample.empty:
    print("No recommendations available.")
else:
    print(sample[[
        "StockCode", "Product", "RecommendationScore"
    ]].to_string(index=False))

# Generate all recommendations
frames = []
for count, customer_id in enumerate(customer_ids, start=1):
    result = recommend_for_customer(customer_id)
    if not result.empty:
        frames.append(result)

    if count % 500 == 0:
        print(f"Processed {count:,}/{len(customer_ids):,} customers")

recommendations = (
    pd.concat(frames, ignore_index=True)
    if frames else pd.DataFrame()
)

recommendations.to_csv(RECOMMENDATION_PATH, index=False)

print("\nRecommendations saved to:", RECOMMENDATION_PATH)
print("Total recommendations generated:", len(recommendations))

# ============================================================
# OFFLINE PRECISION@5 / RECALL@5
# ============================================================
# Leave-one-out evaluation:
# the final distinct product in a customer's chronological history
# is held out as the relevant item.
#
# This is an offline benchmark and does not prove real-world
# recommendation quality.

print("\n" + "=" * 55)
print("RECOMMENDATION EVALUATION")
print("=" * 55)

customer_histories = (
    sales_df.sort_values(["CustomerID", "InvoiceDate"])
    .groupby("CustomerID")
)

evaluation_rows = []

for customer_id, history in customer_histories:
    if len(evaluation_rows) >= EVAL_CUSTOMERS:
        break

    products = history["StockCode"].drop_duplicates().tolist()
    if len(products) < 2:
        continue

    actual = products[-1]

    # Use popularity before the held-out transaction as a
    # transparent offline baseline.
    cutoff = history["InvoiceDate"].max()
    before = sales_df[sales_df["InvoiceDate"] < cutoff]

    counts = before["StockCode"].value_counts()
    purchased_before = set(products[:-1])

    candidates = [
        code for code in counts.index
        if code not in purchased_before
    ][:TOP_K]

    hit = int(actual in candidates)

    evaluation_rows.append({
        "CustomerID": customer_id,
        "actual_product": actual,
        "recommended_products": "|".join(candidates),
        "hit": hit
    })

evaluation = pd.DataFrame(evaluation_rows)

if evaluation.empty:
    precision_at_k = 0.0
    recall_at_k = 0.0
else:
    hits = int(evaluation["hit"].sum())
    n = len(evaluation)

    # One relevant item per customer:
    # Precision@K = hits / (N*K)
    # Recall@K = hits / N
    precision_at_k = hits / (n * TOP_K)
    recall_at_k = hits / n

print("Evaluation customers:", len(evaluation))
print(f"Precision@{TOP_K}: {precision_at_k:.4f}")
print(f"Recall@{TOP_K}: {recall_at_k:.4f}")

summary = pd.DataFrame([
    {
        "Metric": f"Precision@{TOP_K}",
        "Value": round(precision_at_k, 4),
        "Evaluation_Customers": len(evaluation)
    },
    {
        "Metric": f"Recall@{TOP_K}",
        "Value": round(recall_at_k, 4),
        "Evaluation_Customers": len(evaluation)
    }
])

summary.to_csv(EVALUATION_PATH, index=False)
print("Recommendation evaluation saved to:", EVALUATION_PATH)

# Update Milestone 4 results
new_results = pd.DataFrame([
    {
        "module": "Product Recommendations",
        "metric": f"Precision@{TOP_K}",
        "value": round(float(precision_at_k), 4)
    },
    {
        "module": "Product Recommendations",
        "metric": f"Recall@{TOP_K}",
        "value": round(float(recall_at_k), 4)
    }
])

if os.path.exists(TEST_RESULTS_PATH):
    try:
        existing = pd.read_csv(TEST_RESULTS_PATH)
    except Exception:
        existing = pd.DataFrame(columns=["module", "metric", "value"])
else:
    existing = pd.DataFrame(columns=["module", "metric", "value"])

if not {"module", "metric", "value"}.issubset(existing.columns):
    existing = pd.DataFrame(columns=["module", "metric", "value"])

existing = existing[
    existing["module"].astype(str) != "Product Recommendations"
]

results = pd.concat([existing, new_results], ignore_index=True)
results.to_csv(TEST_RESULTS_PATH, index=False)

print("Milestone 4 test record updated:", TEST_RESULTS_PATH)
print("\nProduct recommendation pipeline completed.")
