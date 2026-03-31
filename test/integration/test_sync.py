"""Tests for table synchronization.

This module contains integration tests for verifying that tables are correctly
synchronized with Pydantic models, including adding new columns and
creating tables if they do not exist.
"""

import os
import sys
from typing import Generator, List, Optional

import psycopg
import pytest
from loguru import logger
from pydantic import BaseModel, Field

# Ensure we can import from the parent directory for conftest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# pylint: disable=import-error, wrong-import-position, wrong-import-order
from conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL


@pytest.fixture(autouse=True)
def setup_teardown() -> Generator[None, None, None]:
    """Fixture to clean up tables before and after each test.

    Yields:
        None: Execution context for the test.
    """
    logger.info("Setting up sync test environment...")
    cleanup_table("person")
    cleanup_table("newtable")
    yield
    logger.info("Tearing down sync test environment...")
    cleanup_table("person")
    cleanup_table("newtable")


class TestSyncTable:
    """Tests for table synchronization logic.

    Verifies that adding fields to a Pydantic model results in new columns
    in the existing database table.
    """

    def test_add_new_column_to_existing_table(self) -> None:
        """Test adding a new column to an existing table.

        Initializes a table, inserts a record, then re-initializes with a new
        field in the model to trigger an ALTER TABLE.
        """
        logger.info("Testing adding new column to existing table...")

        class PersonV1(BaseModel):
            """Initial model version."""

            id: int = Field(..., description="Primary Key")
            name: str
            age: int

        # Create table with V1
        _ = WPostgreSQL(PersonV1, DB_CONFIG)

        class PersonV2(BaseModel):
            """Updated model version with 'email' column."""

            __tablename__ = "person"
            id: int = Field(..., description="Primary Key")
            name: str
            age: int
            email: Optional[str] = None

        # Trigger sync with V2
        _ = WPostgreSQL(PersonV2, DB_CONFIG)

        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'person'"
                )
                columns: List[str] = [row[0] for row in cursor.fetchall()]
                assert "email" in columns
        finally:
            pg_conn.close()
        logger.success("Add new column test passed.")

    def test_insert_with_new_column(self) -> None:
        """Test inserting data into a newly added column.

        Verifies that data can be correctly persisted and retrieved after
        the table schema has been synchronized.
        """
        logger.info("Testing insertion with new column...")

        class PersonBase(BaseModel):
            """Initial model."""

            __tablename__ = "person"
            id: int = Field(..., description="Primary Key")
            name: str

        db_v1 = WPostgreSQL(PersonBase, DB_CONFIG)
        db_v1.insert(PersonBase(id=1, name="Juan"))

        class PersonWithEmail(BaseModel):
            """Model with additional email field."""

            __tablename__ = "person"
            id: int = Field(..., description="Primary Key")
            name: str
            email: Optional[str] = None

        db_v2 = WPostgreSQL(PersonWithEmail, DB_CONFIG)
        db_v2.insert(PersonWithEmail(id=2, name="Ana", email="ana@example.com"))

        result = db_v2.get_by_field(id=2)
        assert len(result) == 1
        assert result[0].email == "ana@example.com"
        logger.success("Insertion with new column test passed.")

    def test_multiple_new_columns(self) -> None:
        """Test adding multiple columns simultaneously.

        Verifies that multiple schema changes are correctly handled in a single sync.
        """
        logger.info("Testing multiple new columns synchronization...")

        class PersonShort(BaseModel):
            """Minimal model."""

            __tablename__ = "person"
            id: int = Field(..., description="Primary Key")
            name: str

        _ = WPostgreSQL(PersonShort, DB_CONFIG)

        class PersonFull(BaseModel):
            """Full model with many new fields."""

            __tablename__ = "person"
            id: int = Field(..., description="Primary Key")
            name: str
            email: Optional[str] = None
            phone: Optional[str] = None
            address: Optional[str] = None

        _ = WPostgreSQL(PersonFull, DB_CONFIG)

        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'person'"
                )
                columns: List[str] = [row[0] for row in cursor.fetchall()]
                assert "email" in columns
                assert "phone" in columns
                assert "address" in columns
        finally:
            pg_conn.close()
        logger.success("Multiple new columns test passed.")


class TestCreateTable:
    """Tests for table creation logic.

    Verifies that tables are created if missing and that existing tables
    do not cause initialization failures.
    """

    def test_create_table_if_not_exists(self) -> None:
        """Test that a table is created if it does not exist.

        Verifies presence in information_schema.tables.
        """
        logger.info("Testing table creation if not exists...")

        class NewTable(BaseModel):
            """Model for a brand new table."""

            id: int
            name: str

        _ = WPostgreSQL(NewTable, DB_CONFIG)

        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS (SELECT FROM information_schema.tables "
                    "WHERE table_name = 'newtable')"
                )
                exists: bool = cursor.fetchone()[0]
                assert exists is True
        finally:
            pg_conn.close()
        logger.success("Table creation test passed.")

    def test_create_table_does_not_fail_if_exists(self) -> None:
        """Test that re-initialization with an existing table is safe.

        Verifies that multiple instances can be created without schema errors.
        """
        logger.info("Testing table re-initialization safety...")

        class ExistingTable(BaseModel):
            """Model for an already existing table."""

            __tablename__ = "newtable"
            id: int
            name: str

        _ = WPostgreSQL(ExistingTable, DB_CONFIG)
        db2 = WPostgreSQL(ExistingTable, DB_CONFIG)

        result = db2.get_all()
        assert isinstance(result, list)
        logger.success("Table re-initialization safety test passed.")
