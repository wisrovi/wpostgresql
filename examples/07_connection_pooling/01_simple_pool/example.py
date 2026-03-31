"""
Connection Pooling Example

wpostgresql now uses automatic connection pooling by default.
This example shows:
1. Automatic pooling (default - no config needed)
2. Manual pool configuration (optional)
"""

from pydantic import BaseModel

from wpostgresql import WPostgreSQL
from wpostgresql.core.connection import ConnectionManager, close_global_pools

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Person(BaseModel):
    id: int
    name: str
    age: int


def example_automatic_pooling():
    """Automatic pooling - NO configuration needed.

    All WPostgreSQL operations now use a global pool automatically.
    Connections are reused across all operations.
    """
    print("=== Automatic Pooling (Default) ===")

    # No need to configure pool - it's automatic!
    db = WPostgreSQL(Person, db_config)

    # All operations use the pool automatically
    for i in range(10):
        db.insert(Person(id=i, name=f"Person {i}", age=20 + i))

    people = db.get_all()
    print(f"Inserted and retrieved {len(people)} people")

    # Pool is shared across all WPostgreSQL instances
    db2 = WPostgreSQL(Person, db_config)
    print(f"Total people: {db2.count()}")


def example_manual_pool():
    """Manual pool configuration - for advanced use cases."""
    print("\n=== Manual Pool Configuration ===")

    # Create custom pool with specific settings
    pool = ConnectionManager(db_config, min_connections=2, max_connections=20)

    # Use pool directly
    conn = pool.get_connection()
    print(f"Got connection: {conn}")

    pool.release_connection(conn)
    pool.close_all()


def example_cleanup():
    """Clean up global pools when done."""
    print("\n=== Cleanup ===")

    # Close global pools (usually done at app shutdown)
    close_global_pools()
    print("Global pools closed")


if __name__ == "__main__":
    example_automatic_pooling()
    example_manual_pool()
    example_cleanup()
