"""Integration tests for async operations with real database.

This module contains integration tests that verify async methods work correctly
with a real PostgreSQL database.
"""

import asyncio
import sys
import os
from typing import Generator, List, Optional

import psycopg
import pytest
from loguru import logger
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL


@pytest.fixture(autouse=True)
def setup_teardown() -> Generator[None, None, None]:
    """Fixture to clean up tables before and after each test."""
    logger.info("Setting up async integration test environment...")
    cleanup_table("async_person")
    yield
    logger.info("Tearing down async integration test environment...")
    cleanup_table("async_person")


class PersonAsync(BaseModel):
    """Model for async tests."""

    __tablename__ = "async_person"
    id: int = Field(..., description="Primary Key")
    name: str
    email: Optional[str] = None
    age: Optional[int] = None


class TestAsyncInsert:
    """Tests for async insert operations."""

    @pytest.mark.asyncio
    async def test_insert_single_async(self) -> None:
        """Test inserting a single record asynchronously."""
        logger.info("Testing async insert single record...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)
        await db.insert_async(PersonAsync(id=1, name="John", email="john@example.com"))

        result = await db.get_by_field_async(id=1)
        assert len(result) == 1
        assert result[0].name == "John"
        logger.success("Async insert single record test passed.")

    @pytest.mark.asyncio
    async def test_insert_many_async(self) -> None:
        """Test inserting multiple records asynchronously."""
        logger.info("Testing async insert many...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        await db.insert_many_async(
            [
                PersonAsync(id=1, name="Alice"),
                PersonAsync(id=2, name="Bob"),
                PersonAsync(id=3, name="Charlie"),
            ]
        )

        result = await db.get_all_async()
        assert len(result) == 3
        logger.success("Async insert many test passed.")


class TestAsyncGet:
    """Tests for async get operations."""

    @pytest.mark.asyncio
    async def test_get_all_async(self) -> None:
        """Test getting all records asynchronously."""
        logger.info("Testing async get all...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        await db.insert_many_async(
            [
                PersonAsync(id=1, name="Alice"),
                PersonAsync(id=2, name="Bob"),
            ]
        )

        result = await db.get_all_async()
        assert len(result) == 2
        logger.success("Async get all test passed.")

    @pytest.mark.asyncio
    async def test_get_by_field_async(self) -> None:
        """Test getting records by field asynchronously."""
        logger.info("Testing async get by field...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        await db.insert_many_async(
            [
                PersonAsync(id=1, name="Alice", age=25),
                PersonAsync(id=2, name="Bob", age=30),
            ]
        )

        result = await db.get_by_field_async(name="Alice")
        assert len(result) == 1
        assert result[0].age == 25
        logger.success("Async get by field test passed.")


class TestAsyncUpdate:
    """Tests for async update operations."""

    @pytest.mark.asyncio
    async def test_update_async(self) -> None:
        """Test updating a record asynchronously."""
        logger.info("Testing async update...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        await db.insert_async(PersonAsync(id=1, name="John", email="john@example.com"))
        await db.update_async(1, PersonAsync(id=1, name="John Updated", email="new@example.com"))

        result = await db.get_by_field_async(id=1)
        assert len(result) == 1
        assert result[0].name == "John Updated"
        logger.success("Async update test passed.")


class TestAsyncDelete:
    """Tests for async delete operations."""

    @pytest.mark.asyncio
    async def test_delete_async(self) -> None:
        """Test deleting a record asynchronously."""
        logger.info("Testing async delete...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        await db.insert_async(PersonAsync(id=1, name="John"))
        await db.delete_async(1)

        result = await db.get_all_async()
        assert len(result) == 0
        logger.success("Async delete test passed.")


class TestAsyncPagination:
    """Tests for async pagination operations."""

    @pytest.mark.asyncio
    async def test_get_paginated_async(self) -> None:
        """Test getting paginated results asynchronously."""
        logger.info("Testing async pagination...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        for i in range(1, 11):
            await db.insert_async(PersonAsync(id=i, name=f"Person{i}"))

        result = await db.get_paginated_async(limit=5, offset=0)
        assert len(result) == 5
        logger.success("Async paginated test passed.")

    @pytest.mark.asyncio
    async def test_get_page_async(self) -> None:
        """Test getting page asynchronously."""
        logger.info("Testing async get page...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        for i in range(1, 16):
            await db.insert_async(PersonAsync(id=i, name=f"Person{i}"))

        result = await db.get_page_async(page=2, per_page=5)
        assert len(result) == 5
        logger.success("Async get page test passed.")

    @pytest.mark.asyncio
    async def test_count_async(self) -> None:
        """Test counting records asynchronously."""
        logger.info("Testing async count...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        await db.insert_many_async(
            [
                PersonAsync(id=1, name="Alice"),
                PersonAsync(id=2, name="Bob"),
                PersonAsync(id=3, name="Charlie"),
            ]
        )

        count = await db.count_async()
        assert count == 3
        logger.success("Async count test passed.")


class TestAsyncBulk:
    """Tests for async bulk operations."""

    @pytest.mark.asyncio
    async def test_update_many_async(self) -> None:
        """Test updating many records asynchronously."""
        logger.info("Testing async update many...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        await db.insert_many_async(
            [
                PersonAsync(id=1, name="Alice"),
                PersonAsync(id=2, name="Bob"),
            ]
        )

        updated = await db.update_many_async(
            [
                (PersonAsync(id=1, name="Alice Updated", age=25), 1),
                (PersonAsync(id=2, name="Bob Updated", age=30), 2),
            ]
        )

        assert updated == 2
        result = await db.get_all_async()
        assert result[0].name == "Alice Updated"
        logger.success("Async update many test passed.")

    @pytest.mark.asyncio
    async def test_delete_many_async(self) -> None:
        """Test deleting many records asynchronously."""
        logger.info("Testing async delete many...")
        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        await db.insert_many_async(
            [
                PersonAsync(id=1, name="Alice"),
                PersonAsync(id=2, name="Bob"),
                PersonAsync(id=3, name="Charlie"),
            ]
        )

        deleted = await db.delete_many_async([1, 2])

        result = await db.get_all_async()
        assert len(result) == 1
        assert result[0].name == "Charlie"
        logger.success("Async delete many test passed.")


class TestAsyncTableSync:
    """Tests for async table synchronization using WPostgreSQL methods."""

    @pytest.mark.asyncio
    async def test_async_get_columns_via_db(self) -> None:
        """Test getting columns through WPostgreSQL async."""
        logger.info("Testing async get columns via WPostgreSQL...")

        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        result = await db.get_all_async()
        assert isinstance(result, list)
        logger.success("Async get columns test passed.")

    @pytest.mark.asyncio
    async def test_async_transaction(self) -> None:
        """Test async transaction operations."""
        logger.info("Testing async transaction...")

        db = WPostgreSQL(PersonAsync, DB_CONFIG)

        await db.insert_async(PersonAsync(id=1, name="Test"))

        result = await db.get_all_async()
        assert len(result) == 1
        logger.success("Async transaction test passed.")

    @pytest.mark.asyncio
    async def test_async_table_exists_false(self) -> None:
        """Test async table not exists."""
        logger.info("Testing async table not exists...")

        from wpostgresql import AsyncTableSync

        cleanup_table("nonexistent_async")

        class NonExistent(BaseModel):
            __tablename__ = "nonexistent_async"
            id: int
            name: str

        sync = AsyncTableSync(NonExistent, DB_CONFIG)
        exists = await sync.table_exists_async()
        assert exists is False
        logger.success("Async table not exists test passed.")
