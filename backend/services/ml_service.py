"""Load Milestone 3 artifacts (recommendations, churn, anomalies).

Same pattern as segmentation_service: the heavy modelling runs offline in
`python -m backend.ml.run_milestone3` and the API only reads the results.
"""

import json
import logging
from functools import lru_cache
from pathlib import Path

import pandas as pd

from backend.config import (
    ANOMALY_ARTIFACT_DIR,
    CHURN_ARTIFACT_DIR,
    RECOMMENDATION_ARTIFACT_DIR,
)

logger = logging.getLogger(__name__)

RISK_LEVELS = ("High Risk", "Medium Risk", "Low Risk")

# Codes must stay text: "22759" and "85123A" are both StockCodes, and
# invoice numbers would otherwise be turned into integers.
TEXT_COLUMNS = {
    "StockCode": str,
    "reference": str,
    "antecedent_code": str,
    "consequent_code": str,
    "product_code": str,
    "upsell_code": str,
}


def _records(df: pd.DataFrame) -> list[dict]:
    """DataFrame -> JSON-safe list of dicts (NaN becomes None)."""
    return json.loads(df.to_json(orient="records"))


@lru_cache(maxsize=16)
def _cached(path_str: str, mtime: float) -> pd.DataFrame:
    return pd.read_csv(path_str, dtype=TEXT_COLUMNS)


def _load(path: Path) -> pd.DataFrame:
    """Read an artifact, re-reading only when the file changes."""
    if not path.exists():
        raise FileNotFoundError(
            f"Artifact {path.name} not found. Run "
            "`python -m backend.ml.run_milestone3` first."
        )
    return _cached(str(path), path.stat().st_mtime).copy()


# ------------------------------------------------------------------
# Recommendations
# ------------------------------------------------------------------

def get_customer_recommendations(customer_id: int, top_n: int = 5) -> dict:
    """'Recommended for you' for one customer (cold-start -> popular items)."""
    recs = _load(RECOMMENDATION_ARTIFACT_DIR / "customer_recommendations.csv")
    mine = recs[recs["Customer ID"] == customer_id].sort_values("rank").head(top_n)

    if mine.empty:
        popular = _load(RECOMMENDATION_ARTIFACT_DIR / "popular_products.csv").head(top_n)
        return {
            "customer_id": customer_id,
            "source": "popular_products",
            "note": "No purchase history for this customer, showing best sellers.",
            "recommendations": _records(
                popular.rename(columns={"median_price": "unit_price"})[
                    ["StockCode", "Description", "unit_price"]
                ]
            ),
        }

    return {
        "customer_id": customer_id,
        "source": "collaborative_filtering",
        "note": None,
        "recommendations": _records(
            mine[["rank", "StockCode", "Description", "unit_price", "score"]]
        ),
    }


def get_product_recommendations(stock_code: str, top_n: int = 5) -> dict:
    """'Frequently bought with' and upsell suggestions for one product."""
    rules = _load(RECOMMENDATION_ARTIFACT_DIR / "association_rules.csv")
    upsell = _load(RECOMMENDATION_ARTIFACT_DIR / "product_upsell.csv")

    code = str(stock_code).strip().upper()
    rules["antecedent_code"] = rules["antecedent_code"].astype(str).str.upper()
    upsell["product_code"] = upsell["product_code"].astype(str).str.upper()

    bought_with = (
        rules[rules["antecedent_code"] == code]
        .sort_values("lift", ascending=False)
        .head(top_n)
    )
    upsell_rows = upsell[upsell["product_code"] == code].sort_values("rank").head(top_n)

    product_name = None
    if not bought_with.empty:
        product_name = bought_with.iloc[0]["antecedent_name"]
    elif not upsell_rows.empty:
        product_name = upsell_rows.iloc[0]["product_name"]

    return {
        "stock_code": code,
        "product_name": product_name,
        "frequently_bought_with": _records(
            bought_with[
                ["consequent_code", "consequent_name", "support", "confidence", "lift"]
            ]
        ),
        "upsell_opportunities": _records(
            upsell_rows[
                [
                    "upsell_code", "upsell_name", "upsell_price",
                    "price_uplift_pct", "similarity",
                ]
            ]
        ),
    }


def get_full_recommendations(customer_id: int, stock_code: str | None = None) -> dict:
    """Combined output from the mentor guide: personalised + cross-sell."""
    result = {
        "recommended_for_you": get_customer_recommendations(customer_id),
        "frequently_bought_with": [],
        "upsell_opportunities": [],
    }
    if stock_code:
        product = get_product_recommendations(stock_code)
        result["frequently_bought_with"] = product["frequently_bought_with"]
        result["upsell_opportunities"] = product["upsell_opportunities"]
    return result


