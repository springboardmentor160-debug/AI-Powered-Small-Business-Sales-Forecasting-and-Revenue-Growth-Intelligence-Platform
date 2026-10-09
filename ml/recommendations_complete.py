"""
Product Recommendations -- MarketMind AI
Milestone 3, Day 3-4: Association Rule Mining

Finds products frequently bought TOGETHER in the same invoice, regardless of
which customer bought them -> "customers who bought X also bought Y".

    python recommendations_complete.py     # writes ml/outputs/association_rules.csv
"""
from pathlib import Path

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

ML_DIR = Path(__file__).resolve().parent
DATA_FILE = ML_DIR.parent / "datasets" / "processed" / "online_retail_prepped.csv"
OUT_DIR = ML_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)

MIN_SUPPORT = 0.02       # combo must appear in >= 2% of baskets
MIN_CONFIDENCE = 0.3     # rule must hold >= 30% of the time
MIN_LIFT = 1.0           # FIX: keep only genuinely linked pairs (lift > 1)
ITEM_SEP = " || "        # FIX: product names contain commas, so ", " was ambiguous

# ---------------------------------------------------------------------------
# 1. Basket matrix: one row per INVOICE, True/False per product
# ---------------------------------------------------------------------------
df = pd.read_csv(DATA_FILE, usecols=["InvoiceNo", "Description", "Quantity"])
df = df.dropna(subset=["Description"])
# FIX: strip trailing spaces -- "ROSES REGENCY TEACUP AND SAUCER " and the
# same name without the space were being treated as different products.
df["Description"] = df["Description"].str.strip()
df = df[df["Quantity"] > 0]

# FIX: build a boolean matrix directly (~70 MB) instead of a float64 sum
# matrix (~575 MB) -- Apriori only needs presence/absence anyway.
basket_bool = (
    df[["InvoiceNo", "Description"]].drop_duplicates()
    .assign(bought=True)
    .set_index(["InvoiceNo", "Description"])["bought"]
    .unstack(fill_value=False)
)
print(f"Basket matrix shape: {basket_bool.shape}")

# ---------------------------------------------------------------------------
# 2. Frequent itemsets
# ---------------------------------------------------------------------------
frequent_itemsets = apriori(basket_bool, min_support=MIN_SUPPORT, use_colnames=True)
print(f"\nFrequent itemsets found: {len(frequent_itemsets)}")

# ---------------------------------------------------------------------------
# 3. Rules (confidence filter, then keep lift > 1 as the handout requires)
# ---------------------------------------------------------------------------
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)
rules = rules[rules["lift"] > MIN_LIFT].sort_values("lift", ascending=False)
print(f"Rules generated (confidence >= {MIN_CONFIDENCE}, lift > {MIN_LIFT}): {len(rules)}")

rules_out = rules.copy()
for col in ("antecedents", "consequents"):
    rules_out[col] = rules_out[col].apply(lambda s: ITEM_SEP.join(sorted(s)))

print("\nTop 10 rules by lift:")
print(rules_out[["antecedents", "consequents", "support", "confidence", "lift"]]
      .head(10).to_string(index=False))


# ---------------------------------------------------------------------------
# 4. Simple lookup (the API uses the richer version in recommendations_combined.py)
# ---------------------------------------------------------------------------
def cross_sell_for_product(product_name, top_n=5):
    product_name = product_name.strip()
    matches = rules[rules["antecedents"].apply(lambda s: product_name in s)]
    if matches.empty:
        return pd.DataFrame()
    return (matches.sort_values("lift", ascending=False)
            [["consequents", "confidence", "lift"]].head(top_n))


sample_product = "PINK REGENCY TEACUP AND SAUCER"
print(f"\nCross-sell suggestions for '{sample_product}':")
print(cross_sell_for_product(sample_product))

# ---------------------------------------------------------------------------
# 5. Save -- FIX: always to ml/outputs/ (it used to land in whatever folder the
#    script was run from, leaving two diverging copies of the file)
# ---------------------------------------------------------------------------
out_file = OUT_DIR / "association_rules.csv"
rules_out[["antecedents", "consequents", "support", "confidence", "lift"]].to_csv(out_file, index=False)
print(f"\nSaved {out_file}")