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

from wpostgresql.core.repository import WPostgreSQL

__version__ = "0.1.0"

__all__ = ["WPostgreSQL"]
