"""Milestone 3, Day 9-10: Anomaly detection and fraud/inventory alerts.

Sales anomalies (per invoice):
    * Z-score method (the simple statistical approach).
    * Isolation Forest on several features at once.
Inventory anomalies:
    * Stock write-offs: lines with price 0 and negative quantity (damaged,
      lost, thrown away ...). The project has no real stock counts, so
      these recorded adjustments are the genuine inventory signal.
    * Demand spikes: a product's daily units far above its own normal.

Everything is merged into one alert table with a severity level.
"""

import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from backend.data_pipeline.sources.uci.loader import read_uci_transactions
from backend.ml.common import artifact_dir

logger = logging.getLogger(__name__)

Z_THRESHOLD = 3.0            # classic rule of thumb
CONTAMINATION = 0.005        # expect ~0.5% of invoices to be unusual
ROBUST_Z_THRESHOLD = 3.5     # modified z-score for write-offs / spikes
MIN_SPIKE_UNITS = 1000       # ignore small days, even if "spiky"
MIN_SPIKE_MULTIPLE = 10      # and require 10x the product's typical day
MIN_SPIKE_DAYS = 20          # product needs history to define "normal"
RANDOM_STATE = 42


def _robust_z(values: pd.Series) -> pd.Series:
    """Modified z-score (median / MAD). Not distorted by the outliers."""
    median = values.median()
    mad = (values - median).abs().median()
    if mad == 0:
        mad = values.std() or 1.0
    return 0.6745 * (values - median) / mad


# ------------------------------------------------------------------
# Sales anomalies
# ------------------------------------------------------------------

def build_invoice_features(sales: pd.DataFrame) -> pd.DataFrame:
    invoices = sales.groupby("Invoice").agg(
        InvoiceDate=("InvoiceDate", "max"),
        customer_id=("Customer ID", "first"),
        total_quantity=("Quantity", "sum"),
        total_amount=("line_total", "sum"),
        n_lines=("StockCode", "nunique"),
        max_line_quantity=("Quantity", "max"),
        max_unit_price=("Price", "max"),
    )
    invoices["avg_unit_price"] = invoices["total_amount"] / invoices["total_quantity"]
    return invoices.reset_index()


def detect_sales_anomalies(sales: pd.DataFrame):
    invoices = build_invoice_features(sales)

    # Method 1: Z-score on invoice value.
    mean, std = invoices["total_amount"].mean(), invoices["total_amount"].std()
    invoices["z_score"] = (invoices["total_amount"] - mean) / std
    invoices["flag_zscore"] = invoices["z_score"].abs() > Z_THRESHOLD

    # Method 2: Isolation Forest on several features at once.
    # log1p because order sizes are heavily right-skewed.
    features = [
        "total_quantity", "total_amount", "n_lines",
        "max_line_quantity", "max_unit_price", "avg_unit_price",
    ]
    X = np.log1p(invoices[features].clip(lower=0))
    forest = IsolationForest(
        n_estimators=200, contamination=CONTAMINATION, random_state=RANDOM_STATE
    )
    invoices["flag_isolation_forest"] = forest.fit_predict(X) == -1   # -1 = anomaly
    invoices["anomaly_score"] = -forest.score_samples(X)             # higher = stranger

    flagged = invoices[invoices["flag_zscore"] | invoices["flag_isolation_forest"]].copy()
    flagged["detected_by"] = np.select(
        [
            flagged["flag_zscore"] & flagged["flag_isolation_forest"],
            flagged["flag_zscore"],
        ],
        ["both", "zscore"],
        default="isolation_forest",
    )
    flagged["agreement"] = flagged["detected_by"] == "both"

    summary = {
        "invoices_checked": len(invoices),
        "zscore_flagged": int(invoices["flag_zscore"].sum()),
        "isolation_forest_flagged": int(invoices["flag_isolation_forest"].sum()),
        "flagged_by_both": int((invoices["flag_zscore"] & invoices["flag_isolation_forest"]).sum()),
        "z_threshold": Z_THRESHOLD,
        "contamination": CONTAMINATION,
    }
    return flagged.sort_values("anomaly_score", ascending=False), summary


