from pathlib import Path

import pandas as pd

from backend.ml.segmentation.hierarchical_model import (
    train_hierarchical,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
    / "customer_segmentation_day1.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
)


def main() -> None:
    print("=" * 70)
    print("MARKETMINDAI - M2 DAY 3")
    print("HIERARCHICAL CUSTOMER CLUSTERING")
    print("=" * 70)

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input segmentation result not found: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    hierarchical_df, _, model = train_hierarchical(
        df,
        n_clusters=4,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "customer_segmentation_hierarchical.csv"
    )

    hierarchical_df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nHierarchical clusters created: "
        f"{model.n_clusters}"
    )

    print("\nHierarchical cluster distribution:")
    print(
        hierarchical_df[
            "cluster_hierarchical"
        ]
        .value_counts()
        .sort_index()
    )

    print(
        f"\nSaved: {output_path}"
    )

    print(
        "\nK-Means and hierarchical clustering "
        "will be compared before assigning "
        "business segment names."
    )


if __name__ == "__main__":
    main()