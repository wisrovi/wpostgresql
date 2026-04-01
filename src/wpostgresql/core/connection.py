"""Connection management for PostgreSQL with automatic connection pooling."""

import logging
import threading
from collections.abc import Generator
from contextlib import contextmanager, suppress
from typing import Any, Optional

import psycopg
from psycopg import AsyncConnection, Connection
from psycopg_pool import AsyncConnectionPool, ConnectionPool

logger = logging.getLogger(__name__)

_global_pool_lock = threading.Lock()
# pylint: disable=invalid-name
_global_sync_pool: Optional[ConnectionPool] = None
# pylint: disable=invalid-name
_global_async_pool: Optional[AsyncConnectionPool] = None
DEFAULT_POOL_CONFIG = {"min_size": 5, "max_size": 50}


def _build_conninfo(db_config: dict) -> str:
    """Build connection string from config dict.

    Args:
        db_config: Dictionary containing database connection parameters.

    Returns:
        str: A PostgreSQL connection string (conninfo).
    """
    parts = []
    for key, value in db_config.items():
        if key == "port":
            parts.append(f"port={value}")
        elif key == "dbname":
            parts.append(f"dbname={value}")
        else:
            parts.append(f"{key}={value}")
    return " ".join(parts)


def _get_global_sync_pool(db_config: dict, pool_config: Optional[dict] = None) -> ConnectionPool:
    """Get or create global sync connection pool.

    Args:
        db_config: Dictionary containing database connection parameters.
        pool_config: Optional pool configuration dictionary.

    Returns:
        ConnectionPool: The global synchronous connection pool.
    """
    # pylint: disable=global-statement
    global _global_sync_pool

    config = pool_config or DEFAULT_POOL_CONFIG
    conninfo = _build_conninfo(db_config)

    with _global_pool_lock:
        if _global_sync_pool is None:
            _global_sync_pool = ConnectionPool(
                conninfo,
                min_size=config.get("min_size", DEFAULT_POOL_CONFIG["min_size"]),
                max_size=config.get("max_size", DEFAULT_POOL_CONFIG["max_size"]),
            )
            logger.info("Created global sync pool with config: %s", config)
        return _global_sync_pool


def configure_pool(
    db_config: dict,
    min_size: int = 2,
    max_size: int = 20,
) -> None:
    """Configure global connection pool settings.

    Call this function BEFORE creating any WPostgreSQL instances to set
    custom pool sizes. This is useful for high-concurrency scenarios.

    Args:
        db_config: Database configuration dictionary.
        min_size: Minimum number of connections in the pool.
        max_size: Maximum number of connections in the pool.

    Example:
        from wpostgresql import configure_pool, WPostgreSQL

        configure_pool(db_config, min_size=10, max_size=100)
        db = WPostgreSQL(Model, db_config)
    """
    # pylint: disable=global-statement
    global _global_sync_pool, _global_async_pool

    conninfo = _build_conninfo(db_config)

    with _global_pool_lock:
        if _global_sync_pool is not None:
            _global_sync_pool.close()
        _global_sync_pool = ConnectionPool(
            conninfo,
            min_size=min_size,
            max_size=max_size,
        )
        logger.info("Configured sync pool: min=%d, max=%d", min_size, max_size)

        # Reset async pool to None - it will be recreated on first async use
        # with the new configuration
        _global_async_pool = None
        logger.info("Reset async pool for reconfiguration: min=%d, max=%d", min_size, max_size)
        logger.info("Configured sync pool: min=%d, max=%d", min_size, max_size)

        if _global_async_pool is not None:
            with suppress(Exception):
                _global_async_pool.close()
        _global_async_pool = None
        # Store config for later async pool creation
        _configured_pool = {"db_config": db_config, "min_size": min_size, "max_size": max_size}
        logger.info("Reset async pool for reconfiguration: min=%d, max=%d", min_size, max_size)
        logger.info("Configured sync pool: min=%d, max=%d", min_size, max_size)

        if _global_async_pool is not None:
            with suppress(Exception):
                _global_async_pool.close()
        # Reset async pool to None so it will be recreated with new config
        # when first accessed in an async context
        _global_async_pool = None
        logger.info("Reset async pool for reconfiguration: min=%d, max=%d", min_size, max_size)


def _get_global_async_pool(
    db_config: dict, pool_config: Optional[dict] = None
) -> AsyncConnectionPool:
    """Get or create global async connection pool.

    Args:
        db_config: Dictionary containing database connection parameters.
        pool_config: Optional pool configuration dictionary.

    Returns:
        AsyncConnectionPool: The global asynchronous connection pool.
    """
    # pylint: disable=global-statement
    global _global_async_pool

    config = pool_config or DEFAULT_POOL_CONFIG
    conninfo = _build_conninfo(db_config)

    with _global_pool_lock:
        if _global_async_pool is None:
            _global_async_pool = AsyncConnectionPool(
                conninfo,
                min_size=config.get("min_size", DEFAULT_POOL_CONFIG["min_size"]),
                max_size=config.get("max_size", DEFAULT_POOL_CONFIG["max_size"]),
                open=False,  # Will be opened lazily in get_async_connection
            )
            logger.info(
                "Created global async pool with config: %s (will open on first use)", config
            )
        return _global_async_pool