# ------------------------------------------------------------------
# Inventory anomalies
# ------------------------------------------------------------------

def detect_stock_write_offs(catalog_prices: pd.Series) -> pd.DataFrame:
    """Recorded stock adjustments (price 0, negative quantity, no customer)."""
    raw = read_uci_transactions().rename(columns={"InvoiceNo": "Invoice", "UnitPrice": "Price"})
    raw["Invoice"] = raw["Invoice"].astype(str)

    # Same dedupe rule as the sales table: file 2 repeats 1,088 invoices.
    first = set(raw.loc[raw["_source_file"] == "online_retail_v1.csv", "Invoice"])
    raw = raw[~((raw["_source_file"] == "online_retail_v2.csv") & raw["Invoice"].isin(first))]

    writeoffs = raw[
        (raw["Price"] == 0) & (raw["Quantity"] < 0) & raw["Customer ID"].isna()
        & (~raw["StockCode"].astype(str).str.upper().isin({"M", "D", "S", "POST", "DOT"}))
    ].copy()
    writeoffs["StockCode"] = writeoffs["StockCode"].astype(str)
    writeoffs["units_written_off"] = -writeoffs["Quantity"]
    writeoffs["event_date"] = pd.to_datetime(writeoffs["InvoiceDate"]).dt.date
    writeoffs["reason_note"] = writeoffs["Description"].fillna("").str.strip()

    events = writeoffs.groupby(["StockCode", "event_date"], as_index=False).agg(
        units_written_off=("units_written_off", "sum"),
        reason_note=("reason_note", lambda s: next((x for x in s if x), "no reason recorded")),
        Invoice=("Invoice", "first"),
    )
    events["estimated_value"] = (
        events["units_written_off"] * events["StockCode"].map(catalog_prices)
    ).round(2)
    events["robust_z"] = _robust_z(np.log1p(events["units_written_off"])).round(2)
    return events[events["robust_z"] > ROBUST_Z_THRESHOLD].sort_values(
        "units_written_off", ascending=False
    )


def detect_demand_spikes(sales: pd.DataFrame) -> pd.DataFrame:
    """Daily units of a product vs that product's own typical day."""
    daily = (
        sales.assign(event_date=sales["InvoiceDate"].dt.date)
        .groupby(["StockCode", "event_date"], as_index=False)["Quantity"].sum()
    )
    stats = daily.groupby("StockCode")["Quantity"].agg(
        median_daily="median", days_sold="count"
    )
    daily = daily.join(stats, on="StockCode")
    daily = daily[(daily["days_sold"] >= MIN_SPIKE_DAYS) & (daily["Quantity"] >= MIN_SPIKE_UNITS)]

    log_units = np.log1p(daily["Quantity"])
    daily["robust_z"] = (
        log_units.groupby(daily["StockCode"]).transform(_robust_z)
    ).round(2)
    spikes = daily[daily["robust_z"] > ROBUST_Z_THRESHOLD].copy()
    spikes["times_normal"] = (spikes["Quantity"] / spikes["median_daily"].clip(lower=1)).round(1)
    spikes = spikes[spikes["times_normal"] >= MIN_SPIKE_MULTIPLE]
    return spikes.sort_values("robust_z", ascending=False)


# ------------------------------------------------------------------
# Alerts
# ------------------------------------------------------------------

