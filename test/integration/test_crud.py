"""Integration tests for CRUD operations.

This module contains tests to verify that basic Create, Read, Update, and
Delete operations work correctly with the WPostgreSQL repository and
PostgreSQL database.
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


class Person(BaseModel):
    """Reference model for CRUD tests."""

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
    logger.info("Setting up CRUD test environment...")
    cleanup_table("person")
    cleanup_table("personstropt")
    cleanup_table("personintopt")
    cleanup_table("personboolopt")
    yield
    logger.info("Tearing down CRUD test environment...")
    cleanup_table("person")
    cleanup_table("personstropt")
    cleanup_table("personintopt")
    cleanup_table("personboolopt")


class TestInsert:
    """Tests for the insert() method.

    Verifies single and multiple record insertions, including data validation.
    """

    def test_insert_single_record(self) -> None:
        """Test inserting a single record.

        Verifies that data is correctly persisted and can be retrieved.
        """
        logger.info("Testing single record insertion...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        result: list[Person] = db.get_all()
        assert len(result) == 1
        assert result[0].name == "Juan"
        assert result[0].age == 30
        logger.success("Single record insertion test passed.")

    def test_insert_multiple_records(self) -> None:
        """Test inserting multiple records sequentially.

        Verifies that the table accumulates records correctly.
        """
        logger.info("Testing multiple record insertions...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))
        db.insert(Person(id=2, name="Ana", age=25, is_active=True))

        result: list[Person] = db.get_all()
        assert len(result) == 2
        logger.success("Multiple record insertions test passed.")

    def test_insert_validates_pydantic(self) -> None:
        """Test that insert validates data against the Pydantic model.

        Ensures that invalid types raise an exception before reaching the DB.
        """
        logger.info("Testing Pydantic validation during insertion...")
        db = WPostgreSQL(Person, DB_CONFIG)

        with pytest.raises((ValueError, TypeError)):
            # id is expected to be int, passing str
            db.insert(Person(id="invalid", name="Juan", age=30, is_active=True))  # type: ignore
        logger.success("Pydantic validation test passed.")


class TestGetAll:
    """Tests for the get_all() method.

    Verifies that all records can be retrieved as a list of model instances.
    """

    def test_get_all_returns_list(self) -> None:
        """Test that get_all returns a list even if empty.

        Ensures consistent return type.
        """
        logger.info("Testing get_all return type...")
        db = WPostgreSQL(Person, DB_CONFIG)
        result = db.get_all()
        assert isinstance(result, list)
        logger.success("get_all return type test passed.")

    def test_get_all_with_data(self) -> None:
        """Test get_all with records present.

        Verifies that the correct number of items is returned.
        """
        logger.info("Testing get_all with data...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))
        db.insert(Person(id=2, name="Ana", age=25, is_active=True))

        result: list[Person] = db.get_all()
        assert len(result) == 2
        logger.success("get_all with data test passed.")


class TestGetByField:
    """Tests for the get_by_field() method.

    Verifies filtering capabilities using single and multiple fields.
    """

    def test_get_by_single_field(self) -> None:
        """Test filtering by one field.

        Verifies that only matching records are returned.
        """
        logger.info("Testing get_by_field (single field)...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))
        db.insert(Person(id=2, name="Ana", age=25, is_active=True))

        result: list[Person] = db.get_by_field(name="Juan")
        assert len(result) == 1
        assert result[0].age == 30
        logger.success("get_by_field single field test passed.")

    def test_get_by_multiple_fields(self) -> None:
        """Test filtering by multiple fields simultaneously.

        Verifies that multiple conditions are combined (AND logic).
        """
        logger.info("Testing get_by_field (multiple fields)...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))
        db.insert(Person(id=2, name="Ana", age=25, is_active=True))
        db.insert(Person(id=3, name="Pedro", age=25, is_active=True))

        result: list[Person] = db.get_by_field(age=25, is_active=True)
        assert len(result) == 2
        logger.success("get_by_field multiple fields test passed.")

    def test_get_by_field_no_match(self) -> None:
        """Test filtering with no matching results.

        Ensures an empty list is returned when no records match the criteria.
        """
        logger.info("Testing get_by_field (no match)...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        result: list[Person] = db.get_by_field(name="NoExiste")
        assert len(result) == 0
        logger.success("get_by_field no match test passed.")

    def test_get_by_field_empty_returns_all(self) -> None:
        """Test that calling get_by_field without parameters returns all records.

        Verifies behavior when no filters are provided.
        """
        logger.info("Testing get_by_field with no filters...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        result: list[Person] = db.get_by_field()
        assert len(result) == 1
        logger.success("get_by_field empty filters test passed.")


class TestUpdate:
    """Tests for the update() method.

    Verifies that records can be modified by ID.
    """

    def test_update_record(self) -> None:
        """Test updating an existing record.

        Verifies that changes are persisted correctly.
        """
        logger.info("Testing update record...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        db.update(1, Person(id=1, name="Juan", age=31, is_active=False))

        result: Person = db.get_by_field(id=1)[0]
        assert result.age == 31
        assert result.is_active is False
        logger.success("Update record test passed.")

    def test_update_non_existent(self) -> None:
        """Test updating a record that does not exist.

        Ensures that trying to update a missing ID doesn't crash or modify other data.
        """
        logger.info("Testing update non-existent record...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        db.update(999, Person(id=999, name="NoExiste", age=20, is_active=True))

        result: list[Person] = db.get_all()
        assert len(result) == 1
        logger.success("Update non-existent record test passed.")


class TestDelete:
    """Tests for the delete() method.

    Verifies record removal by ID.
    """

    def test_delete_record(self) -> None:
        """Test deleting an existing record.

        Verifies that the record is truly removed from the table.
        """
        logger.info("Testing delete record...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))
        db.insert(Person(id=2, name="Ana", age=25, is_active=True))

        db.delete(1)

        result: list[Person] = db.get_all()
        assert len(result) == 1
        assert result[0].name == "Ana"
        logger.success("Delete record test passed.")

    def test_delete_non_existent(self) -> None:
        """Test deleting a record that does not exist.

        Ensures that trying to delete a missing ID is safe.
        """
        logger.info("Testing delete non-existent record...")
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        db.delete(999)

        result: list[Person] = db.get_all()
        assert len(result) == 1
        logger.success("Delete non-existent record test passed.")


class TestNullHandling:
    """Tests for handling NULL values in the database.

    Verifies how the repository behaves when encountering NULLs for
    non-optional fields.
    """

    def test_null_handling_string(self) -> None:
        """Test NULL handling for string fields.

        Ensures that NULL strings are converted to empty strings by default.
        """
        logger.info("Testing NULL handling for text...")

        class PersonStrOpt(BaseModel):
            """Test model for NULL strings."""

            __tablename__ = "personstropt"
            id: int
            name: str
            nickname: str = ""

        db = WPostgreSQL(PersonStrOpt, DB_CONFIG)

        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute("INSERT INTO personstropt (id, name) VALUES (1, 'Juan')")
        finally:
            pg_conn.close()

        result: list[PersonStrOpt] = db.get_all()
        assert result[0].nickname == ""
        logger.success("NULL string handling test passed.")

    def test_null_handling_int(self) -> None:
        """Test NULL handling for integer fields.

        Ensures that NULL integers are converted to 0 by default.
        """
        logger.info("Testing NULL handling for integers...")

        class PersonIntOpt(BaseModel):
            """Test model for NULL integers."""

            __tablename__ = "personintopt"
            id: int
            name: str
            age: int = 0

        db = WPostgreSQL(PersonIntOpt, DB_CONFIG)

        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute("INSERT INTO personintopt (id, name) VALUES (1, 'Juan')")
        finally:
            pg_conn.close()

        result: list[PersonIntOpt] = db.get_all()
        assert result[0].age == 0
        logger.success("NULL integer handling test passed.")

    def test_null_handling_bool(self) -> None:
        """Test NULL handling for boolean fields.

        Ensures that NULL booleans are converted to False by default.
        """
        logger.info("Testing NULL handling for booleans...")

        class PersonBoolOpt(BaseModel):
            """Test model for NULL booleans."""

            __tablename__ = "personboolopt"
            id: int
            name: str
            is_active: bool = False

        db = WPostgreSQL(PersonBoolOpt, DB_CONFIG)

        pg_conn = psycopg.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        try:
            with pg_conn.cursor() as cursor:
                cursor.execute("INSERT INTO personboolopt (id, name) VALUES (1, 'Juan')")
        finally:
            pg_conn.close()

        result: list[PersonBoolOpt] = db.get_all()
        assert result[0].is_active is False
        logger.success("NULL boolean handling test passed.")
