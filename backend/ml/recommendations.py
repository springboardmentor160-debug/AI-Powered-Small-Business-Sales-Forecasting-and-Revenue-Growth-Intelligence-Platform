"""Milestone 3, Day 1-4: Product recommendation engine.

Three outputs are produced as CSV artifacts (same pattern as Milestone 2):

1. customer_recommendations.csv  - "recommended for you"
   User-based collaborative filtering (cosine similarity on the
   customer-product matrix).
2. association_rules.csv         - "frequently bought together"
   Single-item association rules (support / confidence / lift) mined from
   invoice baskets. No customer identity is needed.
3. product_upsell.csv            - upsell opportunities
   Similar products (item-item cosine) that sit at a higher price point.

recommendation_evaluation.csv compares collaborative filtering with a
simple "most popular" baseline on a time-based hold-out, so the quality of
the engine is measured instead of assumed.
"""

import logging

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.preprocessing import normalize

from backend.ml.common import artifact_dir

logger = logging.getLogger(__name__)

NEIGHBOURS = 20          # similar customers used per recommendation
TOP_N = 5                # recommendations stored per customer
MIN_SUPPORT = 0.005      # pair must appear in >= 0.5% of invoices
MIN_CONFIDENCE = 0.20
MIN_LIFT = 1.0
HOLDOUT_DAYS = 90        # evaluation: predict the final 90 days
UPSELL_MIN_RATIO = 1.2   # upsell item must cost 20%..200% more
UPSELL_MAX_RATIO = 3.0
UPSELL_MIN_SIMILARITY = 0.15
UPSELL_MIN_BUYERS = 30


# ------------------------------------------------------------------
# Product catalogue
# ------------------------------------------------------------------

def build_catalog(sales: pd.DataFrame) -> pd.DataFrame:
    """One row per StockCode with its most common description and price."""
    names = (
        sales[sales["Description"] != ""]
        .groupby("StockCode")["Description"]
        .agg(lambda s: s.value_counts().index[0])
    )
    stats = sales.groupby("StockCode").agg(
        median_price=("Price", "median"),
        units_sold=("Quantity", "sum"),
    )
    catalog = stats.join(names).reset_index()
    catalog["Description"] = catalog["Description"].fillna(catalog["StockCode"])
    return catalog


# ------------------------------------------------------------------
# Collaborative filtering
# ------------------------------------------------------------------

def build_customer_product_matrix(sales: pd.DataFrame):
    """Sparse customer x product matrix of log(1 + quantity).

    log() stops a few wholesale buyers (orders of thousands) from
    dominating the similarity calculation.
    """
    cust = sales.dropna(subset=["Customer ID"])
    grouped = cust.groupby(["Customer ID", "StockCode"], as_index=False)[
        "Quantity"
    ].sum()

    customers = pd.Index(sorted(grouped["Customer ID"].unique()), name="Customer ID")
    products = pd.Index(sorted(grouped["StockCode"].unique()), name="StockCode")

    rows = customers.get_indexer(grouped["Customer ID"])
    cols = products.get_indexer(grouped["StockCode"])
    values = np.log1p(grouped["Quantity"].to_numpy(dtype="float32"))

    matrix = sparse.csr_matrix(
        (values, (rows, cols)), shape=(len(customers), len(products))
    )
    return matrix, customers, products


def collaborative_top_n(
    matrix: sparse.csr_matrix,
    n_neighbours: int = NEIGHBOURS,
    top_n: int = TOP_N,
    chunk: int = 500,
):
    """Top-N unseen products for every customer (row) in `matrix`.

    Score of a product = sum of cosine similarities of the nearest
    customers who bought it. Products the customer already owns are
    removed, as in the mentor guide.
    """
    normed = normalize(matrix, norm="l2", axis=1)
    owned = (matrix > 0).astype("float32").tocsr()
    n_customers = matrix.shape[0]

    top_idx = np.zeros((n_customers, top_n), dtype="int64")
    top_score = np.zeros((n_customers, top_n), dtype="float32")

    for start in range(0, n_customers, chunk):
        stop = min(start + chunk, n_customers)
        sims = (normed[start:stop] @ normed.T).toarray()
        sims[np.arange(stop - start), np.arange(start, stop)] = 0.0  # skip self

        k = min(n_neighbours, sims.shape[1] - 1)
        neighbour_idx = np.argpartition(-sims, k, axis=1)[:, :k]
        weights = np.zeros_like(sims)
        rows = np.arange(stop - start)[:, None]
        weights[rows, neighbour_idx] = sims[rows, neighbour_idx]

        scores = sparse.csr_matrix(weights) @ owned          # weighted votes
        scores = scores.toarray()
        scores[owned[start:stop].toarray() > 0] = -1.0       # drop owned items

        best = np.argpartition(-scores, top_n, axis=1)[:, :top_n]
        best_scores = np.take_along_axis(scores, best, axis=1)
        order = np.argsort(-best_scores, axis=1)
        top_idx[start:stop] = np.take_along_axis(best, order, axis=1)
        top_score[start:stop] = np.take_along_axis(best_scores, order, axis=1)

    return top_idx, top_score


