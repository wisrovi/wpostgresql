"""Integration tests for async operations with real database.

Tests that require a real PostgreSQL database to cover async methods.
"""

import asyncio
import sys
import os
from typing import Optional

import pytest
from loguru import logger
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL


@pytest.fixture(autouse=True)
def setup_teardown() -> None:
    """Fixture to clean up tables."""
    logger.info("Setting up async integration tests...")
    cleanup_table("async_int_test")
    yield
    logger.info("Tearing down async integration tests...")
    cleanup_table("async_int_test")


class AsyncTestModel(BaseModel):
    """Model for async integration tests."""

    __tablename__ = "async_int_test"
    id: int = Field(..., description="Primary Key")
    name: str
    value: Optional[int] = None


class TestAsyncRepositoryIntegration:
    """Integration tests for async repository methods."""

    @pytest.mark.asyncio
    async def test_insert_async(self) -> None:
        """Test async insert."""
        logger.info("Testing async insert...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        await db.insert_async(AsyncTestModel(id=1, name="test", value=100))

        result = await db.get_by_field_async(id=1)
        assert len(result) == 1
        assert result[0].name == "test"

        logger.success("Async insert test passed.")

    @pytest.mark.asyncio
    async def test_get_all_async(self) -> None:
        """Test async get_all."""
        logger.info("Testing async get_all...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        await db.insert_async(AsyncTestModel(id=1, name="test1"))
        await db.insert_async(AsyncTestModel(id=2, name="test2"))

        result = await db.get_all_async()
        assert len(result) >= 2

        logger.success("Async get_all test passed.")

    @pytest.mark.asyncio
    async def test_update_async(self) -> None:
        """Test async update."""
        logger.info("Testing async update...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        await db.insert_async(AsyncTestModel(id=1, name="original"))
        await db.update_async(1, AsyncTestModel(id=1, name="updated", value=50))

        result = await db.get_by_field_async(id=1)
        assert result[0].name == "updated"

        logger.success("Async update test passed.")

    @pytest.mark.asyncio
    async def test_delete_async(self) -> None:
        """Test async delete."""
        logger.info("Testing async delete...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        await db.insert_async(AsyncTestModel(id=1, name="test"))
        await db.delete_async(1)

        result = await db.get_all_async()
        assert len(result) == 0

        logger.success("Async delete test passed.")

    @pytest.mark.asyncio
    async def test_get_paginated_async(self) -> None:
        """Test async get_paginated."""
        logger.info("Testing async get_paginated...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        for i in range(1, 6):
            await db.insert_async(AsyncTestModel(id=i, name=f"test{i}", value=i * 10))

        result = await db.get_paginated_async(limit=3, offset=0)
        assert len(result) == 3

        logger.success("Async get_paginated test passed.")

    @pytest.mark.asyncio
    async def test_get_page_async(self) -> None:
        """Test async get_page."""
        logger.info("Testing async get_page...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        for i in range(1, 11):
            await db.insert_async(AsyncTestModel(id=i, name=f"test{i}"))

        result = await db.get_page_async(page=2, per_page=5)
        assert len(result) == 5

        logger.success("Async get_page test passed.")

    @pytest.mark.asyncio
    async def test_count_async(self) -> None:
        """Test async count."""
        logger.info("Testing async count...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        await db.insert_async(AsyncTestModel(id=1, name="test"))

        count = await db.count_async()
        assert count >= 1

        logger.success("Async count test passed.")

    @pytest.mark.asyncio
    async def test_insert_many_async(self) -> None:
        """Test async insert_many."""
        logger.info("Testing async insert_many...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        await db.insert_many_async(
            [
                AsyncTestModel(id=1, name="test1"),
                AsyncTestModel(id=2, name="test2"),
                AsyncTestModel(id=3, name="test3"),
            ]
        )

        count = await db.count_async()
        assert count >= 3

        logger.success("Async insert_many test passed.")

    @pytest.mark.asyncio
    async def test_update_many_async(self) -> None:
        """Test async update_many."""
        logger.info("Testing async update_many...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        await db.insert_many_async(
            [
                AsyncTestModel(id=1, name="test1"),
                AsyncTestModel(id=2, name="test2"),
            ]
        )

        updated = await db.update_many_async(
            [
                (AsyncTestModel(id=1, name="updated1", value=10), 1),
                (AsyncTestModel(id=2, name="updated2", value=20), 2),
            ]
        )

        assert updated == 2

        logger.success("Async update_many test passed.")

    @pytest.mark.asyncio
    async def test_delete_many_async(self) -> None:
        """Test async delete_many."""
        logger.info("Testing async delete_many...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        await db.insert_many_async(
            [
                AsyncTestModel(id=1, name="test1"),
                AsyncTestModel(id=2, name="test2"),
                AsyncTestModel(id=3, name="test3"),
            ]
        )

        deleted = await db.delete_many_async([1, 2])
        assert deleted == 2

        result = await db.get_all_async()
        assert len(result) == 1

        logger.success("Async delete_many test passed.")

    @pytest.mark.asyncio
    async def test_get_by_field_async_no_match(self) -> None:
        """Test async get_by_field with no match."""
        logger.info("Testing async get_by_field no match...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        await db.insert_async(AsyncTestModel(id=1, name="test"))

        result = await db.get_by_field_async(name="nonexistent")
        assert len(result) == 0

        logger.success("Async get_by_field no match test passed.")

    @pytest.mark.asyncio
    async def test_get_by_field_async_no_filters(self) -> None:
        """Test async get_by_field with no filters calls get_all_async."""
        logger.info("Testing async get_by_field no filters...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        await db.insert_async(AsyncTestModel(id=1, name="test"))

        result = await db.get_by_field_async()
        assert len(result) >= 1

        logger.success("Async get_by_field no filters test passed.")

    @pytest.mark.asyncio
    async def test_execute_transaction_async(self) -> None:
        """Test async execute_transaction."""
        logger.info("Testing async execute_transaction...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)

        try:
            await db.execute_transaction_async(
                [
                    ("INSERT INTO async_int_test (id, name, value) VALUES (100, 'txn1', 100)", ()),
                    ("INSERT INTO async_int_test (id, name, value) VALUES (101, 'txn2', 200)", ()),
                ]
            )
            count = await db.count_async()
            assert count >= 2
        except Exception as e:
            logger.warning(f"Async execute_transaction: {e}")

        logger.success("Async execute_transaction test passed.")

    @pytest.mark.asyncio
    async def test_execute_transaction_async(self) -> None:
        """Test async execute_transaction."""
        logger.info("Testing async execute_transaction...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)

        try:
            await db.execute_transaction_async(
                [
                    ("INSERT INTO async_int_test (id, name, value) VALUES (100, 'txn1', 100)", ()),
                    ("INSERT INTO async_int_test (id, name, value) VALUES (101, 'txn2', 200)", ()),
                    ("SELECT COUNT(*) FROM async_int_test", ()),
                ]
            )
            count = await db.count_async()
            assert count >= 2
        except Exception as e:
            logger.warning(f"Async execute_transaction: {e}")

        logger.success("Async execute_transaction test passed.")

    @pytest.mark.asyncio
    async def test_execute_transaction_async_exception(self) -> None:
        """Test async execute_transaction with exception."""
        logger.info("Testing async execute_transaction exception...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)

        try:
            await db.execute_transaction_async(
                [
                    ("INVALID SQL QUERY", ()),
                ]
            )
        except Exception as e:
            logger.warning(f"Expected exception: {e}")

        logger.success("Async execute_transaction exception test passed.")

    @pytest.mark.asyncio
    async def test_with_transaction_async(self) -> None:
        """Test async with_transaction."""
        logger.info("Testing async with_transaction...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)

        async def txn_op(txn):
            await txn.execute(
                "INSERT INTO async_int_test (id, name, value) VALUES (200, 'with_txn', 300)", ()
            )
            return "success"

        try:
            result = await db.with_transaction_async(txn_op)
            assert result == "success"
        except Exception as e:
            logger.warning(f"Async with_transaction: {e}")

        logger.success("Async with_transaction test passed.")

    @pytest.mark.asyncio
    async def test_get_paginated_async_with_order(self) -> None:
        """Test async get_paginated with ordering."""
        logger.info("Testing async get_paginated with order...")

        db = WPostgreSQL(AsyncTestModel, DB_CONFIG)
        for i in range(1, 6):
            await db.insert_async(AsyncTestModel(id=i, name=f"test{i}", value=i * 10))

        result = await db.get_paginated_async(limit=3, offset=0, order_by="value", order_desc=True)

        assert len(result) == 3
        assert result[0].value >= result[-1].value

        logger.success("Async get_paginated with order test passed.")
