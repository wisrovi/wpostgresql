import pytest
from pydantic import BaseModel

from examples.test.conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL
from wpostgresql.core.connection import get_connection


class Person(BaseModel):
    id: int
    name: str
    age: int
    salary: float


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("person")
    yield
    cleanup_table("person")


def test_count_aggregation():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Alice", age=30, salary=5000))
    db.insert(Person(id=2, name="Bob", age=25, salary=4000))
    db.insert(Person(id=3, name="Charlie", age=35, salary=6000))

    query = "SELECT COUNT(*) as cnt FROM person"
    with get_connection(DB_CONFIG) as conn, conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    assert result[0] == 3


def test_sum_aggregation():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Alice", age=30, salary=5000))
    db.insert(Person(id=2, name="Bob", age=25, salary=4000))

    query = "SELECT SUM(salary::numeric) as total FROM person"
    with get_connection(DB_CONFIG) as conn, conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    assert result[0] == 9000


def test_avg_aggregation():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Alice", age=30, salary=5000))
    db.insert(Person(id=2, name="Bob", age=25, salary=4000))

    query = "SELECT AVG(salary::numeric) as avg_salary FROM person"
    with get_connection(DB_CONFIG) as conn, conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    assert result[0] == 4500


def test_min_max_aggregation():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Alice", age=30, salary=5000))
    db.insert(Person(id=2, name="Bob", age=25, salary=4000))

    with get_connection(DB_CONFIG) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT MIN(age), MAX(age) FROM person")
        result = cursor.fetchone()
    assert result[0] == 25
    assert result[1] == 30
