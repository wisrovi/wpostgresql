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


def test_insert_single_record():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan Pérez", age=30, is_active=True))

    result = db.get_all()
    assert len(result) == 1
    assert result[0].name == "Juan Pérez"


def test_insert_multiple_records():
    db = WPostgreSQL(Person, DB_CONFIG)
    db.insert(Person(id=1, name="Juan", age=30, is_active=True))
    db.insert(Person(id=2, name="Ana", age=25, is_active=True))

    result = db.get_all()
    assert len(result) == 2


def test_insert_validates_pydantic():
    db = WPostgreSQL(Person, DB_CONFIG)

    with pytest.raises(Exception):
        db.insert(Person(id="invalid", name="Juan", age=30, is_active=True))
