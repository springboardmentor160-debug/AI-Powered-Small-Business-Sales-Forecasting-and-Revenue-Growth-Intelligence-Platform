# MarketMind AI — Milestone 2 Data Lineage

## UCI Online Retail II

UCI Online Retail II
→ online_retail_v1.csv
→ online_retail_v2.csv
→ Source row identification
→ Data-quality validation
→ PostgreSQL sales persistence
→ Sales analytics

## M5

M5 source datasets
→ sales_train_validation.csv
→ calendar.csv
→ sell_prices.csv
→ Daily demand transformation
→ Provenance metadata
→ Data-quality validation
→ M5 forecasting features
→ Forecasting artifacts

## Source Provenance

### UCI

- Source system: UCI
- Source files:
  - online_retail_v1.csv
  - online_retail_v2.csv
- Row-level identifier: _source_row_id
- Source identifier: _source_system
- Source filename: _source_file

### M5

- Source system: M5
- Sales source: sales_train_validation.csv
- Calendar source: calendar.csv
- Pricing source: sell_prices.csv
- Sales provenance: _source_sales_file
- Calendar provenance: _source_calendar_file
- Pricing provenance: _source_price_file

## Data Quality

UCI Online Retail II:
- 1,067,371 rows
- Status: PASS

M5 Daily Demand:
- 1,913 rows
- Status: PASS

## Preservation

Original source files are preserved.

Transformations create separate working data and artifacts rather than
modifying the original source datasets.