# MarketMind AI — Data Dictionary

This document describes the attributes contained in the raw and processed retail datasets for **MarketMind AI**.

| Column Name | Data Type | Constraint / Format | Description | Sample Value |
| :--- | :--- | :--- | :--- | :--- |
| `transaction_id` | String | Unique Identifier (Primary Key) | Unique alphanumeric code assigned to each retail sales transaction. | `TXN-10005` |
| `date` | Timestamp | ISO 8601 `YYYY-MM-DD HH:MM:SS` | Timestamp indicating when the sale was recorded at POS. Raw dates are cleaned into standard ISO format. | `2024-02-15 14:30:00` |
| `product_id` | String | Foreign Key | Unique product identifier code linking to the catalog. | `P101` |
| `product_name` | String | Non-null String | Descriptive title/name of the item sold. | `Wireless Noise-Canceling Headphones` |
| `category` | String | Standardized Enum | Product category (e.g., Electronics, Home & Kitchen, Clothing, Groceries, Books, Beauty & Care). | `Electronics` |
| `quantity` | Integer | Positive integer (> 0) | Number of units purchased in the transaction. | `2` |
| `unit_price` | Float / Numeric | Currency (USD `$`), > 0 | Price per unit of the item sold. | `129.99` |
| `total_amount` | Float / Numeric | Currency (USD `$`), `quantity * unit_price` | Total monetary value of the line item transaction. | `259.98` |
| `store_id` | String | Foreign Key | Unique identifier of the retail branch or store location where the transaction occurred. | `STORE-001` |
| `customer_id` | String | Optional / Nullable Foreign Key | Unique customer ID for registered patrons. Nullable for anonymous guest checkout. Cleaned to `GUEST` if missing. | `CUST-1004` |
| `payment_method` | String | Standardized Enum | Payment channel used (Credit Card, Cash, UPI / Mobile, Debit Card). Cleaned to `Unknown` if missing. | `Credit Card` |
| `stock_level` | Integer | Integer (>= 0) | Current available quantity of the product remaining in the store inventory after transaction. | `8` |
| `reorder_threshold`| Integer | Integer (> 0) | Minimum stock threshold. When `stock_level <= reorder_threshold`, an automated reorder alert is triggered. | `12` |

---

### Data Cleaning Rules & Transformation Policies

1. **Date Formatting**: All variations (`YYYY/MM/DD`, `DD-MM-YYYY`, missing timestamps) are parsed into standardized `YYYY-MM-DD HH:MM:SS` format.
2. **Category Normalization**: Mixed casing (e.g. `electronics` vs `Electronics`, `Apparel & Accessories` vs `Clothing`) is mapped into standardized core categories.
3. **Missing Value Handling**:
   - `customer_id` -> Replaced with `"GUEST"` if unrecorded.
   - `payment_method` -> Standardized into capitalized titles (`Credit Card`, `Cash`, `UPI`, `Debit Card`) or `"Unknown"`.
4. **Calculated Field Integrity**: `total_amount` is recalculated as `quantity * unit_price` if inconsistent.
5. **Deduplication**: Duplicate rows matching `transaction_id`, `date`, `product_id`, and `store_id` are purged.
