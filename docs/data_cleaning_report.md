# MarketMind AI: Data Cleaning Report

## Milestone 1, Day 5-6

This report records the actual output of `data_prep/clean_data.py` for the current raw sample datasets.

## Sales

| Check                      | Result                                                                                                                                                                                                                                    |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rows before cleaning       | 12,000                                                                                                                                                                                                                                    |
| Missing values found       | 0 in every column                                                                                                                                                                                                                         |
| Duplicate rows found       | 0                                                                                                                                                                                                                                         |
| Invalid values found       | 0 non-positive `quantity` or `unit_price`; 0 invalid/missing dates; 0 missing `customer_id`; 0 `total_amount` mismatches                                                                                                                  |
| Cleaning actions performed | Checked and removed missing `quantity` values, duplicate rows, invalid dates/prices, non-positive quantity or price, and missing `customer_id`; converted `date` to `YYYY-MM-DD`; verified `total_amount` against `quantity * unit_price` |
| Rows after cleaning        | 12,000                                                                                                                                                                                                                                    |
| Output                     | `data/processed/sales/cleaned_sales.csv`                                                                                                                                                                                                  |

## Inventory

| Check                      | Result                                                                                                                                                          |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rows before cleaning       | 96                                                                                                                                                              |
| Missing values found       | 0 in every column                                                                                                                                               |
| Duplicate rows found       | 0                                                                                                                                                               |
| Invalid values found       | 0 negative `stock_level` values; 0 missing `reorder_threshold` values                                                                                           |
| Cleaning actions performed | Checked and removed negative stock records and exact duplicates; checked `reorder_threshold` and used the documented default of 20 only when a value is missing |
| Rows after cleaning        | 96                                                                                                                                                              |
| Output                     | `data/processed/inventory/cleaned_inventory.csv`                                                                                                                |

## Customers

| Check                      | Result                                                                                                                                                                       |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rows before cleaning       | 300                                                                                                                                                                          |
| Missing values found       | 0 in every column                                                                                                                                                            |
| Duplicate rows found       | 0                                                                                                                                                                            |
| Invalid values found       | 0 missing or blank `customer_id` values; 0 duplicate email records                                                                                                           |
| Cleaning actions performed | Standardized email values by stripping whitespace and converting to lowercase; validated customer identifiers; checked and removed duplicate customer records based on email |
| Rows after cleaning        | 300                                                                                                                                                                          |
| Output                     | `data/processed/customers/cleaned_customers.csv`                                                                                                                             |

## Why raw and processed data are separate

The files under `data/raw/` are preserved as the original source inputs and are never overwritten by cleaning. The cleaned files are written under `data/processed/` so that the project can reproduce the preparation process, audit the original data, compare cleaning rules, and recover the source data if a future rule changes. This separation also keeps downstream analysis from accidentally modifying the raw datasets.
