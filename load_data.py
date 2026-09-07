import csv
from datetime import datetime
from decimal import Decimal

from database import SessionLocal
from models import Customer, Product, Inventory, SalesTransaction


DATA_DIR = "cleaned_data"


def load_customers(db):
    with open(f"{DATA_DIR}/customers.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            customer = Customer(
                customer_id=int(row["customer_id"]),
                country=row["country"]
            )
            db.add(customer)

    print("Customers loaded")


def load_products(db):
    with open(f"{DATA_DIR}/products.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            product = Product(
                product_id=row["product_id"],
                product_name=row["product_name"]
            )
            db.add(product)

    print("Products loaded")


def load_inventory(db):
    with open(f"{DATA_DIR}/inventory.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            inventory = Inventory(
                product_id=row["product_id"],
                current_stock=int(row["current_stock"]),
                reorder_threshold=int(row["reorder_threshold"])
            )
            db.add(inventory)

    print("Inventory loaded")


def load_sales_transactions(db):
    with open(
        f"{DATA_DIR}/sales_transactions.csv",
        "r",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            transaction = SalesTransaction(
                invoice_id=int(row["invoice_id"]),
                product_id=row["product_id"],
                customer_id=int(row["customer_id"]),
                quantity=int(row["quantity"]),
                unit_price=Decimal(row["unit_price"]),
                invoice_date=datetime.fromisoformat(row["invoice_date"]),
                sales_amount=Decimal(row["sales_amount"])
            )
            db.add(transaction)

    print("Sales transactions loaded")


def main():
    db = SessionLocal()

    try:
        load_sales_transactions(db)
        db.commit()

        print("\nSales transactions loaded successfully!")

    except Exception as e:
        db.rollback()
        print("\nError while loading sales transactions:")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    main()