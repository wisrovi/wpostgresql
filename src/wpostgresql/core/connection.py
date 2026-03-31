"""Connection management for PostgreSQL with automatic connection pooling."""

import logging
import threading
from contextlib import contextmanager
from typing import Any, Optional

import psycopg
from psycopg import AsyncConnection, Connection
from psycopg.connection_async import AsyncConnection as AsyncConnClass
from psycopg_pool import AsyncConnectionPool, ConnectionPool

logger = logging.getLogger(__name__)

_global_pool_lock = threading.Lock()
_global_sync_pool: Optional[ConnectionPool] = None
_global_async_pool: Optional[AsyncConnectionPool] = None
_default_pool_config = {"min_size": 2, "max_size": 20}


def _build_conninfo(db_config: dict) -> str:
    """Build connection string from config dict."""
    parts = []
    for key, value in db_config.items():
        if key == "port":
            parts.append(f"port={value}")
        elif key == "dbname":
            parts.append(f"dbname={value}")
        else:
            parts.append(f"{key}={value}")
    return " ".join(parts)


def _get_global_sync_pool(db_config: dict) -> ConnectionPool:
    """Get or create global sync connection pool."""
    global _global_sync_pool

    conninfo = _build_conninfo(db_config)

    with _global_pool_lock:
        if _global_sync_pool is None:
            _global_sync_pool = ConnectionPool(
                conninfo,
                min_size=_default_pool_config["min_size"],
                max_size=_default_pool_config["max_size"],
            )
            logger.info(f"Created global sync pool")
        return _global_sync_pool


def _get_global_async_pool(db_config: dict) -> AsyncConnectionPool:
    """Get or create global async connection pool."""
    global _global_async_pool

    conninfo = _build_conninfo(db_config)

    with _global_pool_lock:
        if _global_async_pool is None:
            _global_async_pool = AsyncConnectionPool(
                conninfo,
                min_size=_default_pool_config["min_size"],
                max_size=_default_pool_config["max_size"],
            )
            logger.info(f"Created global async pool")
        return _global_async_pool


def close_global_pools():
    """Close global connection pools."""
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
    """Wrapper for pooled connection that returns to pool on close."""

    def __init__(self, conn: Connection, pool: ConnectionPool):
        self._conn = conn
        self._pool = pool

    def __enter__(self):
        return self._conn

    def __exit__(self, *args):
        if self._conn and not self._conn.closed:
            if not self._conn.info.transaction_status:
                pass  # Already idle
            else:
                self._conn.rollback()  # Rollback uncommitted transactions
        self._pool.putconn(self._conn)

    def __getattr__(self, name):
        return getattr(self._conn, name)


class _PooledAsyncConnection:
    """Wrapper for pooled async connection that returns to pool on close."""

    def __init__(self, conn: AsyncConnection, pool: AsyncConnectionPool):
        self._conn = conn
        self._pool = pool

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, *args):
        await self._pool.putconn(self._conn)

    def __getattr__(self, name):
        return getattr(self._conn, name)


class Transaction:
    """Context manager for database transactions (sync)."""

    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.conn: Optional[Connection] = None
        self._committed = False

    def __enter__(self):
        self.conn = psycopg.connect(**self.db_config)
        self.conn.autocommit = False
        logger.debug("Transaction started")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
            logger.debug("Transaction rolled back")
        elif not self._committed:
            self.conn.commit()
            logger.debug("Transaction committed")
        self.conn.close()
        return False

    def commit(self):
        self.conn.commit()
        self._committed = True

    def rollback(self):
        self.conn.rollback()

    def execute(self, query: str, values: tuple = None) -> Any:
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            if cursor.description:
                return cursor.fetchall()
            return cursor.rowcount


class AsyncTransaction:
    """Context manager for database transactions (async)."""

    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.conn: Optional[AsyncConnection] = None
        self._committed = False

    async def __aenter__(self):
        self.conn = await psycopg.AsyncConnection.connect(**self.db_config)
        self.conn.autocommit = False
        logger.debug("Async transaction started")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.conn.rollback()
            logger.debug("Async transaction rolled back")
        elif not self._committed:
            await self.conn.commit()
            logger.debug("Async transaction committed")
        await self.conn.close()
        return False

    async def commit(self):
        await self.conn.commit()
        self._committed = True

    async def rollback(self):
        await self.conn.rollback()

    async def execute(self, query: str, values: tuple = None) -> Any:
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, values)
            if cursor.description:
                return await cursor.fetchall()
            return cursor.rowcount


@contextmanager
def get_transaction(db_config: dict):
    """Get a transaction context manager (sync)."""
    transaction = Transaction(db_config)
    yield transaction


@contextmanager
async def get_async_transaction(db_config: dict):
    """Get an async transaction context manager."""
    transaction = AsyncTransaction(db_config)
    async with transaction:
        yield transaction


class ConnectionManager:
    """Manages PostgreSQL database connections (sync)."""

    def __init__(self, db_config: dict, min_connections: int = 1, max_connections: int = 10):
        self.db_config = db_config
        self.min_connections = min_connections
        self.max_connections = max_connections
        self._pool: Optional[ConnectionPool] = None

    def get_connection(self) -> Connection:
        if self._pool is None:
            conninfo = _build_conninfo(self.db_config)
            self._pool = ConnectionPool(
                conninfo,
                min_size=self.min_connections,
                max_size=self.max_connections,
            )
        return self._pool.getconn()

    def release_connection(self, conn: Connection):
        if self._pool:
            self._pool.putconn(conn)

    def close_all(self):
        if self._pool:
            self._pool.close()
            self._pool = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()


class AsyncConnectionManager:
    """Manages PostgreSQL database connections (async)."""

    def __init__(self, db_config: dict, min_connections: int = 1, max_connections: int = 10):
        self.db_config = db_config
        self.min_connections = min_connections
        self.max_connections = max_connections
        self._pool: Optional[AsyncConnectionPool] = None

    async def get_connection(self) -> AsyncConnection:
        if self._pool is None:
            conninfo = _build_conninfo(self.db_config)
            self._pool = AsyncConnectionPool(
                conninfo,
                min_size=self.min_connections,
                max_size=self.max_connections,
            )
        return await self._pool.getconn()

    async def release_connection(self, conn: AsyncConnection):
        if self._pool:
            await self._pool.putconn(conn)

    async def close_all(self):
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_all()


def get_connection(db_config: dict) -> _PooledConnection:
    """Get a connection from global pool (sync). Uses connection pooling automatically.

    Returns a context manager that automatically returns the connection to the pool.

    Usage:
        with get_connection(config) as conn:
            conn.execute(...)
    """
    pool = _get_global_sync_pool(db_config)
    conn = pool.getconn()
    return _PooledConnection(conn, pool)


async def get_async_connection(db_config: dict) -> _PooledAsyncConnection:
    """Get a connection from global pool (async). Uses connection pooling automatically.

    Returns an async context manager that automatically returns the connection to the pool.

    Usage:
        async with get_async_connection(config) as conn:
            await conn.execute(...)
    """
    pool = _get_global_async_pool(db_config)
    conn = await pool.getconn()
    return _PooledAsyncConnection(conn, pool)
