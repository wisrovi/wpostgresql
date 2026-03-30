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


def test_get_all():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30, is_active=True))
    db.insert(Person(id=2, name="Ana", age=25, is_active=True))
    db.insert(Person(id=3, name="Pedro", age=40, is_active=False))

    result = db.get_all()
    assert len(result) == 3


def test_get_by_field_single_filter():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30, is_active=True))
    db.insert(Person(id=2, name="Ana", age=25, is_active=True))

    result = db.get_by_field(name="Juan")
    assert len(result) == 1
    assert result[0].age == 30


def test_get_by_field_multiple_filters():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30, is_active=True))
    db.insert(Person(id=2, name="Ana", age=25, is_active=True))
    db.insert(Person(id=3, name="Pedro", age=25, is_active=True))

    result = db.get_by_field(age=25, is_active=True)
    assert len(result) == 2


def test_get_by_field_no_results():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30, is_active=True))

    result = db.get_by_field(name="NoExiste")
    assert len(result) == 0
