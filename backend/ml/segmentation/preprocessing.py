import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler


SEGMENTATION_FEATURES = [
    "purchase_frequency",
    "purchase_value",
    "customer_activity_days",
]


def prepare_segmentation_features(
    customer_features: pd.DataFrame,
) -> tuple[np.ndarray, RobustScaler]:
    """
    Prepare customer features for K-Means.

    Processing:
        1. Validate required features.
        2. Keep original business features unchanged.
        3. Apply RobustScaler for the ML representation.

    RobustScaler uses the median and interquartile range,
    reducing the influence of extreme observations without
    deleting legitimate customers.

    Returns:
        X_scaled
        fitted RobustScaler
    """

    missing_features = (
        set(SEGMENTATION_FEATURES)
        - set(customer_features.columns)
    )

    if missing_features:
        raise ValueError(
            f"Missing segmentation features: "
            f"{sorted(missing_features)}"
        )

    features = customer_features[
        SEGMENTATION_FEATURES
    ].copy()

    if features.isna().any().any():
        raise ValueError(
            "Segmentation features contain missing values."
        )

    if (features < 0).any().any():
        raise ValueError(
            "Segmentation features must be non-negative."
        )

    scaler = RobustScaler()

    X_scaled = scaler.fit_transform(features)

    return X_scaled, scaler