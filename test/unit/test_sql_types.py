"""Tests for SQL type mapping.

This module contains unit tests to verify that Pydantic field types
are correctly mapped to their corresponding PostgreSQL data types.
"""

import os
import sys
from collections.abc import Generator

import psycopg
import pytest
from loguru import logger
from pydantic import BaseModel

# Ensure we can import from the parent directory for conftest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# pylint: disable=import-error, wrong-import-position, wrong-import-order
from conftest import DB_CONFIG, cleanup_table

from wpostgresql import WPostgreSQL


class SampleModel(BaseModel):
    """Reference model for type mapping tests."""
    id: int
    name: str
    age: int
    is_active: bool


@pytest.fixture(autouse=True)
def setup_teardown() -> Generator[None, None, None]:
    """Fixture to clean up tables before and after each test.

    Yields:
        None: Execution context for the test.
    """
    logger.info("Setting up SQL type mapping test environment...")
    cleanup_table("samplemodel")
    cleanup_table("mymodel")
    cleanup_table("userprofile")
    yield
    logger.info("Tearing down SQL type mapping test environment...")
    cleanup_table("samplemodel")
    cleanup_table("mymodel")
    cleanup_table("userprofile")


class TestSQLTypeMapping:
    """Tests for Pydantic to SQL type conversion.

    Verifies that basic Python/Pydantic types map to the expected
    PostgreSQL data types in the database schema.
    """

    def _get_table_columns(self, table_name: str) -> dict[str, str]:
        """Helper to retrieve column types from the database.

        Args:
            table_name: The name of the table to inspect.

        Returns:
            Dict[str, str]: A mapping of column names to their SQL data types.
        """
        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute(
                    "SELECT column_name, data_type FROM information_schema.columns "
                    "WHERE table_name = %s", (table_name,)
                )
                return {row[0]: row[1] for row in cursor.fetchall()}
        finally:
            pg_conn.close()

    def test_int_maps_to_integer(self) -> None:
        """Test that int maps to integer.

        Verifies that Pydantic int fields result in 'integer' columns.
        """
        logger.info("Testing mapping of int to integer...")
        # Trigger table creation
        _ = WPostgreSQL(SampleModel, DB_CONFIG)
        columns = self._get_table_columns("samplemodel")

        assert columns["id"] == "integer"
        assert columns["age"] == "integer"
        logger.success("int mapping test passed.")

    def test_str_maps_to_text(self) -> None:
        """Test that str maps to text.

        Verifies that Pydantic str fields result in 'text' columns.
        """
        logger.info("Testing mapping of str to text...")
        _ = WPostgreSQL(SampleModel, DB_CONFIG)
        columns = self._get_table_columns("samplemodel")

        assert columns["name"] == "text"
        logger.success("str mapping test passed.")

    def test_bool_maps_to_boolean(self) -> None:
        """Test that bool maps to boolean.

        Verifies that Pydantic bool fields result in 'boolean' columns.
        """
        logger.info("Testing mapping of bool to boolean...")
        _ = WPostgreSQL(SampleModel, DB_CONFIG)
        columns = self._get_table_columns("samplemodel")

        assert columns["is_active"] == "boolean"
        logger.success("bool mapping test passed.")


class TestTableName:
    """Tests for table name generation.

    Verifies that the database table name is correctly derived from
    the Pydantic model name.
    """

    def test_table_name_is_lowercase_model_name(self) -> None:
        """Test table name is lowercase model name.

        Verifies the default naming convention for single-word models.
        """
        logger.info("Testing lowercase table name convention...")

        class MyModel(BaseModel):
            """Test model."""
            id: int
            name: str

        db = WPostgreSQL(MyModel, DB_CONFIG)
        assert db.table_name == "mymodel"
        logger.success("Lowercase naming test passed.")

    def test_table_name_with_multiple_words(self) -> None:
        """Test table name with multiple words.

        Verifies that CamelCase model names are converted to lowercase
        without separators by default.
        """
        logger.info("Testing multi-word table name convention...")

        class UserProfile(BaseModel):
            """Test model with multiple words."""
            id: int
            full_name: str

        db = WPostgreSQL(UserProfile, DB_CONFIG)
        assert db.table_name == "userprofile"
        logger.success("Multi-word naming test passed.")