def popularity_top_n(matrix: sparse.csr_matrix, top_n: int = TOP_N):
    """Baseline: the most widely bought products the customer does not own."""
    owned = (matrix > 0).astype("float32").tocsr()
    popularity = np.asarray(owned.sum(axis=0)).ravel()
    order = np.argsort(-popularity)
    result = np.zeros((matrix.shape[0], top_n), dtype="int64")
    for i in range(matrix.shape[0]):
        have = set(owned[i].indices)
        picks = [p for p in order[: top_n + len(have) + 5] if p not in have]
        result[i] = picks[:top_n]
    return result


def evaluate_collaborative_filtering(sales: pd.DataFrame) -> pd.DataFrame:
    """Time-based hold-out: learn before the last 90 days, test after."""
    cust = sales.dropna(subset=["Customer ID"])
    cutoff = cust["InvoiceDate"].max() - pd.Timedelta(days=HOLDOUT_DAYS)

    train = cust[cust["InvoiceDate"] < cutoff]
    test = cust[cust["InvoiceDate"] >= cutoff]

    matrix, customers, products = build_customer_product_matrix(train)
    cf_idx, _ = collaborative_top_n(matrix, top_n=10)
    pop_idx = popularity_top_n(matrix, top_n=10)

    test_sets = (
        test.groupby("Customer ID")["StockCode"].agg(set).to_dict()
    )

    rows = []
    for name, idx in (("collaborative_filtering", cf_idx), ("popularity_baseline", pop_idx)):
        hits, precisions, recalls, evaluated = 0, [], [], 0
        for i, customer in enumerate(customers):
            actual = test_sets.get(customer)
            if not actual:
                continue
            evaluated += 1
            recommended = set(products[idx[i]])
            overlap = len(recommended & actual)
            hits += overlap > 0
            precisions.append(overlap / len(recommended))
            recalls.append(overlap / len(actual))
        rows.append(
            {
                "model": name,
                "customers_evaluated": evaluated,
                "hit_rate_at_10": round(hits / max(evaluated, 1), 4),
                "precision_at_10": round(float(np.mean(precisions)), 4),
                "recall_at_10": round(float(np.mean(recalls)), 4),
                "holdout_start": cutoff.date().isoformat(),
            }
        )
    return pd.DataFrame(rows)


# ------------------------------------------------------------------
# Association rules (cross-sell)
# ------------------------------------------------------------------

def mine_association_rules(sales: pd.DataFrame, catalog: pd.DataFrame) -> pd.DataFrame:
    """Single-item rules A -> B with support, confidence and lift.

    This is Apriori restricted to 2-item sets, computed with sparse matrix
    algebra. Output columns match mlxtend's association_rules().
    """
    baskets = sales[["Invoice", "StockCode"]].drop_duplicates()
    invoices = pd.Index(baskets["Invoice"].unique())
    codes = pd.Index(baskets["StockCode"].unique())
    basket_matrix = sparse.csr_matrix(
        (
            np.ones(len(baskets), dtype="float32"),
            (invoices.get_indexer(baskets["Invoice"]), codes.get_indexer(baskets["StockCode"])),
        ),
        shape=(len(invoices), len(codes)),
    )

    n_baskets = basket_matrix.shape[0]
    item_counts = np.asarray(basket_matrix.sum(axis=0)).ravel()
    keep = np.where(item_counts / n_baskets >= MIN_SUPPORT)[0]
    reduced = basket_matrix[:, keep]

    pair_counts = (reduced.T @ reduced).toarray()
    np.fill_diagonal(pair_counts, 0)
    counts = item_counts[keep]

    a_idx, b_idx = np.nonzero(pair_counts / n_baskets >= MIN_SUPPORT)
    pair = pair_counts[a_idx, b_idx]
    support = pair / n_baskets
    confidence = pair / counts[a_idx]
    lift = confidence / (counts[b_idx] / n_baskets)

    rules = pd.DataFrame(
        {
            "antecedent_code": codes[keep][a_idx],
            "consequent_code": codes[keep][b_idx],
            "antecedent_baskets": counts[a_idx].astype(int),
            "pair_baskets": pair.astype(int),
            "support": support,
            "confidence": confidence,
            "lift": lift,
        }
    )
    rules = rules[(rules["confidence"] >= MIN_CONFIDENCE) & (rules["lift"] > MIN_LIFT)]

    names = catalog.set_index("StockCode")["Description"]
    rules.insert(1, "antecedent_name", rules["antecedent_code"].map(names))
    rules.insert(3, "consequent_name", rules["consequent_code"].map(names))
    rules[["support", "confidence", "lift"]] = rules[["support", "confidence", "lift"]].round(4)
    return rules.sort_values("lift", ascending=False).reset_index(drop=True)


