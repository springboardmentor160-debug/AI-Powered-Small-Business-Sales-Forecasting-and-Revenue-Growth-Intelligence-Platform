"""Unit tests for the Milestone 3 modelling code (no database or API needed)."""

import numpy as np
import pandas as pd

from backend.ml import anomaly, churn, recommendations


def make_sales(rows):
    """rows: (customer, invoice, date, stock_code, quantity, price)"""
    df = pd.DataFrame(
        rows,
        columns=["Customer ID", "Invoice", "InvoiceDate", "StockCode", "Quantity", "Price"],
    )
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["line_total"] = df["Quantity"] * df["Price"]
    df["Description"] = "Product " + df["StockCode"]
    return df


# ------------------------------------------------------------------
# Churn
# ------------------------------------------------------------------

def test_risk_categories_follow_thresholds():
    assert churn.categorize_risk(0.95) == "High Risk"
    assert churn.categorize_risk(0.70) == "High Risk"
    assert churn.categorize_risk(0.55) == "Medium Risk"
    assert churn.categorize_risk(0.40) == "Medium Risk"
    assert churn.categorize_risk(0.10) == "Low Risk"


def test_churn_features_never_use_data_after_snapshot():
    snapshot = pd.Timestamp("2011-01-01")
    sales = make_sales(
        [
            (1, "A1", "2010-11-01", "P1", 2, 5.0),
            (1, "A2", "2010-12-01", "P2", 1, 10.0),
            # After the snapshot: must be ignored by the features.
            (1, "A3", "2011-02-01", "P3", 100, 50.0),
            # Customer 2 only exists after the snapshot: no features at all.
            (2, "B1", "2011-02-01", "P1", 1, 5.0),
        ]
    )
    invoices = churn.build_invoice_table(sales)
    feats = churn.build_features(sales, invoices, snapshot)

    assert list(feats["Customer ID"]) == [1]
    row = feats.iloc[0]
    assert row["frequency"] == 2
    assert row["total_spend"] == 20.0          # 10 + 10, not including A3
    assert row["distinct_products"] == 2
    assert row["recency_days"] == 31           # 2010-12-01 -> 2011-01-01


def test_churn_label_is_no_purchase_in_following_window():
    snapshot = pd.Timestamp("2011-01-01")
    sales = make_sales(
        [
            (1, "A1", "2010-12-01", "P1", 1, 5.0),
            (1, "A2", "2011-02-15", "P1", 1, 5.0),   # returns inside 90 days
            (2, "B1", "2010-12-01", "P1", 1, 5.0),   # never returns
            (3, "C1", "2010-12-01", "P1", 1, 5.0),
            (3, "C2", "2011-06-01", "P1", 1, 5.0),   # returns, but too late
        ]
    )
    invoices = churn.build_invoice_table(sales)
    labels = churn.build_labels(invoices, pd.Series([1, 2, 3]), snapshot)

    assert list(labels) == [0, 1, 1]


# ------------------------------------------------------------------
# Recommendations
# ------------------------------------------------------------------

def test_association_rule_metrics_are_correct(monkeypatch):
    monkeypatch.setattr(recommendations, "MIN_SUPPORT", 0.1)
    monkeypatch.setattr(recommendations, "MIN_CONFIDENCE", 0.0)

    baskets = []
    # 10 invoices: A and B together in 4, A alone in 1, B alone in 1, C in 4.
    for i in range(4):
        baskets += [(None, f"AB{i}", "2011-01-01", "A", 1, 1.0), (None, f"AB{i}", "2011-01-01", "B", 1, 1.0)]
    baskets += [(None, "A_only", "2011-01-01", "A", 1, 1.0)]
    baskets += [(None, "B_only", "2011-01-01", "B", 1, 1.0)]
    for i in range(4):
        baskets += [(None, f"C{i}", "2011-01-01", "C", 1, 1.0)]
    sales = make_sales(baskets)
    catalog = recommendations.build_catalog(sales)

    rules = recommendations.mine_association_rules(sales, catalog)
    rule = rules[(rules["antecedent_code"] == "A") & (rules["consequent_code"] == "B")].iloc[0]

    assert rule["support"] == 0.4                  # 4 of 10 invoices
    assert rule["confidence"] == 0.8               # 4 of the 5 invoices with A
    assert abs(rule["lift"] - 1.6) < 1e-3          # 0.8 / (5 of 10 invoices contain B)
    assert rules[(rules["antecedent_code"] == "A") & (rules["consequent_code"] == "C")].empty


