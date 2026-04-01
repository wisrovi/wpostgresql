"""Tests for database restrictions.

This module contains unit tests to verify that primary keys, unique constraints,
and not null constraints are correctly applied in the PostgreSQL database
based on Pydantic model definitions.
"""

import os
import sys
from collections.abc import Generator
from typing import Optional

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
    logger.info("Setting up restriction test environment...")
    cleanup_table("restrictedmodel")
    cleanup_table("uniquemodel")
    cleanup_table("notnullmodel")
    yield
    logger.info("Tearing down restriction test environment...")
    cleanup_table("restrictedmodel")
    cleanup_table("uniquemodel")
    cleanup_table("notnullmodel")


class TestPrimaryKey:
    """Tests for PRIMARY KEY constraints.

    Verifies that fields marked as primary keys in Pydantic models
    result in actual primary key constraints in the database.
    """

    def test_primary_key_constraint(self) -> None:
        """Test that PRIMARY KEY constraint is correctly applied.

        Creates a model with a primary key and checks information_schema.
        """
        logger.info("Testing PRIMARY KEY constraint...")

        class RestrictedModel(BaseModel):
            """Model with primary key."""
            id: int = Field(..., description="Primary Key")
            name: str

        # Initialize WPostgreSQL to trigger table creation
        _ = WPostgreSQL(RestrictedModel, DB_CONFIG)

        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = 'restrictedmodel'
                      AND tc.constraint_type = 'PRIMARY KEY'
                """)
                pkeys: list[str] = [row[0] for row in cursor.fetchall()]
                assert "id" in pkeys
        finally:
            pg_conn.close()
        logger.success("PRIMARY KEY constraint test passed.")


class TestUniqueConstraint:
    """Tests for UNIQUE constraints.

    Verifies that fields marked as unique in Pydantic models
    result in actual unique constraints in the database.
    """

    def test_unique_constraint(self) -> None:
        """Test that UNIQUE constraint is correctly applied.

        Creates a model with a unique field and checks information_schema.
        """
        logger.info("Testing UNIQUE constraint...")

        class UniqueModel(BaseModel):
            """Model with unique constraint."""
            id: int = Field(..., description="Primary Key")
            email: Optional[str] = Field(None, description="UNIQUE")

        # Initialize WPostgreSQL to trigger table creation
        _ = WPostgreSQL(UniqueModel, DB_CONFIG)

        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_name = 'uniquemodel'
                      AND tc.constraint_type = 'UNIQUE'
                """)
                unique_cols: list[str] = [row[0] for row in cursor.fetchall()]
                assert "email" in unique_cols
        finally:
            pg_conn.close()
        logger.success("UNIQUE constraint test passed.")


class TestNotNullConstraint:
    """Tests for NOT NULL constraints.

    Verifies that mandatory fields in Pydantic models
    result in actual NOT NULL constraints in the database.
    """

    def test_not_null_constraint(self) -> None:
        """Test that NOT NULL constraint is correctly applied.

        Creates a model with a not null field and checks information_schema.
        """
        logger.info("Testing NOT NULL constraint...")

        class NotNullModel(BaseModel):
            """Model with NOT NULL constraint."""
            id: int = Field(..., description="Primary Key")
            name: str = Field(..., description="NOT NULL")

        # Initialize WPostgreSQL to trigger table creation
        _ = WPostgreSQL(NotNullModel, DB_CONFIG)

        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'notnullmodel'
                      AND is_nullable = 'NO'
                      AND column_name != 'id'
                """)
                not_null_cols: list[str] = [row[0] for row in cursor.fetchall()]
                assert "name" in not_null_cols
        finally:
            pg_conn.close()
        logger.success("NOT NULL constraint test passed.")
