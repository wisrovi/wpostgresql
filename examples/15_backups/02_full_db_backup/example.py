"""Example demonstrating full database backup to SQLite and SQL dump generation in WPostgreSQL."""

import asyncio
from pathlib import Path
from pydantic import BaseModel, Field
from wpostgresql import (
    WPostgreSQL,
    backup_db_to_sqlite,
    backup_db_to_sqlite_async,
    export_to_sql_script,
    export_to_sql_script_async,
)

db_config = {
    "dbname": "mcp",
    "user": "myuser",
    "password": "mypassword",
    "host": "192.168.1.68",
    "port": 5432,
}


class User(BaseModel):
    """User model for database backup demonstration."""

    __tablename__ = "users_full_backup_demo"
    id: int = Field(description="Primary Key")
    username: str = Field(description="NOT NULL")
    email: str


class Order(BaseModel):
    """Order model for database backup demonstration."""

    __tablename__ = "orders_full_backup_demo"
    id: int = Field(description="Primary Key")
    user_id: int
    amount: float


models = [User, Order]


def run_full_db_backup():
    """Run full database backup and SQL script export (Sync)."""
    # Initialize tables and insert sample records
    db_user = WPostgreSQL(User, db_config)
    db_order = WPostgreSQL(Order, db_config)

    try:
        db_user.insert(User(id=1, username="alice", email="alice@example.com"))
        db_user.insert(User(id=2, username="bob", email="bob@example.com"))
        db_order.insert(Order(id=101, user_id=1, amount=150.50))
        db_order.insert(Order(id=102, user_id=2, amount=75.25))
    except Exception:
        pass

    # 1. Full Database Backup to SQLite (Synchronous)
    sqlite_path = Path("full_database_backup.db")
    results = backup_db_to_sqlite(models, db_config, sqlite_path)
    print(f"[Sync Full DB Backup] Backed up tables to {sqlite_path}: {results}")

    # 2. Export Database to SQL Reconstruction Script (Synchronous)
    sql_script_path = Path("full_database_dump.sql")
    out_path = export_to_sql_script(models, db_config, sql_script_path)
    print(f"[Sync SQL Dump Script] Exported SQL reconstruction script to: {out_path}")


async def run_full_db_backup_async():
    """Run full database backup and SQL script export (Async)."""
    # 1. Full Database Backup to SQLite (Asynchronous)
    sqlite_async_path = Path("full_database_backup_async.db")
    async_results = await backup_db_to_sqlite_async(models, db_config, sqlite_async_path)
    print(f"[Async Full DB Backup] Backed up tables to {sqlite_async_path}: {async_results}")

    # 2. Export Database to SQL Reconstruction Script (Asynchronous)
    sql_script_async_path = Path("full_database_dump_async.sql")
    async_out_path = await export_to_sql_script_async(models, db_config, sql_script_async_path)
    print(f"[Async SQL Dump Script] Exported SQL reconstruction script asynchronously to: {async_out_path}")


if __name__ == "__main__":
    run_full_db_backup()
    asyncio.run(run_full_db_backup_async())
