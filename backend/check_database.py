import sqlite3

connection = sqlite3.connect("db/marketmind.db")
cursor = connection.cursor()

print("\n==================== DATABASE TABLES SUMMARY ====================")

tables = ["users", "customers", "products", "sales", "inventory", "invoices"]
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"Table: {table:<15} Row Count: {count}")

print("\n==================== SAMPLE SALES (EXACTLY 8) ====================")
cursor.execute("""
    SELECT s.order_id, p.name, s.quantity, s.unit_price, s.sale_date, c.name, i.amount, i.payment_status
    FROM sales s
    JOIN products p ON s.product_id = p.id
    JOIN customers c ON s.customer_id = c.id
    LEFT JOIN invoices i ON i.sale_id = s.id
    ORDER BY s.order_id ASC
""")
for row in cursor.fetchall():
    print(f"Order #{row[0]}: {row[1]:<12} | Qty: {row[2]:>2} | Price: ${row[3]:>5.2f} | Date: {row[4]} | Customer: {row[5]:<18} | Inv: ${row[6]:>6.2f} ({row[7]})")

print("\n==================== INVENTORY STATUS & ALERTS ====================")
cursor.execute("""
    SELECT p.name, inv.stock_level, inv.reorder_point,
           CASE WHEN inv.stock_level < inv.reorder_point THEN 'LOW STOCK ALERT' ELSE 'HEALTHY' END AS status
    FROM inventory inv
    JOIN products p ON inv.product_id = p.id
""")
for row in cursor.fetchall():
    print(f"Product: {row[0]:<15} | Stock: {row[1]:>2} | Reorder Point: {row[2]:>2} | Status: {row[3]}")

print("\n==================== USERS & ROLES ====================")
cursor.execute("SELECT id, name, email, role FROM users")
for row in cursor.fetchall():
    print(f"User ID {row[0]}: {row[1]:<20} | Email: {row[2]:<22} | Role: {row[3]}")

connection.close()