import pandas as pd
from sqlalchemy import text

from database import engine


# --------------------------------------------------
# Load Country Data
# --------------------------------------------------

file_path = "../data/processed/cleaned_sales.csv"

df = pd.read_csv(
    file_path,
    usecols=["Country"],
    low_memory=False
)

print("Country records loaded:", len(df))


# --------------------------------------------------
# Add Country Column
# --------------------------------------------------

with engine.begin() as connection:

    columns = connection.execute(
        text("PRAGMA table_info(sales)")
    ).fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    if "country" not in column_names:

        print("Adding country column...")

        connection.execute(
            text(
                "ALTER TABLE sales "
                "ADD COLUMN country VARCHAR"
            )
        )

        print("Country column added.")

    else:
        print("Country column already exists.")


# --------------------------------------------------
# Update Country Values
# --------------------------------------------------

print("Updating country values...")

with engine.begin() as connection:

    batch_size = 10000

    for start in range(0, len(df), batch_size):

        end = min(
            start + batch_size,
            len(df)
        )

        batch = df.iloc[start:end]

        for offset, country in enumerate(
            batch["Country"],
            start=start + 1
        ):

            connection.execute(
                text("""
                    UPDATE sales
                    SET country = :country
                    WHERE id = :sale_id
                """),
                {
                    "country": str(country),
                    "sale_id": offset
                }
            )

        print(
            f"Updated countries: "
            f"{end}/{len(df)}"
        )


print("\n===================================")
print("COUNTRY UPDATE COMPLETE")
print("===================================")