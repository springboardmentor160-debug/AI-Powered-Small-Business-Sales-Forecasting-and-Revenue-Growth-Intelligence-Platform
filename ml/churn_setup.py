"""M3: churn label, feature set and Logistic Regression baseline.

Deliberate deviation from the guide: the guide labels churn as "inactive > 90 days" AND uses inactivity as a feature,
which leaks the label into the features (the model would look ~perfect while learning nothing). Here we
  * pick a cutoff date 90 days before the end of the data,
  * build features ONLY from transactions before the cutoff,
  * label a customer churned = 1 if they made NO purchase in the 90 days after the cutoff.
The same feature function is then applied at today's date to score current customers."""
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from common import SEED, as_of_date, customer_features, load_online, save_json

HORIZON_DAYS = 90
FEATURES = ["order_frequency", "inactivity_days", "avg_order_value", "total_spend", "tenure_days", "avg_days_between_orders", "n_products"]


def build_training_set(tx):
    cutoff = as_of_date(tx) - pd.Timedelta(days=HORIZON_DAYS)
    feats = customer_features(tx[tx["InvoiceDate"] < cutoff], cutoff)
    active_after = set(tx.loc[tx["InvoiceDate"] >= cutoff, "CustomerID"])
    feats["churned"] = (~feats["customer_id"].isin(active_after)).astype(int)
    return feats, cutoff


def metrics(name, y, pred):
    return {"model": name, "accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred, zero_division=0),
            "recall": recall_score(y, pred), "f1": f1_score(y, pred)}


def split(feats):
    return train_test_split(feats[FEATURES], feats["churned"], test_size=0.2, random_state=SEED, stratify=feats["churned"])


def main():
    feats, cutoff = build_training_set(load_online())
    print(f"Cutoff {cutoff.date()} | customers {len(feats):,} | churn rate {feats['churned'].mean():.1%}")
    Xtr, Xte, ytr, yte = split(feats)
    sc = StandardScaler().fit(Xtr)
    lr = LogisticRegression(random_state=SEED, max_iter=1000).fit(sc.transform(Xtr), ytr)
    m = metrics("Logistic Regression", yte, lr.predict(sc.transform(Xte)))
    base_rate = 1 - yte.mean()
    print(m, f"| always-'not churned' accuracy would be {base_rate:.2%}")
    save_json("churn_baseline.json", m)


if __name__ == "__main__":
    main()
