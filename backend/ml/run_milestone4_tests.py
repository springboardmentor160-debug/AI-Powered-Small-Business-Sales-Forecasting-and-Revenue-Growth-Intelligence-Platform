"""Milestone 4, Day 1-4: formal test record for every AI module.

Reads the real prediction / metric artifacts written by Milestones 2 and 3,
computes the metrics required by the project document, and writes ONE
combined record:

    artifacts/milestone-4/milestone4_test_results.csv
    artifacts/milestone-4/milestone4_test_report.md

Usage (project root, virtual environment active):

    python -m backend.ml.run_milestone4_tests             # everything
    python -m backend.ml.run_milestone4_tests --skip-anomaly   # no raw data needed

Nothing here is hard-coded: every number comes from the saved artifacts, or
(for anomaly detection) from a reproducible injected-anomaly experiment.
"""

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger("milestone4")

ROOT = Path(__file__).resolve().parents[2]
M2 = ROOT / "artifacts" / "milestone-2"
M2_M5 = ROOT / "backend" / "artifacts" / "milestone-2" / "forecasting"
M3 = ROOT / "artifacts" / "milestone-3"
OUT = ROOT / "artifacts" / "milestone-4"

RESULTS: list[dict] = []


def record(module: str, metric: str, value: float, note: str = "") -> None:
    RESULTS.append({"module": module, "metric": metric,
                    "value": round(float(value), 4), "note": note})


def _read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing artifact: {path}")
    return pd.read_csv(path)


# ----------------------------------------------------------------- forecasting
def test_forecasting() -> None:
    logger.info("Forecasting: MAE / RMSE / R2")
    uci = _read(M2 / "forecasting" / "uci_model_comparison_predictions.csv")
    actual = uci["actual_revenue"]
    for label, col in [("Prophet", "prophet_prediction"),
                       ("Random Forest", "random_forest_prediction"),
                       ("XGBoost", "xgboost_prediction")]:
        module = f"Revenue Forecasting - {label} (UCI)"
        pred = uci[col]
        note = f"chronological 80/20 test split, {len(uci)} days"
        record(module, "MAE", mean_absolute_error(actual, pred), note)
        record(module, "RMSE", np.sqrt(mean_squared_error(actual, pred)), note)
        record(module, "R2", r2_score(actual, pred), note)

    for label, file in [("Seasonal Naive", "m5_baseline_predictions.csv"),
                        ("Random Forest", "m5_random_forest_predictions.csv"),
                        ("XGBoost", "m5_xgboost_predictions.csv")]:
        df = _read(M2_M5 / file)
        a_col = next(c for c in df.columns if "actual" in c.lower())
        p_col = next(c for c in df.columns if "pred" in c.lower())
        module = f"Demand Forecasting - {label} (M5)"
        note = "28-day validation window"
        record(module, "MAE", mean_absolute_error(df[a_col], df[p_col]), note)
        record(module, "RMSE", np.sqrt(mean_squared_error(df[a_col], df[p_col])), note)
        record(module, "R2", r2_score(df[a_col], df[p_col]), note)


# ---------------------------------------------------------------- segmentation
def test_segmentation() -> None:
    logger.info("Segmentation: Silhouette Score")
    cmp = _read(M2 / "segmentation" / "kmeans_vs_hierarchical.csv")
    for _, row in cmp.iterrows():
        record(f"Customer Segmentation - {row['model']}", "Silhouette Score",
               row["silhouette_score"], f"k={int(row['n_clusters'])}")

    sens = _read(M2 / "segmentation" / "k_sensitivity_results.csv")
    for _, row in sens.sort_values("n_clusters").iterrows():
        record("Customer Segmentation - K sensitivity",
               f"Silhouette (k={int(row['n_clusters'])})", row["silhouette_score"],
               f"smallest cluster = {int(row['minimum_cluster_size'])} customers")


