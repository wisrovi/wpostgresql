"""Integration tests for table sync operations.

Tests that require a real database to verify table synchronization works correctly.
"""

import os
import sys
from collections.abc import Generator
from typing import Optional

import psycopg
import pytest
from loguru import logger
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import DB_CONFIG, cleanup_table

from wpostgresql import TableSync, WPostgreSQL


@pytest.fixture(autouse=True)
def setup_teardown() -> Generator[None, None, None]:
    """Fixture to clean up tables before and after each test."""
    logger.info("Setting up sync test environment...")
    cleanup_table("sync_test")
    yield
    logger.info("Tearing down sync test environment...")
    cleanup_table("sync_test")


class SyncModel(BaseModel):
    """Model for sync tests."""

    __tablename__ = "sync_test"
    id: int = Field(..., description="Primary Key")
    name: str
    email: Optional[str] = None


class TestTableSync:
    """Tests for TableSync operations."""

    def test_table_exists(self) -> None:
        """Test checking if table exists."""
        logger.info("Testing table exists...")

        WPostgreSQL(SyncModel, DB_CONFIG)
        sync = TableSync(SyncModel, DB_CONFIG)

        exists = sync.table_exists()
        assert exists is True
        logger.success("Table exists test passed.")

    def test_get_columns(self) -> None:
        """Test getting table columns."""
        logger.info("Testing get columns...")

        WPostgreSQL(SyncModel, DB_CONFIG)
        sync = TableSync(SyncModel, DB_CONFIG)

        columns = sync.get_columns()
        assert "id" in columns
        assert "name" in columns
        logger.success("Get columns test passed.")

    def test_create_index(self) -> None:
        """Test creating an index."""
        logger.info("Testing create index...")

        WPostgreSQL(SyncModel, DB_CONFIG)
        sync = TableSync(SyncModel, DB_CONFIG)

        index_name = "idx_sync_test_name"
        sync.drop_index(index_name)

        sync.create_index(["name"], unique=False)

        indexes = sync.get_indexes()
        index_names = [idx["name"] for idx in indexes]
        assert any("name" in idx for idx in index_names)
        logger.success("Create index test passed.")

    def test_drop_index(self) -> None:
        """Test dropping an index."""
        logger.info("Testing drop index...")

        WPostgreSQL(SyncModel, DB_CONFIG)
        sync = TableSync(SyncModel, DB_CONFIG)

        index_name = "idx_sync_test_name"
        sync.create_index(["name"], unique=False)
        sync.drop_index(index_name)

        indexes = sync.get_indexes()
        index_names = [idx["name"] for idx in indexes]
        assert not any(index_name in idx for idx in index_names)
        logger.success("Drop index test passed.")

    def test_get_indexes(self) -> None:
        """Test getting table indexes."""
        logger.info("Testing get indexes...")

        WPostgreSQL(SyncModel, DB_CONFIG)
        sync = TableSync(SyncModel, DB_CONFIG)

        sync.create_index(["name"], unique=False)

        indexes = sync.get_indexes()
        assert len(indexes) >= 1
        logger.success("Get indexes test passed.")

    def test_drop_table(self) -> None:
        """Test dropping a table."""
        logger.info("Testing drop table...")

        WPostgreSQL(SyncModel, DB_CONFIG)
        sync = TableSync(SyncModel, DB_CONFIG)

        sync.drop_table()

        exists = sync.table_exists()
        assert exists is False
        logger.success("Drop table test passed.")

    def test_table_not_exists(self) -> None:
        """Test table does not exist."""
        logger.info("Testing table not exists...")

        cleanup_table("nonexistent_table")

        class NonExistent(BaseModel):
            __tablename__ = "nonexistent_table"
            id: int
            name: str

        sync = TableSync(NonExistent, DB_CONFIG)
        exists = sync.table_exists()
        assert exists is False
        logger.success("Table not exists test passed.")

    def test_create_index_unique(self) -> None:
        """Test creating a unique index."""
        logger.info("Testing create unique index...")

        WPostgreSQL(SyncModel, DB_CONFIG)
        sync = TableSync(SyncModel, DB_CONFIG)

        index_name = "idx_unique_name"
        sync.drop_index(index_name)

        sync.create_index(["name"], unique=True)

        indexes = sync.get_indexes()
        index_defs = [idx["definition"] for idx in indexes]
        assert any("UNIQUE" in idx for idx in index_defs)
        logger.success("Create unique index test passed.")


class TestSyncNewColumns:
    """Tests for synchronizing new columns."""

    def test_sync_add_new_column(self) -> None:
        """Test adding new column to existing table."""
        logger.info("Testing sync add new column...")

        class InitialModel(BaseModel):
            __tablename__ = "sync_test"
            id: int = Field(..., description="Primary Key")
            name: str

        WPostgreSQL(InitialModel, DB_CONFIG)

        class UpdatedModel(BaseModel):
            __tablename__ = "sync_test"
            id: int = Field(..., description="Primary Key")
            name: str
            age: Optional[int] = None

        WPostgreSQL(UpdatedModel, DB_CONFIG)

        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'sync_test'"
                )
                columns = [row[0] for row in cursor.fetchall()]
                assert "age" in columns
        finally:
            pg_conn.close()

        logger.success("Sync add new column test passed.")
