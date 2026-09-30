"""Unit tests for WPostgreSQL restore_from_sqlite functionality."""

from pydantic import BaseModel, Field
import pytest

from wpostgresql import WPostgreSQL, backup_to_sqlite, restore_from_sqlite, restore_from_sqlite_async


class ProductRestoreDemo(BaseModel):
    name: str = Field(description="Product name")
    price: float = Field(description="Product price")


@pytest.fixture
def db_config():
    return {
        "dbname": "wpostgresql",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432,
    }


def test_restore_from_sqlite_sync(db_config, tmp_path):
    """Test sync backup to SQLite and restoring records back to PostgreSQL."""
    sqlite_file = tmp_path / "restore_test.db"
    db = WPostgreSQL(ProductRestoreDemo, db_config)

    # Insert items into PostgreSQL
    p1 = db.insert(ProductRestoreDemo(name="Monitor", price=299.99))
    p2 = db.insert(ProductRestoreDemo(name="Mousepad", price=15.00))

    # Backup to SQLite
    backed_up_count = db.backup_to_sqlite(sqlite_file)
    assert backed_up_count >= 2

    # Delete records from PostgreSQL
    db.delete(p1.id, hard=True)
    db.delete(p2.id, hard=True)

    # Restore records back into PostgreSQL
    restored_count = db.restore_from_sqlite(sqlite_file)
    assert restored_count >= 2

    pg_records = db.get_all()
    names = [r.name for r in pg_records]
    assert "Monitor" in names
    assert "Mousepad" in names


@pytest.mark.asyncio
async def test_restore_from_sqlite_async(db_config, tmp_path):
    """Test async backup to SQLite and restoring records back to PostgreSQL."""
    sqlite_file = tmp_path / "restore_test_async.db"
    db = WPostgreSQL(ProductRestoreDemo, db_config)

    # Insert items
    p1 = db.insert(ProductRestoreDemo(name="Headset", price=79.99))

    # Backup
    await db.backup_to_sqlite_async(sqlite_file)

    # Delete
    db.delete(p1.id, hard=True)

    # Restore async
    restored_count = await db.restore_from_sqlite_async(sqlite_file)
    assert restored_count >= 1

    pg_records = db.get_all()
    names = [r.name for r in pg_records]
    assert "Headset" in names
