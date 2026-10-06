# UCI Online Retail II — Raw Dataset

MarketMindAI uses the UCI Online Retail II dataset as the primary
source for customer, transaction, product, invoice, and revenue
intelligence.

## Official source

UCI Machine Learning Repository — Online Retail II

https://archive.ics.uci.edu/dataset/502/online%2Bretail%2Bii

Dataset DOI:

https://doi.org/10.24432/C5CG6D

Dataset creator:

Daqing Chen

License:

Creative Commons Attribution 4.0 International (CC BY 4.0)

## Dataset overview

Online Retail II is a real two-year online retail transaction dataset
from a UK-based, registered, non-store online retailer.

The source covers transactions from:

01/12/2009 to 09/12/2011

The UCI repository reports:

- 1,067,371 instances
- Sequential and time-series characteristics
- Business-domain data
- Missing values
- Supported tasks including clustering and regression

## Raw files used by MarketMindAI

The original source has been preserved as two files:

- online_retail_v1.csv
- online_retail_v2.csv

These files represent the two source periods used by the project.

The raw files are treated as immutable source data.

## Source columns

The original UCI dataset defines the following business fields:

| Source field | MarketMindAI file field | Description |
|---|---|---|
| InvoiceNo | Invoice | Unique invoice/transaction identifier |
| StockCode | StockCode | Product/item code |
| Description | Description | Product/item description |
| Quantity | Quantity | Quantity of the product in the transaction |
| InvoiceDate | InvoiceDate | Transaction date and time |
| UnitPrice | Price | Product price per unit in sterling |
| CustomerID | Customer ID | Customer identifier |
| Country | Country | Customer country |

## Cancellation information

According to the UCI documentation, an invoice number beginning
with the letter `C` indicates a cancellation.

MarketMindAI therefore performs transaction-level and invoice-level
reconciliation in downstream analytical pipelines.

Cancellation and reversal information is NOT deleted from the raw
source files.

## How MarketMindAI uses UCI data

### Customer segmentation

UCI is used to create customer-level behavioral features:

- purchase frequency
- purchase value
- customer activity

These features are used by the M2 customer segmentation pipeline.

The project evaluates:

- K-Means clustering
- Hierarchical clustering
- Silhouette Score

### Revenue forecasting

UCI transactions are also transformed into a daily revenue time
series.

The forecasting pipeline uses:

- transaction reconciliation
- completed-sales analytical views
- daily revenue aggregation
- time-series validation
- Prophet forecasting

### Business intelligence

UCI data also supports:

- sales analytics
- customer analytics
- product intelligence
- invoice-related analysis
- derived inventory intelligence

## Data governance

The raw source files must not be overwritten or modified by analytical
code.

Processing is performed on derived DataFrames and/or generated
datasets.

The intended flow is:

Raw UCI data
    ↓
Validation
    ↓
Reconciliation
    ↓
Transformation
    ↓
Processed analytical data
    ↓
ML / Analytics
    ↓
Business outputs

## Important data limitation

The UCI Online Retail II source does not contain actual historical
physical inventory stock levels.

MarketMindAI therefore treats inventory quantities derived from sales
as estimated/calculated intelligence rather than observed historical
stock levels.

## Reproducibility

The raw UCI files are stored locally in this directory.

Application code should reference them through the UCI data-pipeline
loader rather than hard-coding file paths throughout the application.

## Citation

Chen, D. (2012). Online Retail II [Dataset].
UCI Machine Learning Repository.

https://doi.org/10.24432/C5CG6D