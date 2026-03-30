import pytest
from pydantic import BaseModel

from examples.test.conftest import DB_CONFIG
from wpostgresql.core.connection import get_connection


class Address(BaseModel):
    id: int
    person_id: int
    street: str
    city: str
    country: str


class Person(BaseModel):
    id: int
    name: str
    age: int


@pytest.fixture(autouse=True)
def setup():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS address CASCADE")
            cursor.execute("DROP TABLE IF EXISTS person CASCADE")

            cursor.execute("""
                CREATE TABLE person (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER
                )
            """)

            cursor.execute("""
                CREATE TABLE address (
                    id SERIAL PRIMARY KEY,
                    person_id INTEGER REFERENCES person(id) ON DELETE CASCADE,
                    street TEXT NOT NULL,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL
                )
            """)
        conn.commit()
    yield
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS address CASCADE")
            cursor.execute("DROP TABLE IF EXISTS person CASCADE")
        conn.commit()


def test_insert_person_with_addresses():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO person (name, age) VALUES (%s, %s)", ("Alice", 30))
            cursor.execute("SELECT lastval()")
            person_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO address (person_id, street, city, country) VALUES (%s, %s, %s, %s)",
                (person_id, "123 Main St", "New York", "USA"),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM address WHERE person_id = %s", (person_id,))
            count = cursor.fetchone()[0]

    assert count == 1


def test_get_person_addresses():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO person (name, age) VALUES (%s, %s)", ("Bob", 25))
            cursor.execute("SELECT lastval()")
            person_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO address (person_id, street, city, country) VALUES (%s, %s, %s, %s)",
                (person_id, "456 Oak Ave", "Los Angeles", "USA"),
            )
            cursor.execute(
                "INSERT INTO address (person_id, street, city, country) VALUES (%s, %s, %s, %s)",
                (person_id, "789 Pine Rd", "San Francisco", "USA"),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM address WHERE person_id = %s", (person_id,))
            addresses = cursor.fetchall()

    assert len(addresses) == 2


def test_cascade_delete_addresses():
    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO person (name, age) VALUES (%s, %s)", ("Charlie", 35))
            cursor.execute("SELECT lastval()")
            person_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO address (person_id, street, city, country) VALUES (%s, %s, %s, %s)",
                (person_id, "123 Main St", "New York", "USA"),
            )
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM person WHERE id = %s", (person_id,))
        conn.commit()

    with get_connection(DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM address WHERE person_id = %s", (person_id,))
            count = cursor.fetchone()[0]

    assert count == 0
