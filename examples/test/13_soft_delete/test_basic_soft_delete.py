import pytest
from pydantic import BaseModel

from examples.test.conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL
from wpostgresql.core.connection import get_connection


class SoftDeletePerson(BaseModel):
    id: int
    name: str
    age: int
    deleted_at: str = None
    is_deleted: bool = False


@pytest.fixture(autouse=True)
def setup():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS person_soft")
            cursor.execute(
                """
                CREATE TABLE person_soft (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    deleted_at TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT FALSE
                )
                """
            )
        conn.commit()
    yield
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS person_soft")
        conn.commit()


def test_soft_delete_marks_record():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO person_soft (name, age) VALUES (%s, %s)", ("Alice", 30))
            cursor.execute("INSERT INTO person_soft (name, age) VALUES (%s, %s)", ("Bob", 25))
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE person_soft SET deleted_at = CURRENT_TIMESTAMP, is_deleted = TRUE WHERE name = %s",
                ("Bob",),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT is_deleted FROM person_soft WHERE name = %s", ("Bob",))
            result = cursor.fetchone()

    assert result[0] is True


def test_get_active_records_excludes_deleted():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO person_soft (name, age) VALUES (%s, %s)", ("Alice", 30))
            cursor.execute("INSERT INTO person_soft (name, age) VALUES (%s, %s)", ("Bob", 25))
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE person_soft SET deleted_at = CURRENT_TIMESTAMP, is_deleted = TRUE WHERE name = %s",
                ("Bob",),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM person_soft WHERE is_deleted = FALSE")
            rows = cursor.fetchall()

    assert len(rows) == 1
    assert rows[0][1] == "Alice"


def test_restore_soft_deleted_record():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO person_soft (name, age) VALUES (%s, %s)", ("Bob", 25))
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE person_soft SET deleted_at = CURRENT_TIMESTAMP, is_deleted = TRUE WHERE name = %s",
                ("Bob",),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE person_soft SET deleted_at = NULL, is_deleted = FALSE WHERE name = %s",
                ("Bob",),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT is_deleted FROM person_soft WHERE name = %s", ("Bob",))
            result = cursor.fetchone()

    assert result[0] is False


def test_hard_delete_removes_record():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO person_soft (name, age) VALUES (%s, %s)", ("Alice", 30))
            cursor.execute("INSERT INTO person_soft (name, age) VALUES (%s, %s)", ("Bob", 25))
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM person_soft WHERE name = %s", ("Bob",))
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM person_soft")
            result = cursor.fetchone()

    assert result[0] == 1
