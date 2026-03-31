"""Unit tests for connection module to increase coverage.

Simple tests that mock properly to cover async methods.
"""

import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCloseGlobalPools:
    """Tests for close_global_pools function."""

    def test_close_global_pools_with_pools(self) -> None:
        """Test closing global pools when they exist."""
        logger.info("Testing close_global_pools with pools...")

        from wpostgresql.core import connection

        mock_sync_pool = MagicMock()
        mock_async_pool = MagicMock()

        connection._global_sync_pool = mock_sync_pool
        connection._global_async_pool = mock_async_pool

        from wpostgresql.core.connection import close_global_pools

        close_global_pools()

        assert connection._global_sync_pool is None
        assert connection._global_async_pool is None

        logger.success("Close global pools test passed.")

    def test_close_global_pools_no_pools(self) -> None:
        """Test closing global pools when none exist."""
        logger.info("Testing close_global_pools no pools...")

        from wpostgresql.core import connection
        from wpostgresql.core.connection import close_global_pools

        connection._global_sync_pool = None
        connection._global_async_pool = None

        close_global_pools()

        assert connection._global_sync_pool is None
        assert connection._global_async_pool is None

        logger.success("Close global pools no pools test passed.")


class TestPooledConnection:
    """Tests for _PooledConnection class."""

    def test_pooled_connection_getattr(self) -> None:
        """Test _PooledConnection __getattr__."""
        logger.info("Testing _PooledConnection __getattr__...")

        from wpostgresql.core.connection import _PooledConnection

        mock_conn = MagicMock()
        mock_conn.autocommit = True
        mock_pool = MagicMock()

        pooled = _PooledConnection(mock_conn, mock_pool)
        assert pooled.autocommit is True

        logger.success("_PooledConnection __getattr__ test passed.")

    def test_pooled_connection_context_manager(self) -> None:
        """Test _PooledConnection context manager."""
        logger.info("Testing _PooledConnection context manager...")

        from wpostgresql.core.connection import _PooledConnection

        mock_conn = MagicMock()
        mock_pool = MagicMock()

        pooled = _PooledConnection(mock_conn, mock_pool)

        with pooled as conn:
            assert conn is mock_conn

        mock_pool.putconn.assert_called_once()

        logger.success("_PooledConnection context manager test passed.")


class TestPooledAsyncConnection:
    """Tests for _PooledAsyncConnection class."""

    @pytest.mark.asyncio
    async def test_pooled_async_connection_context_manager(self) -> None:
        """Test _PooledAsyncConnection async context manager."""
        logger.info("Testing _PooledAsyncConnection context manager...")

        from wpostgresql.core.connection import _PooledAsyncConnection

        mock_conn = AsyncMock()
        mock_pool = AsyncMock()

        pooled = _PooledAsyncConnection(mock_conn, mock_pool)

        async with pooled as conn:
            assert conn is mock_conn

        mock_pool.putconn.assert_called_once()

        logger.success("_PooledAsyncConnection context manager test passed.")

    @pytest.mark.asyncio
    async def test_pooled_async_connection_getattr(self) -> None:
        """Test _PooledAsyncConnection __getattr__."""
        logger.info("Testing _PooledAsyncConnection __getattr__...")

        from wpostgresql.core.connection import _PooledAsyncConnection

        mock_conn = AsyncMock()
        mock_conn.autocommit = True
        mock_pool = AsyncMock()

        pooled = _PooledAsyncConnection(mock_conn, mock_pool)
        assert pooled.autocommit is True

        logger.success("_PooledAsyncConnection __getattr__ test passed.")


