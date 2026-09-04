import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine
from models import Product, Sale, Inventory


# --------------------------------------------------
# Initialize Inventory
# --------------------------------------------------

session = Session(engine)

try:
    print("Initializing inventory...")

    # Check whether inventory already contains records
    existing_count = session.query(
        func.count(Inventory.id)
    ).scalar()

    if existing_count > 0:
        print(
            f"Inventory already contains "
            f"{existing_count} records."
        )
        print("No changes made.")

    else:
        products = session.query(Product).all()

        print("Products found:", len(products))

        inventory_count = 0

        for product in products:

            # Calculate total quantity sold
            total_sold = session.query(
                func.sum(Sale.quantity)
            ).filter(
                Sale.product_id == product.id
            ).scalar()

            total_sold = total_sold or 0

            # Create a simple initial stock estimate.
            # This is a starting point because the dataset
            # does not contain actual historical stock levels.
            stock_level = max(
                int(total_sold * 0.10),
                10
            )

            # Reorder when stock falls below 20% of
            # the estimated initial stock.
            reorder_point = max(
                int(stock_level * 0.20),
                5
            )

            inventory = Inventory(
                product_id=product.id,
                stock_level=stock_level,
                reorder_point=reorder_point
            )

            session.add(inventory)
            inventory_count += 1

            if inventory_count % 500 == 0:
                session.commit()
                print(
                    f"Inventory records created: "
                    f"{inventory_count}/{len(products)}"
                )

        session.commit()

        print("\n===================================")
        print("INVENTORY INITIALIZATION COMPLETE")
        print("===================================")
        print("Inventory records:", inventory_count)

except Exception as e:
    session.rollback()
    print("\nERROR:", e)

finally:
    session.close()