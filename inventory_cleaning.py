import pandas as pd

df = pd.read_csv("data/Grocery_Inventory_and_Sales_Dataset.csv")


print("\n--- ORIGINAL COLUMNS ---")
print(df.columns.tolist())


df.columns = [
    str(col).strip().replace(" ", "_")
    for col in df.columns
]


rename_map = {
    "Product_ID": "Product_ID",
    "Product_Name": "Product_Name",
    "Category": "Category",
    "Supplier_ID": "Supplier_ID",
    "Supplier_Name": "Supplier_Name",
    "Stock_Quantity": "Stock_Quantity",
    "Reorder_Level": "Reorder_Level",
    "Reorder_Quantity": "Reorder_Quantity",
    "Unit_Price": "Unit_Price",
    "Date_Received": "Date_Received",
    "Last_Order_Date": "Last_Order_Date",
    "Expiration_Date": "Expiration_Date",
    "Warehouse_Location": "Warehouse_Location",
    "Sales_Volume": "Sales_Volume",
    "Inventory_Turnover_Rate": "Inventory_Turnover_Rate",
    "Status": "Status"
}

df = df.rename(columns=rename_map)

print("\n--- CLEANED COLUMNS ---")
print(df.columns.tolist())

print("\n--- ORIGINAL SHAPE ---")
print(df.shape)

# Remove duplicates
df = df.drop_duplicates()

# IMPORTANT: Do not filter/delete rows
# Just keep the dataset as it is

# Create clean inventory dataset using column positions
clean_inventory = df.iloc[:, [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 15
]].copy()

# Give selected columns correct names
clean_inventory.columns = [
    "Product_ID",
    "Product_Name",
    "Category",
    "Supplier_ID",
    "Supplier_Name",
    "Stock_Quantity",
    "Reorder_Level",
    "Reorder_Quantity",
    "Unit_Price",
    "Warehouse_Location",
    "Status"
]

# Fill missing values
clean_inventory["Product_Name"] = (
    clean_inventory["Product_Name"]
    .fillna("Unknown")
)

clean_inventory["Category"] = (
    clean_inventory["Category"]
    .fillna("Unknown")
)

# Save cleaned inventory dataset
clean_inventory.to_csv(
    "data/clean_inventory.csv",
    index=False
)

# Results
print("\n--- CLEAN DATASET SHAPE ---")
print(clean_inventory.shape)

print("\n--- MISSING VALUES ---")
print(clean_inventory.isnull().sum())

print("\n--- DUPLICATES ---")
print(clean_inventory.duplicated().sum())

print("\n--- FIRST 5 CLEAN RECORDS ---")
print(clean_inventory.head())

print("\nClean inventory dataset saved successfully!")