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
"""

from wpostgresql.builders import QueryBuilder
from wpostgresql.core.connection import ConnectionManager, Transaction, get_transaction
from wpostgresql.core.repository import WPostgreSQL
from wpostgresql.core.sync import TableSync
from wpostgresql.exceptions import (
    ConnectionError,
    OperationError,
    SQLInjectionError,
    TableSyncError,
    TransactionError,
    ValidationError,
    WPostgreSQLError,
)

__version__ = "0.2.0"

__all__ = [
    "WPostgreSQL",
    "QueryBuilder",
    "ConnectionManager",
    "Transaction",
    "get_transaction",
    "TableSync",
    "WPostgreSQLError",
    "ConnectionError",
    "TableSyncError",
    "ValidationError",
    "OperationError",
    "SQLInjectionError",
    "TransactionError",
]
