"""Integration tests for connection pool and transactions.

Tests that require a real database connection to verify pool behavior
and transaction management work correctly.
"""

import os
import sys
from collections.abc import Generator

import pytest
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import DB_CONFIG, cleanup_table

from wpostgresql import ConnectionManager, Transaction


@pytest.fixture(autouse=True)
def setup_teardown() -> Generator[None, None, None]:
    """Fixture to clean up tables before and after each test."""
    logger.info("Setting up connection test environment...")
    cleanup_table("conn_test")
    yield
    logger.info("Tearing down connection test environment...")
    cleanup_table("conn_test")


class TestConnectionPool:
    """Tests for connection pool behavior."""

    def test_connection_pool_get_connection(self) -> None:
        """Test getting connection from pool."""
        logger.info("Testing connection pool get connection...")

        manager = ConnectionManager(DB_CONFIG)
        conn = manager.get_connection()
        assert conn is not None
        manager.release_connection(conn)
        logger.success("Connection pool test passed.")

    def test_connection_pool_context_manager(self) -> None:
        """Test connection as context manager."""
        logger.info("Testing connection context manager...")

        manager = ConnectionManager(DB_CONFIG)
        with manager as conn:
            assert conn is not None
        logger.success("Context manager test passed.")

    def test_connection_pool_close_all(self) -> None:
        """Test closing all connections."""
        logger.info("Testing close all connections...")

        manager = ConnectionManager(DB_CONFIG)
        manager.get_connection()
        manager.close_all()
        logger.success("Close all test passed.")


class TestTransaction:
    """Tests for transaction management."""

    def test_transaction_commit(self) -> None:
        """Test transaction commit."""
        logger.info("Testing transaction commit...")

        with Transaction(DB_CONFIG) as txn:
            txn.execute("CREATE TABLE IF NOT EXISTS conn_test (id INT, name TEXT)")
            txn.execute("INSERT INTO conn_test VALUES (1, 'test')")
            txn.commit()

        logger.success("Transaction commit test passed.")

    def test_transaction_rollback(self) -> None:
        """Test transaction rollback."""
        logger.info("Testing transaction rollback...")

        try:
            with Transaction(DB_CONFIG) as txn:
                txn.execute("INSERT INTO conn_test VALUES (2, 'test2')")
                raise Exception("Force rollback")
        except Exception:
            pass

        logger.success("Transaction rollback test passed.")

    def test_transaction_execute_with_result(self) -> None:
        """Test execute query with result."""
        logger.info("Testing execute with result...")

        with Transaction(DB_CONFIG) as txn:
            txn.execute("SELECT 1 as result", ())
        logger.success("Execute with result test passed.")


class TestGetTransaction:
    """Tests for get_transaction helper."""

    pass
