"""M3: combined output - "recommended for you" (collaborative filtering) + "frequently bought with" (association rules),
plus a time-based Precision@K / Recall@K evaluation against a popularity baseline.
Outputs: outputs/recommendations.json, recsys_eval.json"""
import numpy as np
import pandas as pd
from common import OUT, load_online, product_names, save_json
from recommendations import CFRecommender, build_matrix

HOLDOUT_DAYS, K_LIST = 60, (3, 5)


def evaluate(df, names):
    cutoff = df["InvoiceDate"].max() - pd.Timedelta(days=HOLDOUT_DAYS)
    train, test = df[df["InvoiceDate"] < cutoff], df[df["InvoiceDate"] >= cutoff]
    matrix = build_matrix(train)
    rec = CFRecommender(matrix, names)
    universe = set(matrix.columns)
    popular = train[train["StockCode"].isin(universe)].groupby("StockCode")["InvoiceNo"].nunique().sort_values(ascending=False)
    bought_next = test[test["StockCode"].isin(universe)].groupby("CustomerID")["StockCode"].apply(set)
    custs = [c for c in bought_next.index if c in rec.index]
    out = {"holdout_days": HOLDOUT_DAYS, "customers_evaluated": len(custs), "product_universe": len(universe)}
    for k in K_LIST:
        res = {"cf": [[], []], "popular": [[], []]}
        for c in custs:
            actual = bought_next[c]
            had = set(matrix.columns[matrix.values[rec.index[c]] > 0])
            pop_list = [p for p in popular.index if p not in had][:k]
            for name, lst in (("cf", [r["code"] for r in rec.recommend(c, k)]), ("popular", pop_list)):
                hits = len(set(lst) & actual)
                res[name][0].append(hits / k); res[name][1].append(hits / len(actual))
        for name in res:
            out[f"{name}_precision_at_{k}"] = round(float(np.mean(res[name][0])), 4)
            out[f"{name}_recall_at_{k}"] = round(float(np.mean(res[name][1])), 4)
    return out


def main():
    df = load_online()
    names = product_names(df)
    rec = CFRecommender(build_matrix(df), names)
    rules = pd.read_csv(OUT / "association_rules.csv", dtype={"antecedent_code": str, "consequent_code": str})
    bought_with = {code: [{"code": r.consequent_code, "name": r.consequent, "lift": round(r.lift, 2), "confidence": round(r.confidence, 2)}
                          for r in g.sort_values("lift", ascending=False).head(3).itertuples()]
                   for code, g in rules.groupby("antecedent_code")}
    per_customer = {c: rec.recommend(c, 5) for c in rec.m.index}
    save_json("recommendations.json", {"for_you": per_customer, "frequently_bought_with": bought_with, "names": names})
    ev = evaluate(df, names)
    save_json("recsys_eval.json", ev)
    print(f"{len(per_customer):,} customers, {len(bought_with):,} products with cross-sell rules"); print(ev)


if __name__ == "__main__":
    main()
