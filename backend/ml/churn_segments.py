"""Behaviour segments used to sanity-check the churn model.

The Milestone 2 segmentation (K-Means on value/frequency) puts 91% of
customers into one group, so it cannot say much about churn. These segments
are rule-based RFM-style groups that describe HOW a customer buys, using
only recency, frequency, tenure and spend, so each one is easy to explain.

Rules are applied top to bottom; the first match wins.
"""

import numpy as np
import pandas as pd

NEW = "New Customers"
ONE_TIME = "One-Time Buyers"
HIBERNATING = "Hibernating / Lost"
CHAMPIONS = "Champions"
LOYAL = "Loyal Regulars"
AT_RISK = "At-Risk / Fading"
OCCASIONAL = "Occasional Buyers"

SEGMENT_ORDER = [CHAMPIONS, LOYAL, OCCASIONAL, NEW, AT_RISK, HIBERNATING, ONE_TIME]

SEGMENT_RULES = {
    NEW: "One order, first bought within the last 90 days",
    ONE_TIME: "One order only, more than 90 days ago",
    HIBERNATING: "Repeat buyer, silent for more than 270 days",
    CHAMPIONS: "5+ orders, ordering on their usual rhythm, top 20% by spend",
    LOYAL: "3+ orders, bought in the last 90 days, on their usual rhythm",
    AT_RISK: "Repeat buyer (2+ orders) silent for 90-270 days",
    OCCASIONAL: "Everyone else who is still active",
}

RECENT_DAYS = 90
LOST_DAYS = 270
CHAMPION_MIN_ORDERS = 5
LOYAL_MIN_ORDERS = 3
CHAMPION_SPEND_QUANTILE = 0.80


def assign_behaviour_segments(
    features: pd.DataFrame, top_spend_threshold: float | None = None
) -> pd.Series:
    """Return a segment name per row of `features`.

    Needs: frequency, recency_days, tenure_days, total_spend.
    `top_spend_threshold` lets the training snapshot and the live scoring
    use the same spend cut-off (otherwise it is the 80th percentile).
    """
    frequency = features["frequency"]
    recency = features["recency_days"]

    if top_spend_threshold is None:
        top_spend_threshold = features["total_spend"].quantile(CHAMPION_SPEND_QUANTILE)

    # Typical days between orders, measured inside the customer's active span.
    active_span = (features["tenure_days"] - recency).clip(lower=0)
    typical_gap = (active_span / (frequency - 1).clip(lower=1)).clip(lower=1)
    on_rhythm = recency / typical_gap

    conditions = [
        (frequency == 1) & (features["tenure_days"] <= RECENT_DAYS),
        frequency == 1,
        recency > LOST_DAYS,
        (frequency >= CHAMPION_MIN_ORDERS)
        & (on_rhythm <= 1.0)
        & (features["total_spend"] >= top_spend_threshold),
        (frequency >= LOYAL_MIN_ORDERS) & (on_rhythm <= 1.5) & (recency <= RECENT_DAYS),
        recency > RECENT_DAYS,
    ]
    names = [NEW, ONE_TIME, HIBERNATING, CHAMPIONS, LOYAL, AT_RISK]
    return pd.Series(
        np.select(conditions, names, default=OCCASIONAL),
        index=features.index,
        name="behaviour_segment",
    )


def validate_segments(
    segments: pd.Series, actual_churn: pd.Series, predicted_probability: pd.Series
) -> pd.DataFrame:
    """Per segment: real churn rate vs the model's predicted probability.

    `predicted_probability` must be out-of-sample (cross-validated), so this
    is a fair test and not the model grading its own homework.
    """
    frame = pd.DataFrame(
        {
            "segment": segments.to_numpy(),
            "actual_churn": actual_churn.to_numpy(),
            "predicted": predicted_probability.to_numpy(),
        }
    )
    overall = frame["actual_churn"].mean()
    table = frame.groupby("segment").agg(
        customers=("actual_churn", "size"),
        actual_churn_rate=("actual_churn", "mean"),
        avg_predicted_probability=("predicted", "mean"),
    )
    table["share_of_customers"] = table["customers"] / len(frame)
    table["churn_vs_average"] = table["actual_churn_rate"] / overall
    table["definition"] = pd.Series(SEGMENT_RULES)
    table = table.reindex([name for name in SEGMENT_ORDER if name in table.index])
    table.index.name = "behaviour_segment"
    return table.round(4).reset_index()
