"""Customer-based collaborative filtering for MarketMind recommendations."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


REQUIRED_SALES_COLUMNS = {"customer_id", "product_name", "quantity"}


def build_customer_product_matrix(
    sales: pd.DataFrame,
    customer_ids: pd.Index | list[str] | None = None,
) -> pd.DataFrame:
    """Build customer rows and product columns from summed purchase quantities."""
    missing_columns = REQUIRED_SALES_COLUMNS.difference(sales.columns)
    if missing_columns:
        raise ValueError(f"Sales data is missing required columns: {sorted(missing_columns)}")

    purchase_data = sales[["customer_id", "product_name", "quantity"]].copy()
    purchase_data = purchase_data.dropna(subset=["customer_id", "product_name"])
    purchase_data["quantity"] = pd.to_numeric(purchase_data["quantity"], errors="coerce").fillna(0)
    matrix = purchase_data.pivot_table(
        index="customer_id",
        columns="product_name",
        values="quantity",
        aggfunc="sum",
        fill_value=0,
    )
    if customer_ids is not None:
        matrix = matrix.reindex(index=pd.Index(customer_ids, name="customer_id"), fill_value=0)
    return matrix.sort_index().sort_index(axis=1).astype(float)


@dataclass
class CollaborativeFilteringModel:
    """Customer-based collaborative filtering using cosine similarity."""

    matrix: pd.DataFrame
    similarity: pd.DataFrame

    @classmethod
    def fit(cls, customer_product_matrix: pd.DataFrame) -> "CollaborativeFilteringModel":
        """Fit the cosine-similarity model from a customer-product matrix."""
        if customer_product_matrix.empty:
            raise ValueError("At least one customer-product purchase is required.")
        similarity_values = cosine_similarity(customer_product_matrix.to_numpy())
        similarity = pd.DataFrame(
            similarity_values,
            index=customer_product_matrix.index,
            columns=customer_product_matrix.index,
        )
        return cls(matrix=customer_product_matrix, similarity=similarity)

    def similar_customers(self, customer_id: str, top_n: int = 5) -> list[dict[str, float | str]]:
        """Return the closest other customers by cosine similarity."""
        self._validate_customer(customer_id)
        if top_n < 1:
            return []

        scores = self.similarity.loc[customer_id].drop(index=customer_id)
        scores = scores.sort_values(ascending=False, kind="mergesort").head(top_n)
        return [
            {"customer_id": str(similar_id), "similarity": round(float(score), 6)}
            for similar_id, score in scores.items()
        ]

    def recommend_products(self, customer_id: str, top_n: int = 3) -> list[dict[str, float | int | str]]:
        """Recommend unpurchased products weighted by similar-customer behavior."""
        self._validate_customer(customer_id)
        if top_n < 1:
            return []

        target_purchases = self.matrix.loc[customer_id]
        if float(target_purchases.sum()) <= 0:
            return []

        neighbors = self.similar_customers(customer_id, top_n=len(self.matrix.index) - 1)
        if not neighbors:
            return []

        candidate_scores: dict[str, float] = {}
        supporting_customers: dict[str, set[str]] = {}
        for neighbor in neighbors:
            neighbor_id = neighbor["customer_id"]
            similarity = float(neighbor["similarity"])
            if similarity <= 0:
                continue
            neighbor_products = self.matrix.loc[neighbor_id]
            for product_name, quantity in neighbor_products[neighbor_products > 0].items():
                if target_purchases[product_name] > 0:
                    continue
                candidate_scores[product_name] = candidate_scores.get(product_name, 0.0) + similarity * float(quantity)
                supporting_customers.setdefault(product_name, set()).add(neighbor_id)

        ranked_products = sorted(
            candidate_scores.items(),
            key=lambda item: (-item[1], item[0]),
        )[:top_n]
        return [
            {
                "recommended_product": product_name,
                "recommendation_score": round(score, 6),
                "supporting_customer_count": len(supporting_customers[product_name]),
                "rank": rank,
            }
            for rank, (product_name, score) in enumerate(ranked_products, start=1)
        ]

    def _validate_customer(self, customer_id: str) -> None:
        if customer_id not in self.matrix.index:
            raise KeyError(f"Unknown customer_id: {customer_id}")
