"""
MarketMind AI - Milestone 3, Day 7-8: Churn Prediction Complete
Place in: ml/   (next to churn_setup.py)
Run:      python churn_models.py

1. Trains Logistic Regression, Random Forest and XGBoost on the Day 5-6 dataset
2. Compares them with Precision / Recall / F1 / ROC-AUC on the held-out test set
   AND with 5-fold cross-validation (a single 20% split is too noisy to crown a winner)
3. Uses the best model's probabilities to assign High / Medium / Low retention risk
4. Cross-checks risk against the Milestone 2 customer segments
5. Scores EVERY customer as of the latest date -> outputs/churn_predictions.csv
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from churn_setup import (CHURN_DAYS, FEATURE_COLS, ML_DIR, build_churn_dataset,
                         build_features, get_train_test)

HIGH_RISK, MEDIUM_RISK = 0.7, 0.4      # thresholds; practice task: change these
OUT_DIR = ML_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)


def find_input(pattern):
    """Look in ml/outputs/ first, then ml/ (segmentation.py writes to the folder it is run from)."""
    for folder in (ML_DIR / "outputs", ML_DIR):
        hits = sorted(folder.glob(pattern))
        if hits:
            return hits[0]
    raise FileNotFoundError(f"{pattern} not found in {ML_DIR / 'outputs'} or {ML_DIR}")


feats, orders, cutoff, end_date = build_churn_dataset()
X_train, X_test, y_train, y_test = get_train_test(feats)
print(f"Churn rate {feats['churned'].mean():.1%} | train {len(X_train):,} / test {len(X_test):,}\n")

# ---------------------------------------------------------------- 1. three models
# FIX: scaling is wrapped in a Pipeline with Logistic Regression, so every model
# exposes the same fit / predict / predict_proba interface and the scaler can
# never be applied inconsistently (also required for clean cross-validation).
models = {
    "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(random_state=42, max_iter=1000)),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "XGBoost": XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
}
for model in models.values():
    model.fit(X_train, y_train)

# ---------------------------------------------------------------- 2a. held-out test set
scores = {}
print("=== Held-out test set ===")
for name, model in models.items():
    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)[:, 1]
    p = precision_score(y_test, pred, zero_division=0)
    r = recall_score(y_test, pred, zero_division=0)
    f = f1_score(y_test, pred, zero_division=0)
    auc = roc_auc_score(y_test, prob)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    scores[name] = {"precision": p, "recall": r, "f1": f, "auc": auc}
    print(f"{name:20s} Precision={p:.2f} Recall={r:.2f} F1={f:.2f} AUC={auc:.3f}"
          f"   (caught {tp}, missed {fn}, false alarms {fp})")

# ---------------------------------------------------------------- 2b. 5-fold cross-validation
print("\n=== 5-fold cross-validation (mean over folds, whole dataset) ===")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = {}
for name, model in models.items():
    res = cross_validate(model, feats[FEATURE_COLS], feats["churned"], cv=skf,
                         scoring=["precision", "recall", "f1", "roc_auc"])
    cv_scores[name] = {k: res[f"test_{k}"].mean() for k in ("precision", "recall", "f1", "roc_auc")}
    c = cv_scores[name]
    print(f"{name:20s} Precision={c['precision']:.2f} Recall={c['recall']:.2f} "
          f"F1={c['f1']:.2f} AUC={c['roc_auc']:.3f}")

# FIX: pick the winner on cross-validated F1 (more stable than one 20% split).
# If the top models are within ~0.02 F1 they are statistically indistinguishable
# on this data -- say so, and prefer the higher-Recall one (missed churners cost more).
ranked = sorted(cv_scores, key=lambda n: cv_scores[n]["f1"], reverse=True)
best = ranked[0]
close = [n for n in ranked if cv_scores[best]["f1"] - cv_scores[n]["f1"] <= 0.02]
if len(close) > 1:
    best = max(close, key=lambda n: cv_scores[n]["recall"])
    print(f"\nModels within 0.02 F1 of the top: {close} -> choosing the higher-Recall one.")
print(f"Selected model: {best}")
print("Note: churn is only moderately predictable from order history (AUC ~0.7); "
      "treat probabilities as a ranking for outreach, not certainties.")


# ---------------------------------------------------------------- 3. probabilities -> risk categories
def proba(name, X):
    return models[name].predict_proba(X)[:, 1]


def categorize_risk(prob):
    if prob >= HIGH_RISK:
        return "High Risk"
    elif prob >= MEDIUM_RISK:
        return "Medium Risk"
    return "Low Risk"


results = X_test.copy()
results["CustomerID"] = feats.loc[X_test.index, "CustomerID"]
results["churn_probability"] = proba(best, X_test).round(2)
results["retention_risk"] = results["churn_probability"].apply(categorize_risk)
print(f"\n=== Test-set risk buckets ({best}, thresholds {HIGH_RISK}/{MEDIUM_RISK}) ===")
print(results["retention_risk"].value_counts().to_string())

# ---------------------------------------------------------------- 4. cross-check with M2 segments
segments = pd.read_csv(find_input("segment*assignments.csv"))[["CustomerID", "segment"]]
check = results.merge(segments, on="CustomerID", how="left")
print("\n=== Retention risk by segment (test set) ===")
print(pd.crosstab(check["segment"], check["retention_risk"]).to_string())
print("Do most High Risk customers fall in 'Lapsed / One-Time Buyers'? If so, the model and "
      "the segmentation agree.\n(Segments use data up to the final date, so treat this as a "
      "sanity check, not a score.)")

# ---------------------------------------------------------------- 5. score every customer, as of today
current = build_features(orders, end_date + pd.Timedelta(days=1))
current["churn_probability"] = proba(best, current[FEATURE_COLS]).round(3)
current["retention_risk"] = current["churn_probability"].apply(categorize_risk)
current = current.merge(segments, on="CustomerID", how="left")
current["model_used"] = best
current.sort_values("churn_probability", ascending=False).to_csv(OUT_DIR / "churn_predictions.csv", index=False)

print(f"\nScored {len(current):,} customers -> {OUT_DIR / 'churn_predictions.csv'}")
print(current["retention_risk"].value_counts().to_string())