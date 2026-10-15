"""Checks that every ML output file the API / dashboard reads exists, parses, and has the fields they use.
Run:  python ml/verify_outputs.py        (exit code 1 if anything is missing)"""
import json
import sys
import pandas as pd
from common import OUT

def need(d, keys, where):
    miss = [k for k in keys if k not in d]
    return [f"{where}: missing {miss}"] if miss else []

def main():
    errs = []
    def js(name):
        p = OUT / name
        if not p.exists():
            errs.append(f"{name}: file not found"); return None
        return json.loads(p.read_text(encoding="utf-8"))
    def csv(name, cols):
        p = OUT / name
        if not p.exists():
            errs.append(f"{name}: file not found"); return
        df = pd.read_csv(p, nrows=5)
        errs.extend(need(df.columns, cols, name))

    seg = js("segments.json")
    if seg: errs += need(seg[0], ["segment", "customer_count", "share_pct", "avg_purchase_value", "avg_purchase_frequency", "avg_inactivity_days", "recommended_action"], "segments.json[0]")
    m = js("segmentation_metrics.json")
    if m: errs += need(m, ["kmeans_silhouette", "hierarchical_silhouette", "adjusted_rand_index_kmeans_vs_hierarchical", "by_k", "chosen_k", "k_justification"], "segmentation_metrics.json")
    f = js("forecast.json")
    if f: errs += need(f, ["period", "predicted_revenue", "model_used", "metrics", "history", "daily"], "forecast.json") + need(f.get("metrics", {}), ["mae", "rmse", "mape", "r2"], "forecast.json.metrics")
    fc = js("forecast_model_comparison.json")
    if fc: errs += need(fc, ["results", "best_model", "evaluation"], "forecast_model_comparison.json") + need(fc.get("evaluation", {}), ["test_start", "test_end", "test_days", "beaten_by_baseline"], "forecast_model_comparison.json.evaluation")
    ch = js("churn_metrics.json")
    if ch: errs += need(ch, ["results", "selected_model", "risk_counts", "label", "churn_rate", "test_size"], "churn_metrics.json")
    rs = js("recsys_eval.json")
    if rs: errs += need(rs, ["cf_precision_at_3", "popular_precision_at_3", "cf_recall_at_3", "popular_recall_at_3", "customers_evaluated", "holdout_days"], "recsys_eval.json")
    an = js("anomaly_eval.json")
    if an: errs += need(an.get("evaluation", {}), ["recall", "precision", "false_positive_rate", "injected"], "anomaly_eval.json.evaluation")
    rec = js("recommendations.json")
    if rec: errs += need(rec, ["for_you", "frequently_bought_with", "names"], "recommendations.json")
    js("data_quality.json")
    csv("churn_predictions.csv", ["customer_id", "churn_probability", "retention_risk", "order_frequency", "inactivity_days", "avg_order_value", "segment"])
    csv("anomaly_alerts.csv", ["date", "severity", "message"])
    csv("segment_assignments.csv", ["customer_id", "segment", "cluster", "cluster_hierarchical", "R_score", "F_score", "M_score"])
    csv("milestone4_test_results.csv", ["module", "metric", "value"])
    for name in ("dendrogram.png", "business_report.xlsx"):
        if not (OUT / name).exists():
            errs.append(f"{name}: file not found")
    if errs:
        print("PROBLEMS:"); [print(" -", e) for e in errs]; sys.exit(1)
    print("All ML output files exist and contain the fields used by the API and dashboard.")

if __name__ == "__main__":
    main()
