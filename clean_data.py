import pandas as pd

file_path = "data/raw/customer.xlsx"

df = pd.read_excel(file_path)

print("Original shape:", df.shape)

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

# Remove duplicate rows
df = df.drop_duplicates()

# Remove rows without product description
df = df.dropna(subset=["Description"])

# Remove invalid prices
df = df[df["UnitPrice"] > 0]

# Keep completed sales transactions
df = df[df["Quantity"] > 0]

# Convert date column
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Calculate revenue
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

print("\nCleaned shape:", df.shape)

print("\nFirst 5 cleaned rows:")
print(df.head())

# Save cleaned dataset
output_path = "data/processed/cleaned_sales.csv"
df.to_csv(output_path, index=False)

print("\nCleaned dataset saved to:", output_path)