def close_global_pools() -> None:
    """Close global connection pools.

    Resets the global sync and async pools to None after closing them.
    """
    # pylint: disable=global-statement
    global _global_sync_pool, _global_async_pool

    with _global_pool_lock:
        if _global_sync_pool:
            _global_sync_pool.close()
            _global_sync_pool = None
        if _global_async_pool:
            _global_async_pool.close()
            _global_async_pool = None
        logger.info("Global connection pools closed")


class _PooledConnection:
    """Wrapper for pooled connection that returns to pool on close.

    Attributes:
        _conn: The underlying psycopg connection.
        _pool: The pool to which the connection belongs.
    """

    def __init__(self, conn: Connection, pool: ConnectionPool):
        """Initialize the pooled connection wrapper."""
        self._conn = conn
        self._pool = pool

    def __enter__(self) -> Connection:
        """Enter the context and return the connection."""
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context, rolling back if necessary and returning the connection to the pool."""
        if self._conn and not self._conn.closed:
            if not self._conn.info.transaction_status:
                pass  # Already idle
            else:
                self._conn.rollback()  # Rollback uncommitted transactions
        self._pool.putconn(self._conn)

    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to the underlying connection."""
        return getattr(self._conn, name)


class _PooledAsyncConnection:
    """Wrapper for pooled async connection that returns to pool on close.

    Attributes:
        _conn: The underlying psycopg async connection.
        _pool: The pool to which the connection belongs.
    """

    def __init__(self, conn: AsyncConnection, pool: AsyncConnectionPool):
        """Initialize the pooled async connection wrapper."""
        self._conn = conn
        self._pool = pool

    async def __aenter__(self) -> AsyncConnection:
        """Enter the async context and return the connection."""
        return self._conn

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context and return the connection to the pool."""
        await self._pool.putconn(self._conn)

    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to the underlying connection."""
        return getattr(self._conn, name)


class Transaction:
    """Context manager for database transactions (sync).

    Handles automatic commit on success and rollback on error.
    """

    def __init__(self, db_config: dict):
        """Initialize transaction with database configuration."""
        self.db_config = db_config
        self.conn: Optional[Connection] = None
        self._committed = False

    def __enter__(self) -> "Transaction":
        """Start a new connection and begin a transaction."""
        self.conn = psycopg.connect(**self.db_config)
        self.conn.autocommit = False
        logger.debug("Transaction started")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Commit or rollback based on whether an exception occurred."""
        if exc_type is not None:
            self.conn.rollback()
            logger.debug("Transaction rolled back")
        elif not self._committed:
            self.conn.commit()
            logger.debug("Transaction committed")
        self.conn.close()
        return False

    def commit(self) -> None:
        """Manually commit the transaction."""
        self.conn.commit()
        self._committed = True

    def rollback(self) -> None:
        """Manually rollback the transaction."""
        self.conn.rollback()

    def execute(self, query: str, values: Optional[tuple[Any, ...]] = None) -> Any:
        """Execute a query within the transaction.

        Args:
            query: The SQL query to execute.
            values: Optional parameters for the query.

        Returns:
            Any: The result of the query (fetchall or rowcount).
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            if cursor.description:
                return cursor.fetchall()
            return cursor.rowcount


