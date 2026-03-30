import pytest
from pydantic import BaseModel, Field

from examples.test.conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL


class Person(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str
    age: int


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("person")
    yield
    cleanup_table("person")


def test_primary_key_duplicate():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30))

    with pytest.raises(Exception):
        db.insert(Person(id=1, name="Ana", age=25))
