"""M2: customer segmentation - RFM features, scaling, K-Means + hierarchical (Ward) clustering, evaluation, business interpretation.
Outputs: outputs/segment_assignments.csv, segments.json, segmentation_metrics.json, dendrogram.png

Feature definitions (RFM variant used by the project guide)
  Recency   = customer_activity_days  days since the last order (as-of date = day after the last transaction in the data)
  Frequency = purchase_frequency      number of distinct invoices
  Monetary  = purchase_value          average order value (total spend is kept as an extra column and as RFM score input)
Customers also get quartile RFM scores (1-4 each) for reference; clustering itself uses log1p -> StandardScaler on the three features."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score, calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import StandardScaler
from common import OUT, SEED, as_of_date, customer_features, load_online, save_json

K = 4
K_RANGE = range(2, 8)
FEATURES = ["purchase_frequency", "purchase_value", "customer_activity_days"]


def name_clusters(df, col):
    """Name clusters from their average behaviour (so names never depend on arbitrary cluster ids)."""
    prof = df.groupby(col)[FEATURES].mean()
    z = (prof - prof.mean()) / prof.std(ddof=0)
    score = z["purchase_frequency"] + z["purchase_value"] - z["customer_activity_days"]
    at_risk = prof["customer_activity_days"].idxmax()
    vip = score.drop(at_risk).idxmax() if at_risk == score.idxmax() else score.idxmax()
    rest = score.drop([at_risk, vip]).sort_values(ascending=False)
    names = {vip: "VIP / Loyal Customers", at_risk: "At-Risk / Fading Customers"}
    for i, c in enumerate(rest.index):
        names[c] = "Regular Customers" if i == 0 else "Occasional Shoppers"
    return names


def rfm_scores(cf):
    """Quartile scores 1-4 (4 = best). Recency is inverted: fewer inactive days = higher score. rank(first) breaks ties."""
    q = lambda s, asc=True: pd.qcut(s.rank(method="first", ascending=asc), 4, labels=[1, 2, 3, 4]).astype(int)
    cf["R_score"] = q(cf["customer_activity_days"], asc=False)
    cf["F_score"] = q(cf["purchase_frequency"])
    cf["M_score"] = q(cf["total_spend"])
    cf["RFM_score"] = cf["R_score"] + cf["F_score"] + cf["M_score"]
    return cf


def interpret(row):
    """Plain-language reading + suggested action, built from the segment's actual numbers."""
    n, f, v, d = row["customer_count"], row["avg_purchase_frequency"], row["avg_purchase_value"], row["avg_inactivity_days"]
    facts = f"{int(n):,} customers ({row['share_pct']}%), about {f:.1f} orders each, average order {v:,.0f}, last bought {d:,.0f} days ago on average."
    text = {
        "VIP / Loyal Customers": ("Frequent, recent, high-value buyers - the core of revenue.", "Reward and retain: early access, loyalty perks, personal outreach."),
        "Regular Customers": ("Steady buyers with moderate frequency and value.", "Grow them: cross-sell with recommendations, nudge towards the next tier."),
        "Occasional Shoppers": ("Infrequent buyers that have drifted away from the shop.", "Re-engage: seasonal campaigns and reminders before they lapse further."),
        "At-Risk / Fading Customers": ("The longest-inactive, lowest-value group - most likely already lost.", "Win-back offer once; do not spend heavily beyond that."),
    }[row["segment"]]
    return {"business_interpretation": f"{text[0]} {facts}", "recommended_action": text[1]}


