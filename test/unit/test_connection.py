"""Tests for connection module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from wpostgresql.core.connection import ConnectionManager, Transaction, get_transaction


class TestConnectionManager:
    """Tests for ConnectionManager class."""

    def test_init_default(self):
        """Test initialization with defaults."""
        cm = ConnectionManager({"dbname": "test"})
        assert cm.min_connections == 1
        assert cm.max_connections == 10

    def test_init_custom_pool_size(self):
        """Test initialization with custom pool size."""
        cm = ConnectionManager({"dbname": "test"}, min_connections=2, max_connections=20)
        assert cm.min_connections == 2
        assert cm.max_connections == 20

    @patch("wpostgresql.core.connection.ConnectionPool")
    def test_get_connection_creates_pool(self, mock_pool_class):
        """Test get_connection creates pool if not exists."""
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool

        cm = ConnectionManager({"dbname": "test"})
        conn = cm.get_connection()

        mock_pool_class.assert_called_once()
        assert conn == mock_conn

    @patch("wpostgresql.core.connection.ConnectionPool")
    def test_get_connection_reuses_pool(self, mock_pool_class):
        """Test get_connection reuses existing pool."""
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        mock_pool_class.return_value = mock_pool

        cm = ConnectionManager({"dbname": "test"})
        cm.get_connection()
        cm.get_connection()

        assert mock_pool_class.call_count == 1

    def test_release_connection(self):
        """Test releasing connection back to pool."""
        cm = ConnectionManager({"dbname": "test"})
        cm._pool = MagicMock()
        mock_conn = MagicMock()

        cm.release_connection(mock_conn)

        cm._pool.putconn.assert_called_once_with(mock_conn)

    def test_close_all(self):
        """Test closing all connections."""
        cm = ConnectionManager({"dbname": "test"})
        mock_pool = MagicMock()
        cm._pool = mock_pool

        cm.close_all()

        mock_pool.close.assert_called_once()
        assert cm._pool is None

    def test_context_manager(self):
        """Test ConnectionManager as context manager."""
        cm = ConnectionManager({"dbname": "test"})
        mock_pool = MagicMock()
        cm._pool = mock_pool

        with cm as connection:
            assert connection is cm

        mock_pool.close.assert_called_once()

    def test_context_manager_close_all(self):
        """Test ConnectionManager __exit__ calls close_all."""
        cm = ConnectionManager({"dbname": "test"})
        mock_pool = MagicMock()
        cm._pool = mock_pool

        with cm:
            pass

        mock_pool.close.assert_called_once()


class TestTransaction:
    """Tests for Transaction class."""

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_transaction_context_commit(self, mock_connect):
        """Test transaction commits on successful exit."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with Transaction({"dbname": "test"}) as txn:
            pass

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_transaction_context_rollback_on_exception(self, mock_connect):
        """Test transaction rolls back on exception."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with pytest.raises(ValueError):
            with Transaction({"dbname": "test"}) as txn:
                raise ValueError("Test error")

        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_manual_commit(self, mock_connect):
        """Test manual commit."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with Transaction({"dbname": "test"}) as txn:
            txn.commit()

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_manual_rollback(self, mock_connect):
        """Test manual rollback."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with Transaction({"dbname": "test"}) as txn:
            txn.rollback()

        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_execute_query(self, mock_connect):
        """Test executing query within transaction."""
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

    @patch("wpostgresql.core.connection.psycopg.connect")
    def test_execute_without_result(self, mock_connect):
        """Test executing query without result."""
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


class TestGetTransaction:
    """Tests for get_transaction helper."""

    @patch("wpostgresql.core.connection.Transaction")
    def test_get_transaction(self, mock_transaction_class):
        """Test get_transaction returns Transaction context manager."""
        mock_txn = MagicMock()
        mock_transaction_class.return_value = mock_txn

        with get_transaction({"dbname": "test"}) as txn:
            assert txn == mock_txn

        mock_transaction_class.assert_called_once_with({"dbname": "test"})
