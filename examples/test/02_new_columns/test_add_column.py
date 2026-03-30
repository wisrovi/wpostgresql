from typing import Optional

import psycopg2
import pytest
from pydantic import BaseModel, Field

from examples.test.conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL


class Person(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str
    age: int


class Person2(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str
    age: int
    email: Optional[str]


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("person2")
    yield
    cleanup_table("person2")


def test_add_column():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30))

    db2 = WPostgreSQL(Person2, DB_CONFIG)
    db2.insert(Person2(id=2, name="Ana", age=25, email="ana@example.com"))

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'person2' ORDER BY ordinal_position"
    )
    columns = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    assert "email" in columns
    assert len(db2.get_all()) >= 1
