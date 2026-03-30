"""Connection management for PostgreSQL."""

import psycopg2
from psycopg2 import pool


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
