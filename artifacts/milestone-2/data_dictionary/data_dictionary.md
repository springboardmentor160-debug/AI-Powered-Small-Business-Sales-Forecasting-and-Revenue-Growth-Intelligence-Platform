# MarketMind AI — Milestone 2 Data Dictionary

## UCI Online Retail II

| Field | Description |
|---|---|
| Invoice | Transaction invoice number |
| StockCode | Product stock code |
| Description | Product description |
| Quantity | Number of units sold |
| InvoiceDate | Date and time of transaction |
| Price | Unit price |
| Customer ID | Customer identifier |
| Country | Customer country |
| _source_row_id | Stable source row identifier |
| _source_system | Original source system |
| _source_file | Original source filename |

## M5 Daily Demand

| Field | Description |
|---|---|
| date | Calendar date |
| d | M5 day identifier |
| id | M5 item/store series identifier |
| item_id | Product/item identifier |
| dept_id | Department identifier |
| cat_id | Category identifier |
| store_id | Store identifier |
| state_id | State identifier |
| units_sold | Units sold |
| sell_price | Selling price |
| event_name_1 | Primary calendar event |
| event_type_1 | Primary calendar event type |
| event_name_2 | Secondary calendar event |
| event_type_2 | Secondary calendar event type |
| _source_system | Original source system |
| _source_sales_file | M5 sales source filename |
| _source_calendar_file | M5 calendar source filename |
| _source_price_file | M5 pricing source filename |

## Data Quality

### UCI Online Retail II

- Rows: 1,067,371
- Columns: 11
- Status: PASS
- Unexpected missing values: 0
- Duplicate rows: 0

### M5 Daily Demand

- Rows: 1,913
- Columns: 26
- Status: PASS
- Unexpected missing values: 0
- Duplicate rows: 0

## Data Lineage

### UCI Online Retail II
→ Original CSV files
→ Source metadata
→ Data-quality validation
→ PostgreSQL

### M5 source files
→ Daily demand transformation
→ Source provenance
→ Data-quality validation
→ M5 forecasting artifacts
## Data Preservation

Original UCI and M5 source files are preserved.

Transformations are performed on working data and generated artifacts.
Source information is retained to support traceability and reproducibility.