class AsyncTransaction:
    """Context manager for database transactions (async).

    Handles automatic commit on success and rollback on error asynchronously.
    """

    def __init__(self, db_config: dict):
        """Initialize async transaction with database configuration."""
        self.db_config = db_config
        self.conn: Optional[AsyncConnection] = None
        self._committed = False

    async def __aenter__(self) -> "AsyncTransaction":
        """Start a new async connection and begin a transaction."""
        self.conn = await psycopg.AsyncConnection.connect(**self.db_config)
        self.conn.autocommit = False
        logger.debug("Async transaction started")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Asynchronously commit or rollback based on exceptions."""
        if exc_type is not None:
            await self.conn.rollback()
            logger.debug("Async transaction rolled back")
        elif not self._committed:
            await self.conn.commit()
            logger.debug("Async transaction committed")
        await self.conn.close()
        return False

    async def commit(self) -> None:
        """Manually commit the async transaction."""
        await self.conn.commit()
        self._committed = True

    async def rollback(self) -> None:
        """Manually rollback the async transaction."""
        await self.conn.rollback()

    async def execute(self, query: str, values: Optional[tuple[Any, ...]] = None) -> Any:
        """Execute an async query within the transaction.

        Args:
            query: The SQL query to execute.
            values: Optional parameters for the query.

        Returns:
            Any: The result of the query.
        """
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, values)
            if cursor.description:
                return await cursor.fetchall()
            return cursor.rowcount


@contextmanager
def get_transaction(db_config: dict) -> Generator[Transaction, None, None]:
    """Get a transaction context manager (sync).

    Args:
        db_config: Database configuration dictionary.

    Yields:
        Transaction: An active transaction instance.
    """
    transaction = Transaction(db_config)
    yield transaction


@contextmanager
async def get_async_transaction(db_config: dict) -> Generator[AsyncTransaction, None, None]:
    """Get an async transaction context manager.

    Args:
        db_config: Database configuration dictionary.

    Yields:
        AsyncTransaction: An active async transaction instance.
    """
    transaction = AsyncTransaction(db_config)
    async with transaction:
        yield transaction


class ConnectionManager:
    """Manages PostgreSQL database connections (sync) with local pooling."""

    def __init__(self, db_config: dict, min_connections: int = 1, max_connections: int = 10):
        """Initialize the connection manager with pool settings."""
        self.db_config = db_config
        self.min_connections = min_connections
        self.max_connections = max_connections
        self._pool: Optional[ConnectionPool] = None

    def get_connection(self) -> Connection:
        """Get a connection from the local pool.

        Returns:
            Connection: A psycopg connection.
        """
        if self._pool is None:
            conninfo = _build_conninfo(self.db_config)
            self._pool = ConnectionPool(
                conninfo,
                min_size=self.min_connections,
                max_size=self.max_connections,
            )
        return self._pool.getconn()

    def release_connection(self, conn: Connection) -> None:
        """Return a connection to the pool.

        Args:
            conn: The connection to release.
        """
        if self._pool:
            self._pool.putconn(conn)

    def close_all(self) -> None:
        """Close the local connection pool."""
        if self._pool:
            self._pool.close()
            self._pool = None

    def __enter__(self) -> "ConnectionManager":
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager and close all connections."""
        self.close_all()


class AsyncConnectionManager:
    """Manages PostgreSQL database connections (async) with local pooling."""

    def __init__(self, db_config: dict, min_connections: int = 1, max_connections: int = 10):
        """Initialize the async connection manager with pool settings."""
        self.db_config = db_config
        self.min_connections = min_connections
        self.max_connections = max_connections
        self._pool: Optional[AsyncConnectionPool] = None

    async def get_connection(self) -> AsyncConnection:
        """Asynchronously get a connection from the local pool.

        Returns:
            AsyncConnection: A psycopg async connection.
        """
        if self._pool is None:
            conninfo = _build_conninfo(self.db_config)
            self._pool = AsyncConnectionPool(
                conninfo,
                min_size=self.min_connections,
                max_size=self.max_connections,
            )
        return await self._pool.getconn()

    async def release_connection(self, conn: AsyncConnection) -> None:
        """Asynchronously return a connection to the pool.

        Args:
            conn: The async connection to release.
        """
        if self._pool:
            await self._pool.putconn(conn)

    async def close_all(self) -> None:
        """Asynchronously close the local connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def __aenter__(self) -> "AsyncConnectionManager":
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager and close all connections."""
        await self.close_all()


def get_connection(db_config: dict, pool_config: Optional[dict] = None) -> _PooledConnection:
    """Get a connection from global pool (sync). Uses connection pooling automatically.

    Returns a context manager that automatically returns the connection to the pool.

    Usage:
        with get_connection(config) as conn:
            conn.execute(...)

    Args:
        db_config: Database configuration dictionary.
        pool_config: Optional pool configuration dictionary.

    Returns:
        _PooledConnection: A wrapper around a pooled connection.
    """
    pool = _get_global_sync_pool(db_config, pool_config)
    conn = pool.getconn()
    return _PooledConnection(conn, pool)


async def get_async_connection(
    db_config: dict, pool_config: Optional[dict] = None
) -> _PooledAsyncConnection:
    """Get a connection from global pool (async). Uses connection pooling automatically.

    Returns an async context manager that automatically returns the connection to the pool.

    Usage:
        async with get_async_connection(config) as conn:
            await conn.execute(...)

    Args:
        db_config: Database configuration dictionary.
        pool_config: Optional pool configuration dictionary.

    Returns:
        _PooledAsyncConnection: A wrapper around a pooled async connection.
    """
    pool = _get_global_async_pool(db_config, pool_config)
    # Open pool lazily if needed (psycopg_pool 3.x requires open() before use)
    try:
        conn = await pool.getconn()
    except Exception:
        # Pool not yet open, open it now
        await pool.open()
        conn = await pool.getconn()
    return _PooledAsyncConnection(conn, pool)
