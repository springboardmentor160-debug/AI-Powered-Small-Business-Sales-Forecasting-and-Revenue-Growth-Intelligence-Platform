"""Business summary queries for the initial MarketMind backend."""

from typing import Any

from .database import get_connection


def get_sales_summary() -> dict[str, Any]:
    """Return basic sales totals and the product with the most units sold."""
    with get_connection() as connection:
        totals = connection.execute(
            """
            SELECT
                COALESCE(SUM(total_amount), 0) AS total_revenue,
                COUNT(*) AS total_transactions,
                COALESCE(SUM(quantity), 0) AS total_quantity_sold
            FROM sales_transactions
            """
        ).fetchone()
        top_product = connection.execute(
            """
            SELECT product_id, product_name, SUM(quantity) AS quantity_sold
            FROM sales_transactions
            GROUP BY product_id, product_name
            ORDER BY quantity_sold DESC, product_id ASC
            LIMIT 1
            """
        ).fetchone()

    return {
        "total_revenue": round(float(totals["total_revenue"]), 2),
        "total_transactions": int(totals["total_transactions"]),
        "total_quantity_sold": int(totals["total_quantity_sold"]),
        "top_selling_product": {
            "product_id": top_product["product_id"],
            "product_name": top_product["product_name"],
            "quantity_sold": int(top_product["quantity_sold"]),
        },
    }


def get_inventory_summary() -> dict[str, int]:
    """Return product count, stock total, and products needing replenishment."""
    with get_connection() as connection:
        summary = connection.execute(
            """
            SELECT
                COUNT(DISTINCT product_id) AS total_products,
                COALESCE(SUM(stock_level), 0) AS total_stock,
                COUNT(DISTINCT CASE
                    WHEN stock_level <= reorder_threshold THEN product_id
                END) AS products_at_or_below_reorder_threshold
            FROM inventory
            """
        ).fetchone()

    return {
        "total_products": int(summary["total_products"]),
        "total_stock": int(summary["total_stock"]),
        "products_at_or_below_reorder_threshold": int(
            summary["products_at_or_below_reorder_threshold"]
        ),
    }


def get_customer_summary() -> dict[str, Any]:
    """Return customer count and basic demographic statistics."""
    with get_connection() as connection:
        summary = connection.execute(
            """
            SELECT
                COUNT(*) AS total_customers,
                ROUND(AVG(age), 2) AS average_age,
                MIN(age) AS minimum_age,
                MAX(age) AS maximum_age,
                COUNT(DISTINCT city) AS unique_cities
            FROM customers
            """
        ).fetchone()

    return {
        "total_customers": int(summary["total_customers"]),
        "basic_statistics": {
            "average_age": float(summary["average_age"]),
            "minimum_age": int(summary["minimum_age"]),
            "maximum_age": int(summary["maximum_age"]),
            "unique_cities": int(summary["unique_cities"]),
        },
    }