def get_recommendation_overview() -> dict:
    rules = _load(RECOMMENDATION_ARTIFACT_DIR / "association_rules.csv")
    evaluation = _load(RECOMMENDATION_ARTIFACT_DIR / "recommendation_evaluation.csv")
    upsell = _load(RECOMMENDATION_ARTIFACT_DIR / "product_upsell.csv")

    top_rules = rules.sort_values(["lift", "support"], ascending=False)
    # Show a spread of products, not only colour variants of one product.
    top_rules = top_rules.drop_duplicates("antecedent_code").head(10)

    return {
        "rule_count": int(len(rules)),
        "upsell_pair_count": int(len(upsell)),
        "top_rules": _records(
            top_rules[
                [
                    "antecedent_name", "consequent_name",
                    "support", "confidence", "lift",
                ]
            ]
        ),
        "evaluation": _records(evaluation),
    }


# ------------------------------------------------------------------
# Churn
# ------------------------------------------------------------------

def get_churn_overview(
    top_n: int = 25,
    risk: str | None = None,
    active_only: bool = False,
) -> dict:
    predictions = _load(CHURN_ARTIFACT_DIR / "churn_predictions.csv")
    comparison = _load(CHURN_ARTIFACT_DIR / "churn_model_comparison.csv")
    by_segment = _load(CHURN_ARTIFACT_DIR / "churn_risk_by_segment.csv")
    importance = _load(CHURN_ARTIFACT_DIR / "churn_feature_importance.csv")

    info_path = CHURN_ARTIFACT_DIR / "churn_run_info.json"
    info = json.loads(info_path.read_text()) if info_path.exists() else {}

    predictions_view = predictions
    if risk is not None:
        if risk not in RISK_LEVELS:
            raise ValueError(f"risk must be one of {list(RISK_LEVELS)}")
        predictions_view = predictions_view[predictions_view["retention_risk"] == risk]
    if active_only:
        # Actionable list: customers still ordering who are likely to stop.
        predictions_view = predictions_view[~predictions_view["already_inactive_90d"]]

    counts = predictions["retention_risk"].value_counts()
    # Customers already silent for 90+ days are lost, not "at risk";
    # the business can still try win-back, so they are shown separately.
    active = predictions[~predictions["already_inactive_90d"]]
    active_counts = active["retention_risk"].value_counts()

    return {
        "run_info": info,
        "total_customers": int(len(predictions)),
        "risk_counts": {level: int(counts.get(level, 0)) for level in RISK_LEVELS},
        "still_active_customers": int(len(active)),
        "still_active_risk_counts": {
            level: int(active_counts.get(level, 0)) for level in RISK_LEVELS
        },
        "model_comparison": _records(comparison),
        "feature_importance": _records(importance),
        "risk_by_segment": _records(by_segment),
        "customers": _records(
            predictions_view.sort_values("churn_probability", ascending=False).head(top_n)
        ),
    }


def get_customer_churn(customer_id: int) -> dict | None:
    predictions = _load(CHURN_ARTIFACT_DIR / "churn_predictions.csv")
    row = predictions[predictions["Customer ID"] == customer_id]
    if row.empty:
        return None
    return _records(row)[0]


# ------------------------------------------------------------------
# Anomalies
# ------------------------------------------------------------------

def get_anomaly_overview(
    top_n: int = 50,
    alert_type: str | None = None,
    severity: str | None = None,
) -> dict:
    alerts = _load(ANOMALY_ARTIFACT_DIR / "fraud_inventory_alerts.csv")

    info_path = ANOMALY_ARTIFACT_DIR / "anomaly_run_info.json"
    info = json.loads(info_path.read_text()) if info_path.exists() else {}

    view = alerts
    if alert_type:
        view = view[view["alert_type"] == alert_type]
    if severity:
        view = view[view["severity"] == severity]

    return {
        "run_info": info,
        "total_alerts": int(len(alerts)),
        "by_type": {
            str(key): int(value)
            for key, value in alerts["alert_type"].value_counts().items()
        },
        "by_severity": {
            str(key): int(value)
            for key, value in alerts["severity"].value_counts().items()
        },
        "matching_alerts": int(len(view)),
        "alerts": _records(view.head(top_n)),
    }
