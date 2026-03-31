import pytest
from pydantic import BaseModel

from examples.test.conftest import DB_CONFIG, cleanup_table
from wpostgresql import WPostgreSQL


class Person(BaseModel):
    id: int
    name: str
    age: int
    is_active: bool


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("person")
    yield
    cleanup_table("person")


def test_delete_record():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30, is_active=True))
    db.insert(Person(id=2, name="Ana", age=25, is_active=True))

    db.delete(1)

    result = db.get_all()
    assert len(result) == 1
    assert result[0].name == "Ana"


def test_delete_non_existent():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30, is_active=True))

    db.delete(999)

    result = db.get_all()
    assert len(result) == 1