# ----------------------------------------------------------------------- churn
def test_churn() -> None:
    logger.info("Churn: Accuracy / Precision / Recall / F1")
    df = _read(M3 / "churn" / "churn_model_comparison.csv")
    for _, r in df.iterrows():
        tp, fp, fn, tn = r["true_positive"], r["false_positive"], r["false_negative"], r["true_negative"]
        total = tp + fp + fn + tn
        module = f"Churn Prediction - {r['model']}"
        note = f"{int(total)} held-out customers"
        record(module, "Accuracy", (tp + tn) / total, note)
        record(module, "Precision", tp / (tp + fp), note)
        record(module, "Recall", tp / (tp + fn), note)
        record(module, "F1-Score", 2 * tp / (2 * tp + fp + fn), note)
        record(module, "ROC-AUC", r["roc_auc"], note)
    lazy = df["lazy_model_accuracy"].iloc[0]
    record("Churn Prediction - baseline", "Always-predict-majority accuracy", lazy,
           "any real model must beat this")


# ------------------------------------------------------------- recommendations
def test_recommendations() -> None:
    logger.info("Recommendations: Precision@K / Recall@K")
    df = _read(M3 / "recommendations" / "recommendation_evaluation.csv")
    for _, r in df.iterrows():
        module = f"Recommendations - {r['model']}"
        note = f"top-10 list, {int(r['customers_evaluated'])} customers, holdout from {r['holdout_start']}"
        record(module, "Precision@10", r["precision_at_10"], note)
        record(module, "Recall@10", r["recall_at_10"], note)
        record(module, "Hit rate@10", r["hit_rate_at_10"], note)


# --------------------------------------------------------------------- anomaly
def test_anomaly(n_inject: int = 150, seed: int = 42) -> None:
    """Injected-anomaly experiment (no real fraud labels exist).

    We copy random real invoices and inflate them 20-80x in quantity and value,
    mix them into the real invoice table, run the SAME Isolation Forest the app
    uses, and count how many injected rows it catches. Real invoices are treated
    as 'normal', so the false-positive rate is a conservative upper bound:
    genuinely odd real invoices that get flagged are counted as false alarms.
    """
    from sklearn.ensemble import IsolationForest

    from backend.ml.anomaly import CONTAMINATION, RANDOM_STATE, build_invoice_features
    from backend.ml.common import load_clean_sales

    logger.info("Anomaly: injected-case experiment (%d injected)", n_inject)
    invoices = build_invoice_features(load_clean_sales())
    rng = np.random.default_rng(seed)

    base = invoices.copy()
    base["is_anomaly"] = 0
    picks = base.sample(n=n_inject, random_state=seed).copy()
    factor = rng.uniform(20, 80, size=n_inject)
    for col in ["total_quantity", "total_amount", "max_line_quantity"]:
        picks[col] = picks[col] * factor
    picks["is_anomaly"] = 1
    data = pd.concat([base, picks], ignore_index=True)

    features = ["total_quantity", "total_amount", "n_lines",
                "max_line_quantity", "max_unit_price", "avg_unit_price"]
    X = np.log1p(data[features].clip(lower=0))
    forest = IsolationForest(n_estimators=200, contamination=CONTAMINATION,
                             random_state=RANDOM_STATE)
    pred = (forest.fit_predict(X) == -1).astype(int)

    y = data["is_anomaly"].to_numpy()
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    module = "Anomaly Detection - Isolation Forest"
    note = f"{n_inject} injected + {len(base)} real invoices"
    record(module, "Detection Accuracy", (tp + tn) / len(y), note)
    record(module, "Recall (injected caught)", tp / (tp + fn), note)
    record(module, "Precision", tp / (tp + fp) if tp + fp else 0.0, note)
    record(module, "False Positive Rate", fp / (fp + tn),
           note + "; upper bound, real odd invoices count as false alarms")


# ---------------------------------------------------------------------- report
def write_outputs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(RESULTS)
    df.to_csv(OUT / "milestone4_test_results.csv", index=False)

    lines = ["# MarketMind AI - Milestone 4 Test Results", "",
             "Generated by `python -m backend.ml.run_milestone4_tests`.", ""]
    for module, group in df.groupby("module", sort=False):
        lines += [f"## {module}", "", "| Metric | Value | Note |", "|---|---|---|"]
        lines += [f"| {r.metric} | {r.value:,.4f} | {r.note} |" for r in group.itertuples()]
        lines.append("")
    (OUT / "milestone4_test_report.md").write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %d results to %s", len(df), OUT)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-anomaly", action="store_true",
                        help="skip the injected-anomaly experiment (needs the raw UCI data)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    test_forecasting()
    test_segmentation()
    test_churn()
    test_recommendations()
    if not args.skip_anomaly:
        test_anomaly()
    write_outputs()


if __name__ == "__main__":
    main()
