"""Connection management for PostgreSQL."""

import logging
from contextlib import contextmanager
from typing import Any, Optional

import psycopg2
from psycopg2 import pool

logger = logging.getLogger(__name__)


class Transaction:
    """Context manager for database transactions."""

    def __init__(self, db_config: dict):
        """Initialize transaction.

        Args:
            db_config: PostgreSQL connection configuration.
        """
        self.db_config = db_config
        self.conn = None
        self._committed = False

    def __enter__(self):
        """Enter transaction context."""
        self.conn = psycopg2.connect(**self.db_config)
        self.conn.autocommit = False
        logger.debug("Transaction started")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context."""
        if exc_type is not None:
            self.conn.rollback()
            logger.debug("Transaction rolled back")
        elif not self._committed:
            self.conn.commit()
            logger.debug("Transaction committed")
        self.conn.close()
        return False

    def commit(self):
        """Commit the transaction."""
        self.conn.commit()
        self._committed = True
        logger.debug("Transaction committed")

    def rollback(self):
        """Rollback the transaction."""
        self.conn.rollback()
        logger.debug("Transaction rolled back")

    def execute(self, query: str, values: tuple = None) -> Any:
        """Execute a query within the transaction.

        Args:
            query: SQL query to execute.
            values: Query parameters.

        Returns:
            Query result if any.
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            if cursor.description:
                return cursor.fetchall()
            return cursor.rowcount


@contextmanager
def get_transaction(db_config: dict):
    """Get a transaction context manager.

    Args:
        db_config: PostgreSQL connection configuration.

    Yields:
        Transaction object.
    """
    transaction = Transaction(db_config)
    yield transaction


class ConnectionManager:
    """Manages PostgreSQL database connections."""

    def __init__(self, db_config: dict, min_connections: int = 1, max_connections: int = 10):
        """Initialize connection manager.

        Args:
            db_config: PostgreSQL connection configuration dictionary.
            min_connections: Minimum number of connections in the pool.
            max_connections: Maximum number of connections in the pool.
        """
        self.db_config = db_config
        self.min_connections = min_connections
        self.max_connections = max_connections
        self._pool = None

    def get_connection(self):
        """Get a connection from the pool.

        Returns:
            A psycopg2 connection object.
        """
        if self._pool is None:
            self._pool = pool.ThreadedConnectionPool(
                self.min_connections,
                self.max_connections,
                **self.db_config,
            )
        return self._pool.getconn()

    def release_connection(self, conn):
        """Release a connection back to the pool.

        Args:
            conn: The connection to release.
        """
        if self._pool:
            self._pool.putconn(conn)

    def close_all(self):
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            self._pool = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_all()


def get_connection(db_config: dict):
    """Get a simple database connection.

    Args:
        db_config: PostgreSQL connection configuration dictionary.

    Returns:
        A psycopg2 connection object.
    """
    return psycopg2.connect(**db_config)
