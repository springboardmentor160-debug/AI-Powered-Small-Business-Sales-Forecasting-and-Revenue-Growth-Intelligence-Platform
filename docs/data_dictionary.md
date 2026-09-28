# MarketMind AI: Data Dictionary

## Milestone 1, Day 1-2

This dictionary documents the fields currently present in the raw MarketMind AI sample datasets. Data types are the pandas types observed when the CSV files are loaded. All fields are required in the current generated datasets, which contain no missing values.

The files are raw inputs for exploration and future preparation. The later uses below describe planned MarketMind AI capabilities; they do not indicate that those capabilities are implemented at this stage.

## 1. Sales

Source: `data/raw/sales/sales.csv`

| Field name       | Data type | Description                                                                           | Example value | Required | Later MarketMind AI use                                                                            |
| ---------------- | --------- | ------------------------------------------------------------------------------------- | ------------- | -------- | -------------------------------------------------------------------------------------------------- |
| `transaction_id` | `object`  | Unique identifier for a sales transaction record.                                     | `T000001`     | Yes      | Identify individual sales records and prevent double-counting in revenue and forecasting datasets. |
| `date`           | `object`  | Calendar date on which the sale occurred, stored as `YYYY-MM-DD` text in the raw CSV. | `2023-10-16`  | Yes      | Build time series for sales trends, seasonality analysis, and future forecasting.                  |
| `product_id`     | `object`  | Identifier of the product sold.                                                       | `P001`        | Yes      | Join sales to inventory and product-level revenue, demand, and recommendation analysis.            |
| `product_name`   | `object`  | Human-readable name of the product sold.                                              | `Notebook`    | Yes      | Display product information and support product-level sales interpretation.                        |
| `category`       | `object`  | Business category assigned to the product.                                            | `Stationery`  | Yes      | Compare category performance and support later segmentation and recommendation features.           |
| `quantity`       | `int64`   | Number of units sold in the transaction record.                                       | `1`           | Yes      | Measure demand, calculate total units sold, and create forecasting signals.                        |
| `unit_price`     | `float64` | Price of one unit at the time of the sale.                                            | `8.73`        | Yes      | Analyze price and revenue behavior and support future revenue-growth analysis.                     |
| `total_amount`   | `float64` | Total monetary value of the record, equal to `quantity * unit_price`.                 | `8.73`        | Yes      | Calculate revenue totals, trends, customer value, and future forecasting targets.                  |
| `store_id`       | `object`  | Identifier of the store where the sale occurred.                                      | `S004`        | Yes      | Compare store performance and support store-level sales forecasting.                               |
| `customer_id`    | `object`  | Identifier of the customer associated with the sale.                                  | `C0208`       | Yes      | Link transactions to customer history for segmentation, recommendations, and churn analysis.       |
| `payment_method` | `object`  | Payment method used for the transaction.                                              | `Card`        | Yes      | Describe purchasing behavior and support later sales intelligence analysis.                        |

## 2. Inventory

Source: `data/raw/inventory/inventory.csv`

| Field name          | Data type | Description                                                   | Example value | Required | Later MarketMind AI use                                                                   |
| ------------------- | --------- | ------------------------------------------------------------- | ------------- | -------- | ----------------------------------------------------------------------------------------- |
| `product_id`        | `object`  | Identifier of the product whose stock is recorded.            | `P001`        | Yes      | Join inventory to sales and analyze product availability against demand.                  |
| `product_name`      | `object`  | Human-readable name of the inventoried product.               | `Notebook`    | Yes      | Display product stock information and support inventory interpretation.                   |
| `category`          | `object`  | Business category assigned to the product.                    | `Stationery`  | Yes      | Compare stock position and demand across product categories.                              |
| `stock_level`       | `int64`   | Current stock quantity recorded for the product at a store.   | `38`          | Yes      | Assess availability and provide inputs for future inventory and revenue-growth decisions. |
| `reorder_threshold` | `int64`   | Stock level at which replenishment may need to be considered. | `23`          | Yes      | Identify products approaching replenishment and support future recommendations.           |
| `store_id`          | `object`  | Identifier of the store holding the stock.                    | `S001`        | Yes      | Compare inventory by store and connect availability with store-level sales.               |

## 3. Customers

Source: `data/raw/customers/customers.csv`

| Field name          | Data type | Description                                                                    | Example value              | Required | Later MarketMind AI use                                                            |
| ------------------- | --------- | ------------------------------------------------------------------------------ | -------------------------- | -------- | ---------------------------------------------------------------------------------- |
| `customer_id`       | `object`  | Stable identifier for a customer.                                              | `C0001`                    | Yes      | Join customer profiles to sales and create customer-level intelligence features.   |
| `name`              | `object`  | Customer's display name.                                                       | `Diya Singh`               | Yes      | Identify and display customer records in later business workflows.                 |
| `email`             | `object`  | Customer email address.                                                        | `customer0001@example.com` | Yes      | Maintain a customer contact attribute for future approved communication workflows. |
| `gender`            | `object`  | Gender value recorded for the customer.                                        | `Male`                     | Yes      | Support descriptive customer segmentation where appropriate and permitted.         |
| `age`               | `int64`   | Customer age in years.                                                         | `59`                       | Yes      | Support descriptive customer segmentation and analysis of purchasing patterns.     |
| `city`              | `object`  | City associated with the customer.                                             | `Hyderabad`                | Yes      | Analyze geographic patterns and support location-aware sales intelligence.         |
| `registration_date` | `object`  | Date when the customer registered, stored as `YYYY-MM-DD` text in the raw CSV. | `2024-05-06`               | Yes      | Establish customer tenure and support later churn and lifecycle analysis.          |

## Notes on the raw datasets

- The dictionary includes only fields present in the three current CSV files.
- Dates are currently stored as raw text and may be typed explicitly during a later preparation stage.
- `total_amount` is generated as `quantity * unit_price` in the sample sales data.
- The current sample files contain no missing values, but missingness and quality rules should be reassessed when real source data is introduced.