# ------------------------------------------------------------------
# Upsell opportunities
# ------------------------------------------------------------------

def build_upsell(matrix, products: pd.Index, catalog: pd.DataFrame) -> pd.DataFrame:
    """For each product, similar products priced 20%-200% higher.

    "Similar" = bought by the same customers (item-item cosine on the
    customer-product matrix). This is a heuristic, not a proven uplift.
    """
    owned = (matrix > 0).astype("float32").tocsc()
    buyers = np.asarray(owned.sum(axis=0)).ravel()
    keep = np.where(buyers >= UPSELL_MIN_BUYERS)[0]

    items = normalize(owned[:, keep].T.tocsr(), norm="l2", axis=1)
    sim = (items @ items.T).toarray()
    np.fill_diagonal(sim, 0.0)

    prices = catalog.set_index("StockCode")["median_price"].reindex(products[keep]).to_numpy()
    names = catalog.set_index("StockCode")["Description"]
    codes = products[keep]

    records = []
    for i in range(len(keep)):
        ratio = prices / prices[i]
        eligible = (
            (ratio >= UPSELL_MIN_RATIO)
            & (ratio <= UPSELL_MAX_RATIO)
            & (sim[i] >= UPSELL_MIN_SIMILARITY)
        )
        candidates = np.where(eligible)[0]
        if candidates.size == 0:
            continue
        best = candidates[np.argsort(-sim[i, candidates])[:3]]
        for rank, j in enumerate(best, start=1):
            records.append(
                {
                    "product_code": codes[i],
                    "product_name": names.get(codes[i], codes[i]),
                    "product_price": round(float(prices[i]), 2),
                    "rank": rank,
                    "upsell_code": codes[j],
                    "upsell_name": names.get(codes[j], codes[j]),
                    "upsell_price": round(float(prices[j]), 2),
                    "price_uplift_pct": round(float((ratio[j] - 1) * 100), 1),
                    "similarity": round(float(sim[i, j]), 4),
                }
            )
    return pd.DataFrame(records)


# ------------------------------------------------------------------
# Orchestration
# ------------------------------------------------------------------

def run(sales: pd.DataFrame) -> dict:
    out = artifact_dir("recommendations")
    catalog = build_catalog(sales)

    matrix, customers, products = build_customer_product_matrix(sales)
    logger.info("Customer-product matrix: %s customers x %s products", *matrix.shape)

    idx, score = collaborative_top_n(matrix)
    names = catalog.set_index("StockCode")["Description"]
    prices = catalog.set_index("StockCode")["median_price"]

    recs = []
    for i, customer in enumerate(customers):
        for rank in range(TOP_N):
            code = products[idx[i, rank]]
            recs.append(
                {
                    "Customer ID": int(customer),
                    "rank": rank + 1,
                    "StockCode": code,
                    "Description": names.get(code, code),
                    "unit_price": round(float(prices.get(code, np.nan)), 2),
                    "score": round(float(score[i, rank]), 4),
                }
            )
    pd.DataFrame(recs).to_csv(out / "customer_recommendations.csv", index=False)

    rules = mine_association_rules(sales, catalog)
    rules.to_csv(out / "association_rules.csv", index=False)

    upsell = build_upsell(matrix, products, catalog)
    upsell.to_csv(out / "product_upsell.csv", index=False)

    # Popular products power the cold-start fallback for new customers.
    popular = catalog.sort_values("units_sold", ascending=False).head(10)
    popular.to_csv(out / "popular_products.csv", index=False)

    evaluation = evaluate_collaborative_filtering(sales)
    evaluation.to_csv(out / "recommendation_evaluation.csv", index=False)

    summary = {
        "customers": len(customers),
        "products": len(products),
        "association_rules": len(rules),
        "upsell_pairs": len(upsell),
    }
    logger.info("Recommendations done: %s", summary)
    logger.info("Evaluation:\n%s", evaluation.to_string(index=False))
    return summary
