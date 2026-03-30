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


def test_update_record():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30, is_active=True))

    db.update(1, Person(id=1, name="Juan", age=31, is_active=False))

    result = db.get_by_field(id=1)[0]
    assert result.age == 31
    assert result.is_active is False


def test_update_non_existent():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30, is_active=True))

    db.update(999, Person(id=999, name="NoExiste", age=20, is_active=True))

    result = db.get_all()
    assert len(result) == 1
