"""
Product Recommendations -- MarketMind AI
Milestone 3, Day 3-4 (final step): combined recommendation output

ONE function returning both
  - "recommended_for_you"     (Collaborative Filtering, Day 1-2)
  - "frequently_bought_with"  (Association Rules, Day 3-4)

Requires ml/outputs/association_rules.csv (run recommendations_complete.py first).
Run: python recommendations_combined.py
"""
from pathlib import Path

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

ML_DIR = Path(__file__).resolve().parent
DATA_FILE = ML_DIR.parent / "datasets" / "processed" / "online_retail_prepped.csv"
RULES_FILE = ML_DIR / "outputs" / "association_rules.csv"
ITEM_SEP = " || "        # must match recommendations_complete.py


class CustomerNotFound(LookupError):
    """Raised when a customer ID has no purchase history."""


# ---------------------------------------------------------------- Day 1-2: collaborative filtering
df = pd.read_csv(DATA_FILE, usecols=["CustomerID", "Description", "Quantity"])
df["Description"] = df["Description"].astype(str).str.strip()
matrix = df.pivot_table(index="CustomerID", columns="Description",
                        values="Quantity", aggfunc="sum", fill_value=0)
similarity_df = pd.DataFrame(cosine_similarity(matrix), index=matrix.index, columns=matrix.index)

# Cold-start fallback: most-bought products overall (for customers with no
# useful neighbours). Computed once.
POPULAR = matrix.gt(0).sum().sort_values(ascending=False)


def recommend_products(customer_id, top_n=5, n_similar=5):
    if customer_id not in similarity_df.index:
        raise CustomerNotFound(f"Customer {customer_id} not found")
    similar_ids = (similarity_df[customer_id].drop(customer_id)
                   .sort_values(ascending=False).head(n_similar).index)
    bought_by_similar = matrix.loc[similar_ids].sum()
    owned = matrix.loc[customer_id] != 0
    candidates = bought_by_similar[(~owned) & (bought_by_similar > 0)]
    recs = candidates.sort_values(ascending=False).head(top_n).index.tolist()
    if len(recs) < top_n:   # top up with popular items the customer hasn't bought
        extra = [p for p in POPULAR.index if p not in recs and not owned.get(p, False)]
        recs += extra[: top_n - len(recs)]
    return recs


# ---------------------------------------------------------------- Day 3-4: association rules
rules = pd.read_csv(RULES_FILE)
rules["ante_items"] = rules["antecedents"].str.split(ITEM_SEP, regex=False)
rules["cons_items"] = rules["consequents"].str.split(ITEM_SEP, regex=False)


def frequently_bought_with(product, top_n=3):
    """Single products (not multi-item strings) that go with `product`, ranked by lift."""
    product = product.strip().upper()
    hit = rules[rules["ante_items"].apply(lambda items: product in (i.upper() for i in items))]
    out = []
    for _, row in hit.sort_values("lift", ascending=False).iterrows():
        for item in row["cons_items"]:
            if item.upper() != product and item not in out:
                out.append(item)
    return out[:top_n]


def get_full_recommendations(customer_id, current_product=None):
    result = {"recommended_for_you": recommend_products(customer_id)}
    if current_product and current_product.strip():
        result["frequently_bought_with"] = frequently_bought_with(current_product)
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(get_full_recommendations(17850, "PINK REGENCY TEACUP AND SAUCER"), indent=2))
    print("\nNo current product (e.g. customer just logged in):")
    print(json.dumps(get_full_recommendations(17850), indent=2))