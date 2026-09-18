"""Example demonstrating PostgreSQL table backup to SQLite using wsqlite in WPostgreSQL."""

import asyncio
from pathlib import Path
from pydantic import BaseModel, Field
from wpostgresql import WPostgreSQL

db_config = {
    "dbname": "mcp",
    "user": "myuser",
    "password": "mypassword",
    "host": "192.168.1.68",
    "port": 5432,
}


class Product(BaseModel):
    """Product model for backup demonstration."""

    __tablename__ = "products_backup_demo"
    id: int = Field(description="Primary Key")
    name: str = Field(description="NOT NULL")
    price: float
    stock: int


def run_sync_backup():
    """Run synchronous backup examples."""
    db = WPostgreSQL(Product, db_config)

    # Insert sample records into PostgreSQL (ignore if already inserted)
    try:
        db.insert(Product(id=1, name="Laptop", price=999.99, stock=10))
        db.insert(Product(id=2, name="Mouse", price=25.50, stock=50))
        db.insert(Product(id=3, name="Keyboard", price=49.99, stock=30))
    except Exception:
        pass

    # 1. Synchronous backup (Atomic replace by default)
    sqlite_file = Path("products_backup.db")
    count = db.backup_to_sqlite(sqlite_file)
    print(f"[Sync Atomic] Successfully backed up {count} products to {sqlite_file}")

    # 2. Synchronous backup with update=True (In-place update/sync)
    count_update = db.backup_to_sqlite(sqlite_file, update=True)
    print(f"[Sync Update] Successfully updated backup of {count_update} products in {sqlite_file}")


async def run_async_backup():
    """Run asynchronous backup examples."""
    db = WPostgreSQL(Product, db_config)

    # 1. Asynchronous backup (Atomic replace by default)
    sqlite_async_file = Path("products_backup_async.db")
    count_async = await db.backup_to_sqlite_async(sqlite_async_file)
    print(f"[Async Atomic] Successfully backed up {count_async} products asynchronously to {sqlite_async_file}")

    # 2. Asynchronous backup with update=True (In-place update/sync)
    count_async_update = await db.backup_to_sqlite_async(sqlite_async_file, update=True)
    print(f"[Async Update] Successfully updated backup of {count_async_update} products asynchronously in {sqlite_async_file}")


if __name__ == "__main__":
    run_sync_backup()
    asyncio.run(run_async_backup())

