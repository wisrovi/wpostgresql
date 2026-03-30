"""Automatic timestamps example."""

import time
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from wpostgresql import WPostgreSQL
from wpostgresql.core.connection import get_connection


class TimestampedModel(BaseModel):
    """Base model with automatic timestamps."""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class Person(BaseModel):
    id: int
    name: str
    age: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


db = WPostgreSQL(Person, db_config)

# Insert with automatic timestamps
person = Person(id=1, name="Alice", age=30)
db.insert(person)

# Get and display
results = db.get_by_field(id=1)
print("After insert:")
print(f"  created_at: {results[0].created_at}")
print(f"  updated_at: {results[0].updated_at}")

time.sleep(1)

# Update - we need to manually update the timestamp
updated_person = Person(
    id=1, name="Alice Smith", age=31, created_at=results[0].created_at, updated_at=datetime.now()
)
db.update(1, updated_person)

# Get updated
results = db.get_by_field(id=1)
print("\nAfter update:")
print(f"  name: {results[0].name}")
print(f"  age: {results[0].age}")
print(f"  created_at: {results[0].created_at}")
print(f"  updated_at: {results[0].updated_at}")


# Using raw SQL for automatic timestamps
def create_table_with_timestamps(table_name: str):
    """Create table with automatic timestamps."""
    query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
        conn.commit()


def update_with_timestamp(table_name: str, record_id: int, **kwargs):
    """Update record with automatic timestamp."""
    set_clauses = [f"{k} = %s" for k in kwargs.keys()]
    set_clauses.append("updated_at = CURRENT_TIMESTAMP")

    query = f"""
    UPDATE {table_name}
    SET {", ".join(set_clauses)}
    WHERE id = %s
    """
    values = tuple(kwargs.values()) + (record_id,)

    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, values)
        conn.commit()


# Example with auto timestamps
create_table_with_timestamps("person_auto")

with get_connection(db_config) as conn:
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO person_auto (name, age) VALUES (%s, %s) RETURNING id, created_at",
            ("Bob", 25),
        )
        result = cursor.fetchone()
        print(f"\nInserted: id={result[0]}, created_at={result[1]}")
    conn.commit()

update_with_timestamp("person_auto", 1, name="Bob Smith", age=26)

with get_connection(db_config) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name, age, created_at, updated_at FROM person_auto WHERE id = 1")
        row = cursor.fetchone()
        print(
            f"Updated: id={row[0]}, name={row[1]}, age={row[2]}, created_at={row[3]}, updated_at={row[4]}"
        )