def build_alerts(sales_flags, writeoffs, spikes, names: pd.Series) -> pd.DataFrame:
    alerts = []
    median_invoice = sales_flags["total_amount"].median()

    # Z-score-only invoices are mostly legitimate wholesale orders; they stay
    # in sales_anomalies.csv for review but do not raise alerts (avoids a flood).
    alertable = sales_flags[sales_flags["detected_by"] != "zscore"]

    for row in alertable.itertuples():
        high = row.agreement or row.total_amount > median_invoice * 50
        alerts.append(
            {
                "alert_type": "unusual_sales_activity",
                "reference": row.Invoice,
                "event_date": row.InvoiceDate.date().isoformat(),
                "severity": "high" if high else "medium",
                "detected_by": row.detected_by,
                "message": (
                    f"Invoice {row.Invoice} flagged: {int(row.total_quantity):,} units, "
                    f"{row.n_lines} products, value {row.total_amount:,.2f} "
                    f"(largest line {int(row.max_line_quantity):,} units)"
                ),
                "value": round(float(row.total_amount), 2),
            }
        )

    for row in writeoffs.itertuples():
        high = row.units_written_off >= 1000 or (
            pd.notna(row.estimated_value) and row.estimated_value >= 1000
        )
        alerts.append(
            {
                "alert_type": "stock_write_off",
                "reference": row.StockCode,
                "event_date": str(row.event_date),
                "severity": "high" if high else "medium",
                "detected_by": "robust_zscore",
                "message": (
                    f"{names.get(row.StockCode, row.StockCode)} ({row.StockCode}): "
                    f"{int(row.units_written_off):,} units written off - "
                    f"note: '{row.reason_note}'"
                ),
                "value": float(row.estimated_value) if pd.notna(row.estimated_value) else None,
            }
        )

    for row in spikes.itertuples():
        alerts.append(
            {
                "alert_type": "demand_spike",
                "reference": row.StockCode,
                "event_date": str(row.event_date),
                "severity": "high" if row.times_normal >= 50 else "medium",
                "detected_by": "robust_zscore",
                "message": (
                    f"{names.get(row.StockCode, row.StockCode)} ({row.StockCode}): "
                    f"{int(row.Quantity):,} units in one day, "
                    f"{row.times_normal}x its typical day"
                ),
                "value": float(row.Quantity),
            }
        )

    frame = pd.DataFrame(alerts)
    frame["severity_rank"] = frame["severity"].map({"high": 0, "medium": 1})
    frame = frame.sort_values(["severity_rank", "value"], ascending=[True, False]).drop(
        columns="severity_rank"
    )
    frame.insert(0, "alert_id", [f"ALT-{i:04d}" for i in range(1, len(frame) + 1)])
    return frame.reset_index(drop=True)


def run(sales: pd.DataFrame) -> dict:
    out = artifact_dir("anomaly")

    names = (
        sales[sales["Description"] != ""]
        .groupby("StockCode")["Description"].agg(lambda s: s.value_counts().index[0])
    )
    prices = sales.groupby("StockCode")["Price"].median()

    sales_flags, method_summary = detect_sales_anomalies(sales)
    writeoffs = detect_stock_write_offs(prices)
    spikes = detect_demand_spikes(sales)
    alerts = build_alerts(sales_flags, writeoffs, spikes, names)

    sales_flags.drop(columns=["flag_zscore", "flag_isolation_forest"]).round(
        {"z_score": 3, "anomaly_score": 4, "total_amount": 2, "avg_unit_price": 2}
    ).to_csv(out / "sales_anomalies.csv", index=False)
    writeoffs.to_csv(out / "stock_write_offs.csv", index=False)
    spikes.to_csv(out / "demand_spikes.csv", index=False)
    alerts.to_csv(out / "fraud_inventory_alerts.csv", index=False)

    summary = {
        **method_summary,
        "stock_write_off_alerts": len(writeoffs),
        "demand_spike_alerts": len(spikes),
        "total_alerts": len(alerts),
        "high_severity_alerts": int((alerts["severity"] == "high").sum()),
    }
    pd.Series(summary).to_json(out / "anomaly_run_info.json", indent=2)
    logger.info("Anomaly detection done: %s", summary)
    return summary
