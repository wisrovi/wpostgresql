"""wpostgresql - PostgreSQL ORM using Pydantic models.

A simple and type-safe PostgreSQL ORM that uses Pydantic models
to define database schemas. Automatically handles table creation,
synchronization, and CRUD operations.

Usage:
    from wpostgresql import WPostgreSQL

    class User(BaseModel):
        id: int
        name: str
        email: str

    db = WPostgreSQL(User, db_config)
    db.insert(User(id=1, name="John", email="john@example.com"))

Async usage:
    db.insert_async(User(id=1, name="John", email="john@example.com"))
    users = await db.get_all_async()
"""

from wpostgresql.builders import QueryBuilder
from wpostgresql.core.connection import (
    AsyncConnectionManager,
    AsyncTransaction,
    ConnectionManager,
    Transaction,
    get_async_connection,
    get_async_transaction,
    get_connection,
    get_transaction,
)
from wpostgresql.core.repository import WPostgreSQL
from wpostgresql.core.sync import AsyncTableSync, TableSync
from wpostgresql.exceptions import (
    ConnectionError,
    OperationError,
    SQLInjectionError,
    TableSyncError,
    TransactionError,
    ValidationError,
    WPostgreSQLError,
)

__version__ = "0.3.0"

__all__ = [
    "WPostgreSQL",
    "QueryBuilder",
    "ConnectionManager",
    "AsyncConnectionManager",
    "Transaction",
    "AsyncTransaction",
    "get_connection",
    "get_async_connection",
    "get_transaction",
    "get_async_transaction",
    "TableSync",
    "AsyncTableSync",
    "WPostgreSQLError",
    "ConnectionError",
    "TableSyncError",
    "ValidationError",
    "OperationError",
    "SQLInjectionError",
    "TransactionError",
]
