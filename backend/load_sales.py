import pandas as pd
from sqlalchemy.orm import Session

from database import engine
from models import Sale, Product, Customer


# --------------------------------------------------
# Load cleaned CSV
# --------------------------------------------------

file_path = "../data/processed/cleaned_sales.csv"

df = pd.read_csv(
    file_path,
    low_memory=False
)

print("Cleaned data loaded:", df.shape)

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])


session = Session(engine)


try:

    # ==================================================
    # 1. CREATE PRODUCTS
    # ==================================================

    print("\nLoading products...")

    products = (
        df[
            ["StockCode", "Description", "UnitPrice"]
        ]
        .drop_duplicates(subset=["StockCode"])
    )

    print("Unique products found:", len(products))

    product_map = {}

    for _, row in products.iterrows():

        product = Product(
            stock_code=str(row["StockCode"]),
            name=str(row["Description"]),
            category=None,
            unit_price=float(row["UnitPrice"])
        )

        session.add(product)
        session.flush()

        product_map[row["StockCode"]] = product.id

    print("Products inserted:", len(product_map))


    # ==================================================
    # 2. CREATE CUSTOMERS
    # ==================================================

    print("\nLoading customers...")

    customers = (
        df[
            ["CustomerID"]
        ]
        .dropna()
        .drop_duplicates(subset=["CustomerID"])
    )

    print("Unique customers found:", len(customers))

    customer_map = {}

    for _, row in customers.iterrows():

        customer_id = int(row["CustomerID"])

        customer = Customer(
            customer_id=customer_id,
            name=f"Customer {customer_id}",
            contact_info=None
        )

        session.add(customer)
        session.flush()

        customer_map[customer_id] = customer.id

    print("Customers inserted:", len(customer_map))


    # ==================================================
    # 3. CREATE SALES
    # ==================================================

    print("\nLoading sales...")

    sales_count = 0

    for _, row in df.iterrows():

        stock_code = row["StockCode"]

        product_id = product_map.get(stock_code)

        customer_id = None

        if pd.notna(row["CustomerID"]):
            customer_id = customer_map.get(
                int(row["CustomerID"])
            )

        sale = Sale(
            product_id=product_id,
            customer_id=customer_id,
            quantity=int(row["Quantity"]),
            sale_date=row["InvoiceDate"].date()
        )

        session.add(sale)

        sales_count += 1

        # Commit every 10,000 records
        if sales_count % 10000 == 0:

            session.commit()

            print(
                f"Sales inserted: {sales_count}/{len(df)}"
            )


    # Final commit
    session.commit()

    print("\n===================================")
    print("DATABASE LOADING COMPLETE")
    print("===================================")
    print("Products:", len(product_map))
    print("Customers:", len(customer_map))
    print("Sales:", sales_count)


except Exception as e:

    session.rollback()

    print("\nERROR:", e)


finally:

    session.close()