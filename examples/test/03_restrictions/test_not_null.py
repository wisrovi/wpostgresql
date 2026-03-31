import psycopg
import pytest
from pydantic import BaseModel, Field

from examples.test.conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL


class Person(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("person")
    yield
    cleanup_table("person")


def test_not_null_constraint():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30))

    conn = psycopg.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()
    with pytest.raises(Exception):
        cursor.execute("INSERT INTO person (id, name, age) VALUES (2, NULL, 25)")
    cursor.close()
    conn.close()
