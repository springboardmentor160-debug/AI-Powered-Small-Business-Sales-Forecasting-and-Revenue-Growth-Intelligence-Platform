MARKETMIND AI

DATA PREPARATION DOCUMENTATION

1. PURPOSE

The purpose of the data preparation process is to clean, validate, standardize, and organize the collected business datasets so that they can be reliably used by the analytics, dashboard, and AI/ML components of MarketMind AI.

The preparation process focuses on identifying data quality issues, correcting or handling invalid records where appropriate, preserving legitimate business values, validating relationships between datasets, and producing consistent analytical datasets.

2. DATA SOURCES

The project uses the following datasets:

1. Customers
2. Geolocation
3. Order Items
4. Order Payments
5. Order Reviews
6. Orders
7. Product Category Translation
8. Products
9. Retail Store Inventory
10. Sellers

The original datasets are stored in:

data/raw/

The cleaned datasets are stored in:

data/processed/

The derived analytical datasets are stored in:

data/analytical/

3. DATA CLEANING AND PREPROCESSING

The datasets were inspected and processed to identify common data quality issues, including:

Missing values

Duplicate records

Invalid data types

Invalid dates

Invalid numeric values

Invalid categorical values

Primary key issues

Foreign key and relationship issues

Business rule violations

Unusual transaction and payment records

4. CUSTOMER DATA PREPARATION

The customer dataset was inspected for missing values, duplicate records, key integrity, data types, and relationships with order and geographic data.

Customer records were cleaned and standardized for use in customer analytics, segmentation, and churn prediction.

The resulting dataset is stored as:

data/processed/customers_clean.csv

5. TRANSACTION DATA PREPARATION

The order, order item, payment, and review datasets were processed and validated.

The following areas were checked:

Order identifiers

Customer relationships

Product relationships

Seller relationships

Order dates

Transaction quantities

Prices

Freight values

Payment values

Payment methods

Review scores

The transaction datasets were cleaned while preserving legitimate business values.

6. INVENTORY DATA PREPARATION

The retail inventory dataset was processed to ensure that inventory and sales-related fields were in a consistent and usable format.

The following fields and business conditions were checked:

Inventory levels

Units sold

Units ordered

Demand forecasts

Prices

Discounts

Competitor pricing

Seasonality

Weather conditions

Holiday and promotion information

Negative inventory, sales, price, and discount values were investigated and invalid values were not retained.

7. PRODUCT DATA PREPARATION

Product records were checked for duplicates, data types, product attributes, dimensions, and category information.

Missing English product categories were handled by assigning the value "Unknown" where an English category was unavailable.

The resulting dataset contains no missing category values.

8. DATA RELATIONSHIP VALIDATION

Relationships between related datasets were checked to ensure referential consistency.

The following relationships were validated:

Orders → Customers

Order Items → Orders

Order Payments → Orders

Order Reviews → Orders

Order Items → Products

Order Items → Sellers

Customers → Geolocation

Sellers → Geolocation

Products → Category Translation

Legitimate or unresolved geographic and category relationships were investigated rather than automatically treating every unmatched record as an error.

9. BUSINESS LOGIC VALIDATION

Business rules were checked after cleaning.

The validation included:

Order and delivery date relationships

Order item prices

Freight values

Payment values

Review scores

Product dimensions

Inventory quantities

Units sold

Prices and discounts

Demand forecast values

Analytical calculations

Values that were negative but represented valid business conditions were preserved.

10. HANDLING OF LEGITIMATE NEGATIVE VALUES

Not every negative value was treated as an error.

For example:

Negative delivery_delay_days indicates that an order was delivered earlier than estimated.

Negative forecast_error indicates that actual demand was lower than the forecast.

Negative price_difference_competitor indicates that the business price was lower than the competitor price.

These values were therefore preserved because they provide meaningful business information.

11. ANALYTICAL DATA PREPARATION

After cleaning and validation, analytical datasets were created for the major business areas.

The following analytical datasets were produced:

sales_analytics.csv

customer_analytics.csv

product_analytics.csv

inventory_analytics.csv

These datasets are stored in:

data/analytical/

12. ANALYTICAL DATA VALIDATION

The analytical datasets were validated for duplicate records and unusual or invalid analytical values.

Duplicate records found:

Sales Analytics: 0

Customer Analytics: 0

Product Analytics: 0

Inventory Analytics: 0

Certain missing analytical values were intentionally retained when they represented meaningful conditions.

For example, inventory_to_demand_ratio remains missing when Demand Forecast is zero because division by zero does not produce a meaningful ratio.

Delivery-related fields remain missing for orders where delivery information was unavailable instead of being incorrectly filled with artificial values.

13. PAYMENT DATA VALIDATION

Payment-related data quality checks were completed during the preparation process.

The checks identified:

Invalid installment records: 2

Zero-payment records: 9

Negative payment values: 0

The identified payment anomalies were investigated as part of the validation process.

14. FINAL OUTPUT

The final prepared data is organized into three layers:

Raw Data

Original source datasets stored in:

data/raw/

Processed Data

Cleaned and standardized datasets stored in:

data/processed/

Analytical Data

Business-ready analytical datasets stored in:

data/analytical/

15. DATA PREPARATION RESULT

The data preparation process has produced clean, structured, and validated datasets suitable for use by the remaining MarketMind AI platform components.

The prepared data can now be used for:

Sales analytics

Inventory analytics

Customer analytics

Product analytics

Customer segmentation

Sales forecasting

Churn prediction

Product recommendation

Anomaly detection

Dashboard development

Reporting

16. CONCLUSION

The data preparation stage transformed the collected datasets into structured and validated data suitable for the MarketMind AI platform.

Data quality issues were investigated systematically, legitimate business values were preserved, invalid values were handled appropriately, dataset relationships were validated, and analytical datasets were created for downstream business intelligence and AI/ML processing.

The prepared datasets are now ready to support the initial application build and subsequent machine learning stages of MarketMind AI.