def test_collaborative_filtering_never_recommends_owned_products():
    sales = make_sales(
        [
            (1, "I1", "2011-01-01", "A", 2, 1.0),
            (1, "I1", "2011-01-01", "B", 2, 1.0),
            (2, "I2", "2011-01-01", "A", 3, 1.0),
            (2, "I2", "2011-01-01", "B", 1, 1.0),
            (2, "I2", "2011-01-01", "C", 1, 1.0),
            (3, "I3", "2011-01-01", "D", 5, 1.0),
        ]
    )
    matrix, customers, products = recommendations.build_customer_product_matrix(sales)
    idx, score = recommendations.collaborative_top_n(matrix, n_neighbours=2, top_n=1)

    customer_1 = list(customers).index(1)
    # Customer 1 resembles customer 2, who also bought C.
    assert products[idx[customer_1, 0]] == "C"
    for i in range(len(customers)):
        assert matrix[i, idx[i, 0]] == 0 or score[i, 0] < 0   # never an owned product


# ------------------------------------------------------------------
# Anomaly detection
# ------------------------------------------------------------------

def test_robust_z_is_not_distorted_by_one_huge_value():
    values = pd.Series([10, 11, 9, 10, 12, 10, 11, 10_000])
    z = anomaly._robust_z(values)
    assert z.iloc[-1] > 3.5
    assert (z.iloc[:-1].abs() < 3.5).all()


def test_injected_giant_order_is_flagged_by_both_methods():
    rng = np.random.default_rng(0)
    rows = []
    for i in range(400):
        for line in range(int(rng.integers(1, 5))):
            rows.append(
                (None, f"N{i}", "2011-03-01", f"P{line}", int(rng.integers(1, 12)), float(rng.uniform(1, 5)))
            )
    # One order of 20,000 units across a few products.
    for line in range(3):
        rows.append((None, "HUGE", "2011-03-02", f"P{line}", 7000, 4.0))
    sales = make_sales(rows)

    flagged, summary = anomaly.detect_sales_anomalies(sales)
    huge = flagged[flagged["Invoice"] == "HUGE"]

    assert len(huge) == 1
    assert huge.iloc[0]["detected_by"] == "both"
    assert summary["invoices_checked"] == 401


# ------------------------------------------------------------------
# Behaviour segments
# ------------------------------------------------------------------

def test_behaviour_segments_follow_the_rules():
    from backend.ml import churn_segments as seg

    frame = pd.DataFrame(
        {
            #            new  one-time  lost  champion  loyal  at-risk  occasional
            "frequency":    [1,    1,     4,     8,       4,      3,       2],
            "recency_days": [20,  200,   400,    10,      30,    150,      40],
            "tenure_days":  [20,  200,   900,   600,     300,    500,     200],
            "total_spend":  [50,   50,   400,  9000,     500,    300,      80],
        }
    )
    result = seg.assign_behaviour_segments(frame, top_spend_threshold=5000)

    assert list(result) == [
        seg.NEW,
        seg.ONE_TIME,
        seg.HIBERNATING,
        seg.CHAMPIONS,
        seg.LOYAL,
        seg.AT_RISK,
        seg.OCCASIONAL,
    ]


def test_segment_validation_compares_actual_and_predicted():
    from backend.ml import churn_segments as seg

    segments = pd.Series([seg.CHAMPIONS] * 4 + [seg.ONE_TIME] * 4)
    actual = pd.Series([0, 0, 0, 1, 1, 1, 1, 0])
    predicted = pd.Series([0.1, 0.2, 0.1, 0.2, 0.9, 0.8, 0.9, 0.7])

    table = seg.validate_segments(segments, actual, predicted).set_index("behaviour_segment")

    assert table.loc[seg.CHAMPIONS, "actual_churn_rate"] == 0.25
    assert table.loc[seg.ONE_TIME, "actual_churn_rate"] == 0.75
    assert table.loc[seg.ONE_TIME, "churn_vs_average"] == 1.5      # 0.75 / 0.5
