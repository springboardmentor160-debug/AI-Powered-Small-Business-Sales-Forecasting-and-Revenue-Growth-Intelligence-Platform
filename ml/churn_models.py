"""M3: Random Forest + XGBoost vs Logistic Regression, probability + High/Medium/Low risk per customer.
Outputs: outputs/churn_predictions.csv, churn_metrics.json"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from churn_setup import FEATURES, build_training_set, metrics, split
from common import OUT, SEED, as_of_date, customer_features, load_online, make_classifier, save_json


def risk(p):
    return "High Risk" if p >= 0.7 else "Medium Risk" if p >= 0.4 else "Low Risk"


def main():
    tx = load_online()
    feats, cutoff = build_training_set(tx)
    Xtr, Xte, ytr, yte = split(feats)
    rate = float(feats["churned"].mean())
    spw = (1 - rate) / rate if rate < 0.25 else 1.0     # only re-weight when churn is genuinely the rare class

    sc = StandardScaler().fit(Xtr)
    lr = LogisticRegression(random_state=SEED, max_iter=1000).fit(sc.transform(Xtr), ytr)
    rf = RandomForestClassifier(n_estimators=100, random_state=SEED, class_weight="balanced_subsample" if spw > 1 else None).fit(Xtr, ytr)
    xgb, xgb_name = make_classifier(spw); xgb.fit(Xtr, ytr)

    results = []
    for name, model, X in (("Logistic Regression", lr, sc.transform(Xte)), ("Random Forest", rf, Xte), (xgb_name, xgb, Xte)):
        m = metrics(name, yte, model.predict(X)); m["roc_auc"] = roc_auc_score(yte, model.predict_proba(X)[:, 1])
        results.append(m)
    best = max(results, key=lambda r: (r["f1"], r["recall"]))["model"]
    model = {"Logistic Regression": lr, "Random Forest": rf}.get(best, xgb)

    # score every customer as of "today" using the same feature definitions
    today = customer_features(tx, as_of_date(tx))
    X_now = sc.transform(today[FEATURES]) if best == "Logistic Regression" else today[FEATURES]
    today["churn_probability"] = model.predict_proba(X_now)[:, 1].round(3)
    today["retention_risk"] = today["churn_probability"].apply(risk)
    seg_path = OUT / "segment_assignments.csv"
    if seg_path.exists():
        seg = pd.read_csv(seg_path, dtype={"customer_id": str})[["customer_id", "segment"]]
        today = today.merge(seg, on="customer_id", how="left")
    today.sort_values("churn_probability", ascending=False).to_csv(OUT / "churn_predictions.csv", index=False)

    out = {"label": f"no purchase in the {90} days after {cutoff.date()}", "churn_rate": round(rate, 4), "test_size": len(yte),
           "results": results, "selected_model": best, "risk_counts": today["retention_risk"].value_counts().to_dict()}
    if "segment" in today:
        out["risk_by_segment"] = pd.crosstab(today["segment"], today["retention_risk"]).to_dict(orient="index")
    save_json("churn_metrics.json", out)
    print(pd.DataFrame(results).round(3).to_string(index=False)); print("Selected:", best, out["risk_counts"])


if __name__ == "__main__":
    main()
