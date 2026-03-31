import pytest
from datetime import datetime
from pydantic import BaseModel, Field

from examples.test.conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL
from wpostgresql.core.connection import get_connection


class TimestampedPerson(BaseModel):
    id: int
    name: str
    age: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = None


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("person_timestamp")
    yield
    cleanup_table("person_timestamp")


def test_auto_timestamp_on_insert():
    db = WPostgreSQL(TimestampedPerson, DB_CONFIG)

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS person_timestamp (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO person_timestamp (name, age) VALUES (%s, %s) RETURNING id, created_at",
                ("Alice", 30),
            )
            result = cursor.fetchone()
        conn.commit()

    assert result[0] is not None
    assert result[1] is not None


def test_update_timestamp():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS person_timestamp (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute("INSERT INTO person_timestamp (name, age) VALUES (%s, %s)", ("Bob", 25))
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE person_timestamp SET name = %s, updated_at = CURRENT_TIMESTAMP WHERE name = %s",
                ("Bob Smith", "Bob"),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT name, updated_at FROM person_timestamp WHERE name = %s", ("Bob Smith",)
            )
            result = cursor.fetchone()

    assert result[0] == "Bob Smith"
    assert result[1] is not None
