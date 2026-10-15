"""M3: Z-score + Isolation Forest anomaly detection on store sales/inventory records -> outputs/anomaly_alerts.csv
Also evaluates detection with injected anomalies (the guide's approach when no fraud labels exist)."""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score
from common import OUT, SEED, load_sales, save_json

FEATURES = ["units_sold", "price", "revenue", "inventory_level", "units_ordered"]
CONTAMINATION, Z_THRESHOLD = 0.02, 3.0


def main():
    df = load_sales()
    df["z_score"] = ((df["revenue"] - df["revenue"].mean()) / df["revenue"].std()).round(2)
    df["flag_zscore"] = df["z_score"].abs() > Z_THRESHOLD
    iso = IsolationForest(contamination=CONTAMINATION, random_state=SEED, n_estimators=200).fit(df[FEATURES])
    df["anomaly_score"] = (-iso.score_samples(df[FEATURES])).round(4)          # higher = more unusual
    df["flag_iso"] = iso.predict(df[FEATURES]) == -1

    flagged = df[df["flag_zscore"] | df["flag_iso"]].copy()
    flagged["method"] = np.select([flagged.flag_zscore & flagged.flag_iso, flagged.flag_iso], ["Z-score + Isolation Forest", "Isolation Forest"], "Z-score")
    hi = flagged["anomaly_score"].quantile(0.80)          # top 20% most unusual alerts are "high"
    flagged["severity"] = np.where(flagged.anomaly_score >= hi, "high", "medium")
    flagged["alert_type"] = np.where(flagged.units_sold > flagged.inventory_level, "inventory_anomaly", "unusual_sales_activity")
    flagged["message"] = flagged.apply(lambda r: f"{r.date:%Y-%m-%d} store {r.store_id} product {r.product_id}: {r.units_sold} units sold "
                                       f"(stock {r.inventory_level}), revenue {r.revenue:,.2f} - outside the normal pattern", axis=1)
    cols = ["date", "store_id", "product_id", "category", "units_sold", "price", "revenue", "inventory_level", "z_score",
            "anomaly_score", "method", "severity", "alert_type", "message"]
    flagged = flagged.sort_values(["severity", "anomaly_score"], ascending=[True, False])[cols]   # 'high' sorts before 'medium'
    flagged.to_csv(OUT / "anomaly_alerts.csv", index=False)

    # --- evaluation with injected anomalies ---
    rng = np.random.default_rng(SEED)
    normal = df.sample(3000, random_state=SEED)[FEATURES].copy()
    inj = df.sample(150, random_state=SEED + 1)[FEATURES].copy()
    inj["units_sold"] = inj["units_sold"] * rng.integers(5, 10, len(inj))
    inj["units_ordered"] = inj["units_ordered"] * rng.integers(4, 8, len(inj))
    inj["revenue"] = (inj["units_sold"] * inj["price"] * 0.9).round(2)
    X = pd.concat([normal, inj]); y = np.r_[np.zeros(len(normal)), np.ones(len(inj))]
    pred = (iso.predict(X) == -1).astype(int)
    fpr = float(((pred == 1) & (y == 0)).sum() / (y == 0).sum())
    ev = {"test_rows": len(X), "injected": len(inj), "detection_accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred),
          "recall": recall_score(y, pred), "false_positive_rate": fpr}
    summary = {"rows": len(df), "flagged_zscore": int(df.flag_zscore.sum()), "flagged_iso": int(df.flag_iso.sum()),
               "flagged_both": int((df.flag_zscore & df.flag_iso).sum()), "alerts": len(flagged),
               "high": int((flagged.severity == "high").sum()), "medium": int((flagged.severity == "medium").sum())}
    save_json("anomaly_eval.json", {"summary": summary, "evaluation": ev})
    print(summary); print({k: round(v, 4) if isinstance(v, float) else v for k, v in ev.items()})


if __name__ == "__main__":
    main()
