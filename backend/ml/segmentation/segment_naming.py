import pandas as pd


def assign_business_segment_names(
    cluster_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Assign business-friendly names to hierarchical clusters.

    Naming is based on observed customer behavior:
        - purchase frequency
        - purchase value
        - recency/activity

    Cluster identifiers are not assumed to have business meaning.
    """

    required_columns = {
        "cluster_hierarchical",
        "average_purchase_frequency",
        "median_purchase_frequency",
        "average_purchase_value",
        "median_purchase_value",
        "average_activity_days",
        "median_activity_days",
    }

    missing = required_columns - set(
        cluster_summary.columns
    )

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    result = cluster_summary.copy()

    # ---------------------------------------------------------
    # Identify behavioral extremes.
    # ---------------------------------------------------------

    highest_frequency_cluster = result.loc[
        result["median_purchase_frequency"].idxmax(),
        "cluster_hierarchical",
    ]

    highest_value_cluster = result.loc[
        result["median_purchase_value"].idxmax(),
        "cluster_hierarchical",
    ]

    remaining = result[
        ~result["cluster_hierarchical"].isin(
            [
                highest_frequency_cluster,
                highest_value_cluster,
            ]
        )
    ].copy()

    # ---------------------------------------------------------
    # Among the remaining groups, identify the more active
    # customer population.
    # ---------------------------------------------------------

    active_cluster = remaining.loc[
        remaining["median_activity_days"].idxmin(),
        "cluster_hierarchical",
    ]

    # ---------------------------------------------------------
    # Assign business names.
    # ---------------------------------------------------------

    def name_cluster(cluster_id):

        if cluster_id == highest_frequency_cluster:
            return "High-Frequency Loyal Customers"

        if cluster_id == highest_value_cluster:
            return "Premium High-Value Customers"

        if cluster_id == active_cluster:
            return "Active Regular Customers"

        return "Occasional / Low-Engagement Customers"

    result["segment_name"] = (
        result["cluster_hierarchical"]
        .apply(name_cluster)
    )

    return result


def attach_segment_names(
    customer_df: pd.DataFrame,
    named_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Attach the business segment name to each customer.
    """

    mapping = named_summary[
        [
            "cluster_hierarchical",
            "segment_name",
        ]
    ]

    result = customer_df.merge(
        mapping,
        on="cluster_hierarchical",
        how="left",
    )

    return result