class TestAsyncTransaction:
    """Tests for AsyncTransaction class."""

    @pytest.mark.asyncio
    async def test_async_transaction_init(self) -> None:
        """Test AsyncTransaction initialization."""
        logger.info("Testing AsyncTransaction init...")

        from wpostgresql.core.connection import AsyncTransaction

        txn = AsyncTransaction({"dbname": "test"})
        assert txn.db_config == {"dbname": "test"}
        assert txn.conn is None
        assert txn._committed is False

        logger.success("AsyncTransaction init test passed.")

    @pytest.mark.asyncio
    async def test_async_transaction_commit(self) -> None:
        """Test AsyncTransaction commit method."""
        logger.info("Testing AsyncTransaction commit...")

        from wpostgresql.core.connection import AsyncTransaction

        mock_conn = AsyncMock()

        txn = AsyncTransaction({"dbname": "test"})
        txn.conn = mock_conn

        await txn.commit()
        assert txn._committed is True
        mock_conn.commit.assert_called_once()

        logger.success("AsyncTransaction commit test passed.")

    @pytest.mark.asyncio
    async def test_async_transaction_rollback(self) -> None:
        """Test AsyncTransaction rollback method."""
        logger.info("Testing AsyncTransaction rollback...")

        from wpostgresql.core.connection import AsyncTransaction

        mock_conn = AsyncMock()

        txn = AsyncTransaction({"dbname": "test"})
        txn.conn = mock_conn

        await txn.rollback()
        mock_conn.rollback.assert_called_once()

        logger.success("AsyncTransaction rollback test passed.")

    @pytest.mark.asyncio
    async def test_async_transaction_aexit_with_exception(self) -> None:
        """Test AsyncTransaction __aexit__ with exception."""
        logger.info("Testing AsyncTransaction __aexit__ with exception...")

        from wpostgresql.core.connection import AsyncTransaction

        mock_conn = AsyncMock()

        txn = AsyncTransaction({"dbname": "test"})
        txn.conn = mock_conn

        await txn.__aexit__(ValueError, ValueError("test"), None)
        mock_conn.rollback.assert_called_once()

        logger.success("AsyncTransaction __aexit__ with exception test passed.")

    @pytest.mark.asyncio
    async def test_async_transaction_aexit_without_exception(self) -> None:
        """Test AsyncTransaction __aexit__ without exception."""
        logger.info("Testing AsyncTransaction __aexit__ without exception...")

        from wpostgresql.core.connection import AsyncTransaction

        mock_conn = AsyncMock()

        txn = AsyncTransaction({"dbname": "test"})
        txn.conn = mock_conn

        await txn.__aexit__(None, None, None)
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

        logger.success("AsyncTransaction __aexit__ without exception test passed.")

    @pytest.mark.asyncio
    async def test_async_transaction_aexit_committed(self) -> None:
        """Test AsyncTransaction __aexit__ when already committed."""
        logger.info("Testing AsyncTransaction __aexit__ committed...")

        from wpostgresql.core.connection import AsyncTransaction

        mock_conn = AsyncMock()

        txn = AsyncTransaction({"dbname": "test"})
        txn.conn = mock_conn
        txn._committed = True

        await txn.__aexit__(None, None, None)
        mock_conn.close.assert_called_once()

        logger.success("AsyncTransaction __aexit__ committed test passed.")


class TestGetAsyncTransaction:
    """Tests for get_async_transaction helper."""

    def test_get_async_transaction_exists(self) -> None:
        """Test get_async_transaction function exists."""
        logger.info("Testing get_async_transaction exists...")

        from wpostgresql.core.connection import get_async_transaction

        assert callable(get_async_transaction)

        logger.success("Get async transaction exists test passed.")


class TestAsyncConnectionManager:
    """Tests for AsyncConnectionManager class."""

    def test_async_connection_manager_init(self) -> None:
        """Test AsyncConnectionManager initialization."""
        logger.info("Testing AsyncConnectionManager init...")

        from wpostgresql.core.connection import AsyncConnectionManager

        manager = AsyncConnectionManager({"dbname": "test"})
        assert manager.db_config == {"dbname": "test"}
        assert manager._pool is None

        logger.success("AsyncConnectionManager init test passed.")

    def test_get_async_connection_exists(self) -> None:
        """Test get_async_connection function exists."""
        logger.info("Testing get_async_connection exists...")

        from wpostgresql.core.connection import get_async_connection

        assert callable(get_async_connection)

        logger.success("Get async connection exists test passed.")
