"""Example demonstrating PostgreSQL table backup to SQLite using wsqlite in WPostgreSQL."""

from pathlib import Path
from pydantic import BaseModel, Field
from wpostgresql import WPostgreSQL

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Product(BaseModel):
    """Product model for backup demonstration."""

    __tablename__ = "products_backup_demo"
    id: int = Field(description="Primary Key")
    name: str = Field(description="NOT NULL")
    price: float
    stock: int


def main():
    """Run backup example."""
    db = WPostgreSQL(Product, db_config)

    # Insert sample records into PostgreSQL
    db.insert(Product(id=1, name="Laptop", price=999.99, stock=10))
    db.insert(Product(id=2, name="Mouse", price=25.50, stock=50))
    db.insert(Product(id=3, name="Keyboard", price=49.99, stock=30))

    # Backup to SQLite database file using wsqlite
    sqlite_file = Path("products_backup.db")
    count = db.backup_to_sqlite(sqlite_file)

    print(f"Successfully backed up {count} products to {sqlite_file}")


if __name__ == "__main__":
    main()
