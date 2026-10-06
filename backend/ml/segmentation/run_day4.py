from pathlib import Path

import pandas as pd

from backend.ml.segmentation.segment_naming import (
    assign_business_segment_names,
    attach_segment_names,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
    / "customer_segmentation_hierarchical.csv"
)

SUMMARY_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
    / "hierarchical_cluster_summary.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
)


def main() -> None:

    print("=" * 75)
    print("MARKETMINDAI - M2 DAY 4")
    print("BUSINESS CUSTOMER SEGMENT NAMING")
    print("=" * 75)

    customer_df = pd.read_csv(
        INPUT_PATH
    )

    summary_df = pd.read_csv(
        SUMMARY_PATH
    )

    # ---------------------------------------------------------
    # Assign business names from observed behavior.
    # ---------------------------------------------------------

    named_summary = (
        assign_business_segment_names(
            summary_df
        )
    )

    named_customers = (
        attach_segment_names(
            customer_df,
            named_summary,
        )
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_output = (
        OUTPUT_DIR
        / "named_segment_summary.csv"
    )

    customer_output = (
        OUTPUT_DIR
        / "customer_segments_final.csv"
    )

    named_summary.to_csv(
        summary_output,
        index=False,
    )

    named_customers.to_csv(
        customer_output,
        index=False,
    )

    print("\nBusiness segment summary:")
    print(
        named_summary[
            [
                "cluster_hierarchical",
                "segment_name",
                "customer_count",
                "customer_percentage",
                "median_purchase_frequency",
                "median_purchase_value",
                "median_activity_days",
                "average_silhouette",
            ]
        ]
        .round(2)
        .to_string(index=False)
    )

    print(
        f"\nSaved segment summary: "
        f"{summary_output}"
    )

    print(
        f"Saved customer segments: "
        f"{customer_output}"
    )

    print(
        "\nM2 Day 4 business segment naming completed."
    )


if __name__ == "__main__":
    main()