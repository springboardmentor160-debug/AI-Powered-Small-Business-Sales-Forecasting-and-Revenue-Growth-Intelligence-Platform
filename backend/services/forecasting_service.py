import logging
from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)


def load_m5_demand_forecast(
    comparison_path: Path,
    predictions_path: Path,
) -> dict:
    """
    Load M5 model comparison and XGBoost prediction artifacts.

    The original artifact files are never modified.
    """

    if not comparison_path.exists():
        raise FileNotFoundError(
            "M5 model comparison artifact not found."
        )

    comparison = pd.read_csv(
        comparison_path
    )

    required_columns = {
        "model",
        "mae",
        "rmse",
    }

    if not required_columns.issubset(
        comparison.columns
    ):
        raise ValueError(
            "M5 model comparison artifact "
            "has an unexpected schema."
        )

    model_columns = [
        column
        for column in [
            "model",
            "mae",
            "rmse",
            "mae_change_vs_baseline_pct",
            "rmse_change_vs_baseline_pct",
        ]
        if column in comparison.columns
    ]

    result = {
        "validation_horizon_days": 28,
        "validation_start": (
            str(
                comparison[
                    "validation_start"
                ].iloc[0]
            )
            if "validation_start"
            in comparison.columns
            and not comparison.empty
            else None
        ),
        "validation_end": (
            str(
                comparison[
                    "validation_end"
                ].iloc[0]
            )
            if "validation_end"
            in comparison.columns
            and not comparison.empty
            else None
        ),
        "models": comparison[
            model_columns
        ].to_dict(
            orient="records"
        ),
    }

    if predictions_path.exists():

        predictions = pd.read_csv(
            predictions_path
        )

        if "date" in predictions.columns:

            predictions["date"] = (
                pd.to_datetime(
                    predictions["date"],
                    errors="coerce",
                )
                .dt.strftime(
                    "%Y-%m-%d"
                )
            )

        for column in [
            "actual_units",
            "predicted_units",
            "absolute_error",
            "squared_error",
        ]:

            if column in predictions.columns:

                predictions[column] = (
                    pd.to_numeric(
                        predictions[column],
                        errors="coerce",
                    )
                    .fillna(0)
                )

        result["predictions"] = (
            predictions
            .fillna("")
            .to_dict(
                orient="records"
            )
        )

    logger.info(
        "M5 demand forecast artifacts loaded successfully."
    )

    return result

def load_uci_revenue_forecast(
    comparison_path: Path,
    predictions_path: Path,
) -> dict:
    """
    Load UCI revenue model comparison and prediction artifacts.

    The original artifact files are never modified.
    """

    if not comparison_path.exists():
        raise FileNotFoundError(
            "UCI model comparison artifact not found."
        )

    comparison = pd.read_csv(
        comparison_path
    )

    required_columns = {
        "model",
        "mae",
        "rmse",
    }

    if not required_columns.issubset(
        comparison.columns
    ):
        raise ValueError(
            "UCI model comparison artifact "
            "has an unexpected schema."
        )

    validation = {}

    for column in [
        "test_split",
        "test_start",
        "test_end",
        "test_rows",
    ]:
        if (
            column in comparison.columns
            and not comparison.empty
        ):
            value = comparison[
                column
            ].iloc[0]

            if column == "test_rows":
                validation[column] = int(
                    value
                )
            else:
                validation[column] = str(
                    value
                )

    result = {
        "validation": validation,
        "models": comparison[
            [
                "model",
                "mae",
                "rmse",
            ]
        ].to_dict(
            orient="records"
        ),
    }

    if predictions_path.exists():

        predictions = pd.read_csv(
            predictions_path
        )

        if "date" in predictions.columns:
            predictions["date"] = (
                pd.to_datetime(
                    predictions["date"],
                    errors="coerce",
                )
                .dt.strftime(
                    "%Y-%m-%d"
                )
            )

        numeric_columns = [
            "actual_revenue",
            "prophet_prediction",
            "random_forest_prediction",
            "xgboost_prediction",
        ]

        for column in numeric_columns:
            if column in predictions.columns:
                predictions[column] = (
                    pd.to_numeric(
                        predictions[column],
                        errors="coerce",
                    )
                    .fillna(0)
                )

        result["predictions"] = (
            predictions
            .fillna("")
            .to_dict(
                orient="records"
            )
        )

    logger.info(
        "UCI revenue forecast artifacts loaded successfully."
    )

    return result
def load_forecast_model_comparison(
    uci_path: Path,
    m5_path: Path,
) -> dict:
    """
    Load UCI revenue and M5 demand model comparison artifacts.

    The original artifact files are never modified.
    """

    if not uci_path.exists():
        raise FileNotFoundError(
            "UCI comparison artifact not found."
        )

    if not m5_path.exists():
        raise FileNotFoundError(
            "M5 comparison artifact not found."
        )

    uci = pd.read_csv(
        uci_path
    )

    m5 = pd.read_csv(
        m5_path
    )

    required_columns = {
        "model",
        "mae",
        "rmse",
    }

    if not required_columns.issubset(
        uci.columns
    ):
        raise ValueError(
            "UCI comparison artifact "
            "has an unexpected schema."
        )

    if not required_columns.issubset(
        m5.columns
    ):
        raise ValueError(
            "M5 comparison artifact "
            "has an unexpected schema."
        )

    logger.info(
        "Forecast model comparison artifacts loaded successfully."
    )

    return {
        "uci_revenue_models": uci[
            [
                "model",
                "mae",
                "rmse",
            ]
        ].to_dict(
            orient="records"
        ),
        "m5_demand_models": m5[
            [
                "model",
                "mae",
                "rmse",
            ]
        ].to_dict(
            orient="records"
        ),
    }