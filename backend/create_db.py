from backend.database import Base, engine
# Import all models to ensure they are registered with Base.metadata
from backend.models import User, Customer, Product, Sale, Inventory, Invoice

def init_db():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully:")
    for table_name in Base.metadata.tables.keys():
        print(f" - {table_name}")

if __name__ == "__main__":
    init_db()