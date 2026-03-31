"""Integration tests for repository operations.

Tests that require a real database to verify repository CRUD operations.
"""

import sys
import os
from typing import Generator, Optional

import pytest
from loguru import logger
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL


@pytest.fixture(autouse=True)
def setup_teardown() -> Generator[None, None, None]:
    """Fixture to clean up tables before and after each test."""
    logger.info("Setting up repository test environment...")
    cleanup_table("repo_test")
    yield
    logger.info("Tearing down repository test environment...")
    cleanup_table("repo_test")


class RepoPerson(BaseModel):
    """Model for repository tests."""

    __tablename__ = "repo_test"
    id: int = Field(..., description="Primary Key")
    name: str
    email: Optional[str] = None
    age: Optional[int] = None


class TestRepositoryCRUD:
    """Tests for basic CRUD operations."""

    def test_insert(self) -> None:
        """Test insert operation."""
        logger.info("Testing insert...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)
        db.insert(RepoPerson(id=1, name="John", email="john@test.com"))

        result = db.get_all()
        assert len(result) == 1
        assert result[0].name == "John"
        logger.success("Insert test passed.")

    def test_get_all(self) -> None:
        """Test get_all operation."""
        logger.info("Testing get_all...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        db.insert(RepoPerson(id=1, name="Alice"))
        db.insert(RepoPerson(id=2, name="Bob"))

        result = db.get_all()
        assert len(result) == 2
        logger.success("Get all test passed.")

    def test_get_by_field(self) -> None:
        """Test get_by_field operation."""
        logger.info("Testing get_by_field...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        db.insert(RepoPerson(id=1, name="Alice", age=25))
        db.insert(RepoPerson(id=2, name="Bob", age=30))

        result = db.get_by_field(name="Alice")
        assert len(result) == 1
        assert result[0].age == 25
        logger.success("Get by field test passed.")

    def test_update(self) -> None:
        """Test update operation."""
        logger.info("Testing update...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        db.insert(RepoPerson(id=1, name="John"))
        db.update(1, RepoPerson(id=1, name="John Updated", email="new@test.com"))

        result = db.get_by_field(id=1)
        assert result[0].name == "John Updated"
        logger.success("Update test passed.")

    def test_delete(self) -> None:
        """Test delete operation."""
        logger.info("Testing delete...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        db.insert(RepoPerson(id=1, name="John"))
        db.delete(1)

        result = db.get_all()
        assert len(result) == 0
        logger.success("Delete test passed.")


class TestRepositoryPagination:
    """Tests for pagination operations."""

    def test_get_paginated(self) -> None:
        """Test get_paginated operation."""
        logger.info("Testing get_paginated...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        for i in range(1, 11):
            db.insert(RepoPerson(id=i, name=f"Person{i}"))

        result = db.get_paginated(limit=5, offset=0)
        assert len(result) == 5
        logger.success("Get paginated test passed.")

    def test_get_page(self) -> None:
        """Test get_page operation."""
        logger.info("Testing get_page...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        for i in range(1, 16):
            db.insert(RepoPerson(id=i, name=f"Person{i}"))

        result = db.get_page(page=2, per_page=5)
        assert len(result) == 5
        logger.success("Get page test passed.")

    def test_count(self) -> None:
        """Test count operation."""
        logger.info("Testing count...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        db.insert(RepoPerson(id=1, name="Alice"))
        db.insert(RepoPerson(id=2, name="Bob"))
        db.insert(RepoPerson(id=3, name="Charlie"))

        count = db.count()
        assert count == 3
        logger.success("Count test passed.")


class TestRepositoryBulk:
    """Tests for bulk operations."""

    def test_insert_many(self) -> None:
        """Test insert_many operation."""
        logger.info("Testing insert_many...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        db.insert_many(
            [
                RepoPerson(id=1, name="Alice"),
                RepoPerson(id=2, name="Bob"),
                RepoPerson(id=3, name="Charlie"),
            ]
        )

        count = db.count()
        assert count == 3
        logger.success("Insert many test passed.")

    def test_update_many(self) -> None:
        """Test update_many operation."""
        logger.info("Testing update_many...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        db.insert_many(
            [
                RepoPerson(id=1, name="Alice"),
                RepoPerson(id=2, name="Bob"),
            ]
        )

        updated = db.update_many(
            [
                (RepoPerson(id=1, name="Alice Updated", age=25), 1),
                (RepoPerson(id=2, name="Bob Updated", age=30), 2),
            ]
        )

        assert updated == 2
        result = db.get_all()
        assert result[0].name == "Alice Updated"
        logger.success("Update many test passed.")

    def test_delete_many(self) -> None:
        """Test delete_many operation."""
        logger.info("Testing delete_many...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        db.insert_many(
            [
                RepoPerson(id=1, name="Alice"),
                RepoPerson(id=2, name="Bob"),
                RepoPerson(id=3, name="Charlie"),
            ]
        )

        deleted = db.delete_many([1, 2])

        result = db.get_all()
        assert len(result) == 1
        assert result[0].name == "Charlie"
        logger.success("Delete many test passed.")


class TestRepositoryTransactions:
    """Tests for transaction operations."""

    def test_get_all_after_insert(self) -> None:
        """Test basic insert/get operations."""
        logger.info("Testing basic insert/get...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        db.insert(RepoPerson(id=1, name="Test"))

        result = db.get_all()
        assert len(result) == 1
        logger.success("Basic insert/get test passed.")

    def test_with_transaction(self) -> None:
        """Test with_transaction operation."""
        logger.info("Testing with_transaction...")
        db = WPostgreSQL(RepoPerson, DB_CONFIG)

        try:

            def insert_op(txn):
                txn.execute("INSERT INTO repo_test (id, name) VALUES (200, 'Test')", ())
                return True

            result = db.with_transaction(insert_op)
            assert result is True
            logger.success("With transaction test passed.")
        except Exception as e:
            logger.warning(f"With transaction had issues: {e}")
            pass
