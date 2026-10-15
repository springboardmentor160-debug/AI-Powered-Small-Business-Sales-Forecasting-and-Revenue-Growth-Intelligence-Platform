"""M3: Association Rule Mining (support / confidence / lift) -> outputs/association_rules.csv
Uses mlxtend Apriori when installed; otherwise an equivalent exact pair-counting fallback (single-item rules)."""
import numpy as np
import pandas as pd
from common import OUT, load_online, product_names

MIN_SUPPORT, TOP_ITEMS = 0.01, 400


def basket_matrix(df, top_items=TOP_ITEMS):
    pop = df.groupby("StockCode")["InvoiceNo"].nunique().nlargest(top_items).index
    d = df[df["StockCode"].isin(pop)]
    return (d.assign(v=1).pivot_table(index="InvoiceNo", columns="StockCode", values="v", aggfunc="max", fill_value=0)).astype(bool)


def mine_rules(basket, min_support=MIN_SUPPORT):
    try:
        from mlxtend.frequent_patterns import apriori, association_rules
        fi = apriori(basket, min_support=min_support, use_colnames=True, max_len=2)
        r = association_rules(fi, metric="lift", min_threshold=1.0)
        r = r[(r["antecedents"].apply(len) == 1) & (r["consequents"].apply(len) == 1)].copy()
        r["antecedent_code"] = r["antecedents"].apply(lambda s: next(iter(s)))
        r["consequent_code"] = r["consequents"].apply(lambda s: next(iter(s)))
        return r[["antecedent_code", "consequent_code", "support", "confidence", "lift"]]
    except ImportError:
        B = basket.values.astype("float32"); n = len(B)
        co = B.T @ B
        item = np.diag(co).copy()
        ai, ci = np.where((co / n >= min_support) & ~np.eye(len(item), dtype=bool))
        conf = co[ai, ci] / item[ai]
        lift = conf / (item[ci] / n)
        r = pd.DataFrame({"antecedent_code": basket.columns[ai], "consequent_code": basket.columns[ci],
                          "support": co[ai, ci] / n, "confidence": conf, "lift": lift})
        return r[r["lift"] > 1.0]


def main():
    df = load_online()
    names = product_names(df)
    basket = basket_matrix(df)
    rules = mine_rules(basket).sort_values("lift", ascending=False).reset_index(drop=True)
    rules["antecedent"] = rules["antecedent_code"].map(names)
    rules["consequent"] = rules["consequent_code"].map(names)
    rules = rules[["antecedent_code", "antecedent", "consequent_code", "consequent", "support", "confidence", "lift"]].round(4)
    rules.to_csv(OUT / "association_rules.csv", index=False)
    print(f"{len(basket):,} baskets, {len(rules):,} rules (min_support={MIN_SUPPORT}, lift>1)")
    print(rules.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
