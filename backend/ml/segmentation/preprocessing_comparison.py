import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import (
    PowerTransformer,
    RobustScaler,
    StandardScaler,
)


FEATURES = [
    "purchase_frequency",
    "purchase_value",
    "customer_activity_days",
]

DATA_PATH = (
    "artifacts/milestone-2/segmentation/"
    "customer_segmentation_day1.csv"
)


def load_features() -> pd.DataFrame:
    """Load the customer-level feature dataset."""

    df = pd.read_csv(DATA_PATH)

    missing = set(FEATURES) - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required features: {sorted(missing)}"
        )

    return df[FEATURES].copy()


def evaluate(
    name: str,
    X: np.ndarray,
) -> tuple[str, float]:

    model = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10,
    )

    labels = model.fit_predict(X)

    score = silhouette_score(
        X,
        labels,
    )

    return name, float(score)


def main() -> None:

    print("=" * 70)
    print("MARKETMINDAI - M2 SEGMENTATION PREPROCESSING COMPARISON")
    print("=" * 70)

    features = load_features()

    results = []

    # ---------------------------------------------------------
    # 1. Raw + StandardScaler
    # ---------------------------------------------------------

    standard_scaled = StandardScaler().fit_transform(
        features
    )

    results.append(
        evaluate(
            "Raw + StandardScaler",
            standard_scaled,
        )
    )

    # ---------------------------------------------------------
    # 2. Raw + RobustScaler
    # ---------------------------------------------------------

    robust_scaled = RobustScaler().fit_transform(
        features
    )

    results.append(
        evaluate(
            "Raw + RobustScaler",
            robust_scaled,
        )
    )

    # ---------------------------------------------------------
    # 3. PowerTransformer
    #
    # PowerTransformer estimates a transformation that makes
    # the feature distributions more Gaussian-like.
    # ---------------------------------------------------------

    power_scaled = PowerTransformer(
        method="yeo-johnson",
        standardize=True,
    ).fit_transform(features)

    results.append(
        evaluate(
            "Yeo-Johnson + Standardization",
            power_scaled,
        )
    )

    # ---------------------------------------------------------
    # 4. Log1p + StandardScaler
    #
    # Included because we already tested it in the main
    # pipeline. This gives us an explicit benchmark.
    # ---------------------------------------------------------

    log_features = np.log1p(features)

    log_scaled = StandardScaler().fit_transform(
        log_features
    )

    results.append(
        evaluate(
            "Log1p + StandardScaler",
            log_scaled,
        )
    )

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    results_df = (
        pd.DataFrame(
            results,
            columns=[
                "preprocessing",
                "silhouette_score",
            ],
        )
        .sort_values(
            "silhouette_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )
    output_path =\
    (
        "artifacts/milestone-2/segmentation/"
        "preprocessing_comparison.csv"
    )

    results_df.to_csv(
        output_path,
        index=False,
    )

    print(f"\nSaved comparison: {output_path}")
    print("\nPreprocessing comparison:")
    print(
        results_df.to_string(
            index=False,
        )
    )

    best = results_df.iloc[0]

    print("\nBest candidate:")
    print(
        f"{best['preprocessing']} "
        f"→ silhouette = "
        f"{best['silhouette_score']:.4f}"
    )


if __name__ == "__main__":
    main()