def main():
    tx = load_online()
    asof = as_of_date(tx)
    cf = customer_features(tx, asof).rename(columns={"order_frequency": "purchase_frequency", "avg_order_value": "purchase_value",
                                                     "inactivity_days": "customer_activity_days"})
    cf = rfm_scores(cf)
    # heavy right-skew in spend/frequency -> log transform before scaling so a few whales don't dominate distances
    X = StandardScaler().fit_transform(np.log1p(cf[FEATURES]))

    metrics = {"n_customers": len(cf), "as_of": str(asof.date()), "features": FEATURES, "preprocessing": "log1p -> StandardScaler",
               "chosen_k": K, "by_k": {}}
    labels_by_k = {}
    for k in K_RANGE:
        km = KMeans(n_clusters=k, random_state=SEED, n_init=10).fit(X)
        labels_by_k[k] = km.labels_
        metrics["by_k"][str(k)] = {"inertia": round(float(km.inertia_), 1), "silhouette": round(float(silhouette_score(X, km.labels_)), 4),
                                    "davies_bouldin": round(float(davies_bouldin_score(X, km.labels_)), 4),
                                    "calinski_harabasz": round(float(calinski_harabasz_score(X, km.labels_)), 1)}
    metrics["kmeans_silhouette_by_k"] = {k: v["silhouette"] for k, v in metrics["by_k"].items()}      # kept for older consumers
    best_sil_k = max(K_RANGE, key=lambda k: metrics["by_k"][str(k)]["silhouette"])
    metrics["best_silhouette_k"] = best_sil_k
    metrics["k_justification"] = (
        f"Silhouette is highest at K={best_sil_k} ({metrics['by_k'][str(best_sil_k)]['silhouette']}), but K=2 only separates active from lapsed customers. "
        f"K={K} is used (silhouette {metrics['by_k'][str(K)]['silhouette']}, close to K=5/6, no sharp elbow in inertia) because four segments "
        f"(loyal / regular / occasional / at-risk) give marketing distinct actions. The clusters overlap moderately - read them as "
        f"behavioural tiers, not hard boundaries.")

    km = KMeans(n_clusters=K, random_state=SEED, n_init=10).fit(X)
    cf["cluster"] = km.labels_
    cf["cluster_hierarchical"] = AgglomerativeClustering(n_clusters=K, linkage="ward").fit_predict(X)
    cf["segment"] = cf["cluster"].map(name_clusters(cf, "cluster"))
    cf["segment_hierarchical"] = cf["cluster_hierarchical"].map(name_clusters(cf, "cluster_hierarchical"))
    metrics["kmeans_silhouette"] = round(float(silhouette_score(X, cf["cluster"])), 4)
    metrics["hierarchical_silhouette"] = round(float(silhouette_score(X, cf["cluster_hierarchical"])), 4)
    metrics["kmeans_davies_bouldin"] = round(float(davies_bouldin_score(X, cf["cluster"])), 4)
    metrics["hierarchical_davies_bouldin"] = round(float(davies_bouldin_score(X, cf["cluster_hierarchical"])), 4)
    # Adjusted Rand Index: agreement of the two partitions regardless of how clusters are numbered (1 = identical, 0 = chance level)
    metrics["adjusted_rand_index_kmeans_vs_hierarchical"] = round(float(adjusted_rand_score(cf["cluster"], cf["cluster_hierarchical"])), 4)
    metrics["segment_name_agreement"] = round(float((cf["segment"] == cf["segment_hierarchical"]).mean()), 4)
    metrics["method_agreement"] = metrics["segment_name_agreement"]            # legacy key
    # stability: re-run K-Means with other seeds and compare to the reference solution
    seeds = [1, 2, 3, 4, 5]
    metrics["kmeans_seed_stability_ari_mean"] = round(float(np.mean([adjusted_rand_score(
        km.labels_, KMeans(n_clusters=K, random_state=s, n_init=10).fit_predict(X)) for s in seeds])), 4)
    metrics["cluster_sizes"] = {"kmeans": cf["segment"].value_counts().to_dict(), "hierarchical": cf["segment_hierarchical"].value_counts().to_dict()}

    summary = cf.groupby("segment").agg(
        customer_count=("customer_id", "count"), avg_purchase_value=("purchase_value", "mean"),
        avg_purchase_frequency=("purchase_frequency", "mean"), avg_inactivity_days=("customer_activity_days", "mean"),
        avg_total_spend=("total_spend", "mean"), avg_rfm_score=("RFM_score", "mean"),
        total_revenue=("total_spend", "sum")).round(2).reset_index().sort_values("customer_count", ascending=False)
    summary["share_pct"] = (summary["customer_count"] / len(cf) * 100).round(1)
    summary["revenue_share_pct"] = (summary["total_revenue"] / summary["total_revenue"].sum() * 100).round(1)
    interp = summary.apply(interpret, axis=1, result_type="expand")
    summary = pd.concat([summary, interp], axis=1)

    cf.to_csv(OUT / "segment_assignments.csv", index=False)
    save_json("segments.json", summary.to_dict(orient="records"))
    save_json("segmentation_metrics.json", metrics)

    link = linkage(X, method="ward")
    cut = link[-(K - 1), 2]
    plt.figure(figsize=(9, 4.5))
    dendrogram(link, truncate_mode="lastp", p=15, color_threshold=cut)
    plt.axhline(cut, ls="--", c="grey", lw=1)
    plt.title(f"Customer Similarity Tree (Ward linkage, {K}-cluster cut shown)")
    plt.xlabel("Customers (merged groups, size in brackets)"); plt.ylabel("Distance")
    plt.tight_layout(); plt.savefig(OUT / "dendrogram.png", dpi=110); plt.close()

    print(summary[["segment", "customer_count", "share_pct", "revenue_share_pct", "avg_purchase_value", "avg_purchase_frequency", "avg_inactivity_days"]].to_string(index=False))
    print({k: v for k, v in metrics.items() if k not in ("by_k", "cluster_sizes", "k_justification")})
    print(metrics["k_justification"])


if __name__ == "__main__":
    main()
