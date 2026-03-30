"""Soft delete examples."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from wpostgresql import WPostgreSQL
from wpostgresql.core.connection import get_connection

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "port": 5432,
    "host": "localhost",
}


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at: Optional[datetime] = None
    is_deleted: bool = False


class Person(BaseModel):
    id: int
    name: str
    age: int
    deleted_at: Optional[datetime] = None
    is_deleted: bool = False


db = WPostgreSQL(Person, db_config)


def create_table_with_soft_delete():
    """Create table with soft delete columns."""
    query = """
    CREATE TABLE IF NOT EXISTS person_soft (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        deleted_at TIMESTAMP,
        is_deleted BOOLEAN DEFAULT FALSE
    )
    """
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
        conn.commit()


def soft_delete(table_name: str, record_id: int):
    """Soft delete a record (marks as deleted without removing)."""
    query = f"""
    UPDATE {table_name}
    SET deleted_at = CURRENT_TIMESTAMP, is_deleted = TRUE
    WHERE id = %s
    """
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (record_id,))
        conn.commit()


def restore(table_name: str, record_id: int):
    """Restore a soft-deleted record."""
    query = f"""
    UPDATE {table_name}
    SET deleted_at = NULL, is_deleted = FALSE
    WHERE id = %s
    """
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (record_id,))
        conn.commit()


def hard_delete(table_name: str, record_id: int):
    """Permanently delete a record."""
    query = f"DELETE FROM {table_name} WHERE id = %s"
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (record_id,))
        conn.commit()


def get_active(table_name: str) -> list:
    """Get all active (non-deleted) records."""
    query = f"SELECT * FROM {table_name} WHERE is_deleted = FALSE"
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def get_deleted(table_name: str) -> list:
    """Get all soft-deleted records."""
    query = f"SELECT * FROM {table_name} WHERE is_deleted = TRUE"
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


# Run example
create_table_with_soft_delete()

# Insert records
with get_connection(db_config) as conn:
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO person_soft (name, age) VALUES (%s, %s)", ("Alice", 30))
        cursor.execute("INSERT INTO person_soft (name, age) VALUES (%s, %s)", ("Bob", 25))
        cursor.execute("INSERT INTO person_soft (name, age) VALUES (%s, %s)", ("Charlie", 35))
    conn.commit()

print("Initial records:")
for row in get_active("person_soft"):
    print(f"  {row}")

# Soft delete Bob
print("\nSoft deleting Bob:")
soft_delete("person_soft", 2)

print("Active records:")
for row in get_active("person_soft"):
    print(f"  {row}")

print("Deleted records:")
for row in get_deleted("person_soft"):
    print(f"  {row}")

# Restore Bob
print("\nRestoring Bob:")
restore("person_soft", 2)

print("Active records after restore:")
for row in get_active("person_soft"):
    print(f"  {row}")

# Hard delete Charlie
print("\nHard deleting Charlie:")
hard_delete("person_soft", 3)

print("Final records:")
for row in get_active("person_soft"):
    print(f"  {row}")
