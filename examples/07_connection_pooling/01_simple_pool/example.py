"""Connection Pooling Example using WPostgreSQL.

wpostgresql uses automatic connection pooling by default.
This example shows:
1. Automatic pooling (default - no config needed)
2. Manual pool configuration (optional)
3. Pool cleanup
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
    name: str
    age: int


def example_automatic_pooling():
    """Automatic pooling - NO configuration needed.

    All WPostgreSQL operations use a global pool automatically.
    Connections are reused across all operations.
    """
    print("=== Automatic Pooling (Default) ===")

    db = WPostgreSQL(Person, db_config)
    try:
        db._sync.drop_table()
    except Exception:
        pass
    db = WPostgreSQL(Person, db_config)

    # All operations use the pool automatically
    for i in range(10):
        db.insert(Person(name=f"Person {i}", age=20 + i))

    people = db.get_all()
    print(f"Inserted and retrieved {len(people)} people")

    # Pool is shared across all WPostgreSQL instances
    db2 = WPostgreSQL(Person, db_config)
    print(f"Total people: {db2.count()}")


def example_manual_pool():
    """Manual pool configuration - for advanced use cases."""
    print("\n=== Manual Pool Configuration ===")

    # Create custom pool manager
    pool = ConnectionManager(db_config, min_connections=2, max_connections=20)
    conn = pool.get_connection()
    print("Obtained pooled connection successfully!")
    pool.release_connection(conn)
    pool.close_all()


def example_cleanup():
    """Clean up global pools when done."""
    print("\n=== Cleanup ===")
    close_global_pools()
    print("Global pools closed")


if __name__ == "__main__":
    example_automatic_pooling()
    example_manual_pool()
    example_cleanup()
