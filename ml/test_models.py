"""M4: collect every module's measured performance into outputs/milestone4_test_results.csv."""
import pandas as pd
from common import OUT, load_json, save_json


def main():
    rows = []
    fc = load_json("forecast_model_comparison.json", {})
    for r in fc.get("results", []):
        for k, label in (("mae", "MAE"), ("rmse", "RMSE"), ("mape", "MAPE (%)"), ("r2", "R2 Score")):
            if r.get(k) is None:
                continue
            rows.append({"module": f"Sales Forecasting ({r['model']})", "metric": label, "value": round(r[k], 3)})
    seg = load_json("segmentation_metrics.json", {})
    for k, label in (("kmeans_silhouette", "K-Means"), ("hierarchical_silhouette", "Hierarchical")):
        if k in seg:
            rows.append({"module": f"Customer Segmentation ({label})", "metric": "Silhouette Score", "value": seg[k]})
    for k, label in (("adjusted_rand_index_kmeans_vs_hierarchical", "Adjusted Rand Index (K-Means vs Hierarchical)"),
                     ("kmeans_seed_stability_ari_mean", "K-Means seed stability (mean ARI)"),
                     ("kmeans_davies_bouldin", "Davies-Bouldin (K-Means, lower is better)")):
        if k in seg:
            rows.append({"module": "Customer Segmentation", "metric": label, "value": seg[k]})
    ch = load_json("churn_metrics.json", {})
    for r in ch.get("results", []):
        for k, label in (("accuracy", "Accuracy"), ("precision", "Precision"), ("recall", "Recall"), ("f1", "F1-Score"), ("roc_auc", "ROC-AUC")):
            rows.append({"module": f"Churn Prediction ({r['model']})", "metric": label, "value": round(r[k], 3)})
    rs = load_json("recsys_eval.json", {})
    for k, v in rs.items():
        if "precision_at" in k or "recall_at" in k:
            who, rest = k.split("_", 1)
            rows.append({"module": "Recommendation System (" + ("Collaborative Filtering" if who == "cf" else "Popularity baseline") + ")",
                         "metric": rest.replace("_at_", "@").replace("precision", "Precision").replace("recall", "Recall"), "value": v})
    an = load_json("anomaly_eval.json", {}).get("evaluation", {})
    for k, label in (("detection_accuracy", "Detection Accuracy"), ("recall", "Recall (injected anomalies caught)"), ("false_positive_rate", "False Positive Rate")):
        if k in an:
            rows.append({"module": "Anomaly Detection (Isolation Forest)", "metric": label, "value": round(an[k], 4)})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "milestone4_test_results.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
