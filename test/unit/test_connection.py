"""Tests for connection module.

This module contains unit tests for ConnectionManager, Transaction, and
helper functions in the wpostgresql.core.connection module.
"""


from unittest.mock import MagicMock, Mock, patch

import pytest
from loguru import logger

from wpostgresql.core.connection import ConnectionManager, Transaction, get_transaction


class TestConnectionManager:
    """Tests for ConnectionManager class.

    This class groups tests that verify the pooling logic and context
    management of ConnectionManager.
    """

    def test_init_default(self) -> None:
        """Test initialization with defaults.

        Ensures that min and max connections have the expected default values.
        """
        logger.info("Testing ConnectionManager default initialization...")
        cm = ConnectionManager({"dbname": "test"})
        assert cm.min_connections == 1
        assert cm.max_connections == 10
        logger.success("Default initialization test passed.")

    def test_init_custom_pool_size(self) -> None:
        """Test initialization with custom pool size.

        Ensures that custom pool boundaries are correctly applied.
        """
        logger.info("Testing ConnectionManager custom initialization...")
        cm = ConnectionManager({"dbname": "test"}, min_connections=2, max_connections=20)
        assert cm.min_connections == 2
        assert cm.max_connections == 20
        logger.success("Custom initialization test passed.")

    @patch("wpostgresql.core.connection.ConnectionPool")
    def test_get_connection_creates_pool(self, mock_pool_class: Mock) -> None:
        """Test get_connection creates pool if not exists.

        Args:
            mock_pool_class: Mocked ConnectionPool class.
        """
        logger.info("Testing pool creation on first connection...")
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool

        cm = ConnectionManager({"dbname": "test"})
        conn = cm.get_connection()

        mock_pool_class.assert_called_once()
        assert conn == mock_conn
        logger.success("Pool creation test passed.")

    @patch("wpostgresql.core.connection.ConnectionPool")
    def test_get_connection_reuses_pool(self, mock_pool_class: Mock) -> None:
        """Test get_connection reuses existing pool.

        Args:
            mock_pool_class: Mocked ConnectionPool class.
        """
        logger.info("Testing pool reuse on subsequent connections...")
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool

        cm = ConnectionManager({"dbname": "test"})
        cm.get_connection()
        cm.get_connection()

        assert mock_pool_class.call_count == 1
        logger.success("Pool reuse test passed.")

    def test_release_connection(self) -> None:
        """Test releasing connection back to pool.

        Verifies that release_connection calls putconn on the underlying pool.
        """
        logger.info("Testing connection release...")
        cm = ConnectionManager({"dbname": "test"})
        # pylint: disable=protected-access
        cm._pool = MagicMock()
        mock_conn = MagicMock()

        cm.release_connection(mock_conn)

        cm._pool.putconn.assert_called_once_with(mock_conn)
        logger.success("Connection release test passed.")

    def test_close_all(self) -> None:
        """Test closing all connections.

        Verifies that close_all closes the pool and resets it to None.
        """
        logger.info("Testing close_all functionality...")
        cm = ConnectionManager({"dbname": "test"})
        mock_pool = MagicMock()
        # pylint: disable=protected-access
        cm._pool = mock_pool

        cm.close_all()

        mock_pool.close.assert_called_once()
        assert cm._pool is None
        logger.success("close_all test passed.")

    def test_context_manager(self) -> None:
        """Test ConnectionManager as context manager.

        Ensures that entering the context returns the manager and exiting
        closes the pool.
        """
        logger.info("Testing ConnectionManager context manager...")
        cm = ConnectionManager({"dbname": "test"})
        mock_pool = MagicMock()
        # pylint: disable=protected-access
        cm._pool = mock_pool

        with cm as connection:
            assert connection is cm

        mock_pool.close.assert_called_once()
        logger.success("Context manager test passed.")

    def test_context_manager_close_all(self) -> None:
        """Test ConnectionManager __exit__ calls close_all.

        Verifies that exiting the 'with' block triggers a cleanup.
        """
        logger.info("Testing ConnectionManager __exit__ cleanup...")
        cm = ConnectionManager({"dbname": "test"})
        mock_pool = MagicMock()
        # pylint: disable=protected-access
        cm._pool = mock_pool

        with cm:
            pass

        mock_pool.close.assert_called_once()
        logger.success("__exit__ cleanup test passed.")


class TestTransaction:
    """Tests for Transaction class.

    This class groups tests that verify transaction lifecycle, including
    automatic commits, rollbacks, and query execution.
    """

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_transaction_context_commit(self, mock_connect: Mock) -> None:
        """Test transaction commits on successful exit.

        Args:
            mock_connect: Mocked psycopg.connect function.
        """
        logger.info("Testing transaction commit on success...")
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with Transaction({"dbname": "test"}):
            pass

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        logger.success("Transaction commit test passed.")

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_transaction_context_rollback_on_exception(self, mock_connect: Mock) -> None:
        """Test transaction rolls back on exception.

        Args:
            mock_connect: Mocked psycopg.connect function.
        """
        logger.info("Testing transaction rollback on exception...")
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with pytest.raises(ValueError, match="Test error"):
            with Transaction({"dbname": "test"}):
                raise ValueError("Test error")

        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()
        logger.success("Transaction rollback test passed.")

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_manual_commit(self, mock_connect: Mock) -> None:
        """Test manual commit.

        Args:
            mock_connect: Mocked psycopg.connect function.
        """
        logger.info("Testing manual commit...")
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with Transaction({"dbname": "test"}) as txn:
            txn.commit()

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
        logger.success("Manual commit test passed.")

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_manual_rollback(self, mock_connect: Mock) -> None:
        """Test manual rollback.

        Args:
            mock_connect: Mocked psycopg.connect function.
        """
        logger.info("Testing manual rollback...")
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with Transaction({"dbname": "test"}) as txn:
            txn.rollback()

        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()
        logger.success("Manual rollback test passed.")

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_execute_query(self, mock_connect: Mock) -> None:
        """Test executing query within transaction.

        Args:
            mock_connect: Mocked psycopg.connect function.
        """
        logger.info("Testing query execution within transaction...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("value",)]
        mock_cursor.description = [("col",)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        with Transaction({"dbname": "test"}) as txn:
            result = txn.execute("SELECT * FROM users", ())

        mock_cursor.execute.assert_called_once_with("SELECT * FROM users", ())
        assert result == [("value",)]
        logger.success("Query execution test passed.")

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_execute_without_result(self, mock_connect: Mock) -> None:
        """Test executing query without result.

        Args:
            mock_connect: Mocked psycopg.connect function.
        """
        logger.info("Testing query execution without result (INSERT)...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = None
        mock_cursor.rowcount = 0
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        with Transaction({"dbname": "test"}) as txn:
            result = txn.execute("INSERT INTO users VALUES (1)", ())

        mock_cursor.execute.assert_called_once()
        assert result == 0
        logger.success("Query execution without result test passed.")


class TestGetTransaction:
    """Tests for get_transaction helper.

    Verifies that the helper correctly returns a Transaction instance.
    """

    @patch("wpostgresql.core.connection.Transaction")
    def test_get_transaction(self, mock_transaction_class: Mock) -> None:
        """Test get_transaction returns Transaction context manager.

        Args:
            mock_transaction_class: Mocked Transaction class.
        """
        logger.info("Testing get_transaction helper...")
        mock_txn = MagicMock()
        mock_transaction_class.return_value = mock_txn

        with get_transaction({"dbname": "test"}) as txn:
            assert txn == mock_txn

        mock_transaction_class.assert_called_once_with({"dbname": "test"})
        logger.success("get_transaction helper test passed.")
