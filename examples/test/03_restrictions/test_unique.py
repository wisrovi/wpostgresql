from typing import Optional

import pytest
from pydantic import BaseModel, Field

from examples.test.conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL


class Person(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str
    email: Optional[str] = Field(None, description="UNIQUE")


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("person")
    yield
    cleanup_table("person")


def test_unique_constraint():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", email="juan@example.com"))

    with pytest.raises(Exception):
        db.insert(Person(id=2, name="Ana", email="juan@example.com"))


def test_unique_allows_null():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", email=None))
    db.insert(Person(id=2, name="Ana", email=None))

    result = db.get_all()
    assert len(result) == 2
