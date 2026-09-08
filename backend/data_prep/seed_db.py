import csv
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database import engine, Base, SessionLocal
import models
from auth import get_password_hash


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # --- Roles ---
        role_defs = [
            ("franchise_owner", "Global view across every outlet"),
            ("outlet_manager", "Single-outlet view, restock alerts, stock management"),
            ("waiter", "Order entry and quick menu lookup"),
            ("admin", "Staff administration and RBAC provisioning"),
        ]
        roles = {}
        for name, desc in role_defs:
            role = db.query(models.Role).filter(models.Role.role_name == name).first()
            if not role:
                role = models.Role(role_name=name, description=desc)
                db.add(role)
                db.commit()
                db.refresh(role)
            roles[name] = role

        # --- Outlets ---
        outlet_defs = [
            ("OUT-BBSR", "MarketMind - Bhubaneswar", "Bhubaneswar", "+91-90000-00001"),
            ("OUT-KOL", "MarketMind - Kolkata", "Kolkata", "+91-90000-00002"),
            ("OUT-BLR", "MarketMind - Bengaluru", "Bengaluru", "+91-90000-00003"),
        ]
        for outlet_id, name, city, phone in outlet_defs:
            if not db.query(models.Outlet).filter(models.Outlet.outlet_id == outlet_id).first():
                db.add(models.Outlet(outlet_id=outlet_id, outlet_name=name, city=city, contact_phone=phone))
        db.commit()

        # --- Demo staff accounts ---
        demo_accounts = [
            ("owner", "owner@marketmind.dev", "Franchise Owner", "franchise_owner", None),
            ("manager", "manager@marketmind.dev", "Outlet Manager", "outlet_manager", "OUT-BBSR"),
            ("waiter", "waiter@marketmind.dev", "Front Desk Waiter", "waiter", "OUT-BBSR"),
            ("admin", "admin@marketmind.dev", "Platform Admin", "admin", None),
        ]
        for username, email, full_name, role_key, outlet_id in demo_accounts:
            if not db.query(models.Staff).filter(models.Staff.username == username).first():
                db.add(models.Staff(
                    username=username,
                    email=email,
                    hashed_password=get_password_hash("password123"),
                    full_name=full_name,
                    role_id=roles[role_key].role_id,
                    outlet_id=outlet_id
                ))
        db.commit()

        # --- Menu items from cleaned CSV ---
        processed_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
        menu_csv = os.path.join(processed_dir, "menu_clean.csv")
        orders_csv = os.path.join(processed_dir, "orders_clean.csv")

        with open(menu_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if not db.query(models.MenuItem).filter(models.MenuItem.item_id == row["item_id"]).first():
                    db.add(models.MenuItem(
                        item_id=row["item_id"],
                        item_name=row["item_name"],
                        category=row["category"],
                        unit_price=float(row["unit_price"]),
                        stock_units=int(row["stock_units"]),
                        reorder_level=int(row["reorder_level"]),
                    ))
        db.commit()

        # --- Patrons referenced by orders ---
        patron_ids = set()
        with open(orders_csv, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            patron_ids.add(row["patron_id"])

        for pid in patron_ids:
            if pid == "WALKIN":
                continue
            if not db.query(models.Patron).filter(models.Patron.patron_id == pid).first():
                db.add(models.Patron(patron_id=pid, patron_name=f"Guest {pid}"))
        db.commit()

        # --- Orders ---
        for row in rows:
            if db.query(models.Order).filter(models.Order.order_id == row["order_id"]).first():
                continue
            db.add(models.Order(
                order_id=row["order_id"],
                order_time=datetime.strptime(row["order_time"], "%Y-%m-%d %H:%M:%S"),
                item_id=row["item_id"],
                quantity=int(row["quantity"]),
                unit_price=float(row["unit_price"]),
                total_amount=float(row["total_amount"]),
                outlet_id=row["outlet_id"],
                patron_id=row["patron_id"] if row["patron_id"] != "WALKIN" else None,
                payment_mode=row["payment_mode"],
            ))
        db.commit()

        print("Seed complete: roles, outlets, demo staff, menu items, patrons, orders.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
