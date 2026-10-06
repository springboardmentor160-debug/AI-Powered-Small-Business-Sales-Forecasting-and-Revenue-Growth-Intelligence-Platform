"""Apriori association-rule mining for actual MarketMind transaction baskets."""

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules


RULE_COLUMNS = [
    "antecedents",
    "consequents",
    "support",
    "confidence",
    "lift",
]


def build_transaction_product_matrix(sales: pd.DataFrame) -> pd.DataFrame:
    """Create one binary product basket row for each actual transaction_id."""
    required_columns = {"transaction_id", "product_name"}
    missing_columns = required_columns.difference(sales.columns)
    if missing_columns:
        raise ValueError(f"Sales data is missing required columns: {sorted(missing_columns)}")

    basket_data = sales[["transaction_id", "product_name"]].dropna().drop_duplicates()
    basket = pd.crosstab(basket_data["transaction_id"], basket_data["product_name"])
    return basket.gt(0).astype(int).sort_index().sort_index(axis=1)


def _format_itemset(itemset: Iterable[str]) -> str:
    return " + ".join(sorted(str(item) for item in itemset))


@dataclass
class AssociationRuleMiner:
    """Run deterministic Apriori and expose explainable rule-based suggestions."""

    min_support: float = 0.01
    min_confidence: float = 0.1

    def fit(self, transaction_product_matrix: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return frequent itemsets and readable association rules."""
        if transaction_product_matrix.empty:
            return self._empty_itemsets(), self._empty_rules()

        frequent_itemsets = apriori(
            transaction_product_matrix.astype(bool),
            min_support=self.min_support,
            use_colnames=True,
        )
        if frequent_itemsets.empty:
            return self._empty_itemsets(), self._empty_rules()

        itemsets = frequent_itemsets.copy()
        itemsets["itemsets"] = itemsets["itemsets"].map(_format_itemset)
        itemsets = itemsets[["itemsets", "support"]].sort_values(
            ["support", "itemsets"], ascending=[False, True]
        ).reset_index(drop=True)

        has_pair_itemset = frequent_itemsets["itemsets"].map(len).ge(2).any()
        if not has_pair_itemset:
            return itemsets, self._empty_rules()

        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=self.min_confidence,
        )
        if rules.empty:
            return itemsets, self._empty_rules()

        rules = rules[rules["lift"] > 1].copy()
        if rules.empty:
            return itemsets, self._empty_rules()
        rules["antecedents"] = rules["antecedents"].map(_format_itemset)
        rules["consequents"] = rules["consequents"].map(_format_itemset)
        rules = rules[RULE_COLUMNS].sort_values(
            ["lift", "confidence", "support", "antecedents", "consequents"],
            ascending=[False, False, False, True, True],
        ).reset_index(drop=True)
        return itemsets, rules.round({"support": 6, "confidence": 6, "lift": 6})

    def cross_sell(
        self,
        purchased_products: Iterable[str],
        rules: pd.DataFrame,
        top_n: int = 3,
    ) -> list[dict[str, float | int | str]]:
        """Return rule-based products not already in a customer's purchase set."""
        if top_n < 1 or rules.empty:
            return []
        purchased = {str(product) for product in purchased_products}
        matches = []
        for _, rule in rules.iterrows():
            antecedents = set(str(rule["antecedents"]).split(" + "))
            consequents = set(str(rule["consequents"]).split(" + "))
            if antecedents.issubset(purchased) and not consequents.intersection(purchased):
                for product in sorted(consequents):
                    matches.append(
                        {
                            "recommended_product": product,
                            "antecedents": rule["antecedents"],
                            "support": float(rule["support"]),
                            "confidence": float(rule["confidence"]),
                            "lift": float(rule["lift"]),
                        }
                    )
        return matches[:top_n]

    @staticmethod
    def _empty_itemsets() -> pd.DataFrame:
        return pd.DataFrame(columns=["itemsets", "support"])

    @staticmethod
    def _empty_rules() -> pd.DataFrame:
        return pd.DataFrame(columns=RULE_COLUMNS)
