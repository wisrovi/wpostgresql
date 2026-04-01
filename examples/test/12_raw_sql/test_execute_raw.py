import pytest
from pydantic import BaseModel

from examples.test.conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL
from wpostgresql.core.connection import get_connection


class Person(BaseModel):
    id: int
    name: str
    age: int


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("person")
    yield
    cleanup_table("person")


def test_raw_sql_select():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Alice", age=30))
    db.insert(Person(id=2, name="Bob", age=25))

    with get_connection(DB_CONFIG) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM person")
        rows = cursor.fetchall()

    assert len(rows) == 2


def test_raw_sql_insert_returning():
    WPostgreSQL(Person, DB_CONFIG)

    with get_connection(DB_CONFIG) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM person")
        next_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO person (id, name, age) VALUES (%s, %s, %s) RETURNING id, name",
            (next_id, "Charlie", 35),
        )
        result = cursor.fetchone()
        conn.commit()

    assert result[0] is not None
    assert result[1] == "Charlie"


def test_raw_sql_update_returning():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Alice", age=30))

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE person SET age = %s WHERE name = %s RETURNING id, name, age",
                (31, "Alice"),
            )
            result = cursor.fetchone()
        conn.commit()

    assert result[2] == 31


def test_raw_sql_delete_returning():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Alice", age=30))
    db.insert(Person(id=2, name="Bob", age=25))

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM person WHERE name = %s RETURNING id, name", ("Bob",))
            result = cursor.fetchone()
        conn.commit()

    assert result[1] == "Bob"

    result = db.get_all()
    assert len(result) == 1


def test_raw_sql_with_parameters():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Alice", age=30))
    db.insert(Person(id=2, name="Bob", age=25))

    with get_connection(DB_CONFIG) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM person WHERE age > %s", (26,))
        rows = cursor.fetchall()

    assert len(rows) == 1
    assert rows[0][2] == 30
