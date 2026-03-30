import os
import sys

import pytest
from pydantic import BaseModel

from wpostgresql import WPostgreSQL

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import DB_CONFIG, cleanup_table


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


class TestInsert:
    """Tests para el método insert()."""

    def test_insert_single_record(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        result = db.get_all()
        assert len(result) == 1
        assert result[0].name == "Juan"
        assert result[0].age == 30

    def test_insert_multiple_records(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))
        db.insert(Person(id=2, name="Ana", age=25, is_active=True))

        result = db.get_all()
        assert len(result) == 2

    def test_insert_validates_pydantic(self):
        db = WPostgreSQL(Person, DB_CONFIG)

        with pytest.raises(Exception):
            db.insert(Person(id="invalid", name="Juan", age=30, is_active=True))


class TestGetAll:
    """Tests para el método get_all()."""

    def test_get_all_returns_list(self):
        db = WPostgreSQL(Person, DB_CONFIG)

        result = db.get_all()
        assert isinstance(result, list)

    def test_get_all_with_data(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))
        db.insert(Person(id=2, name="Ana", age=25, is_active=True))

        result = db.get_all()
        assert len(result) == 2


class TestGetByField:
    """Tests para el método get_by_field()."""

    def test_get_by_single_field(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))
        db.insert(Person(id=2, name="Ana", age=25, is_active=True))

        result = db.get_by_field(name="Juan")
        assert len(result) == 1
        assert result[0].age == 30

    def test_get_by_multiple_fields(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))
        db.insert(Person(id=2, name="Ana", age=25, is_active=True))
        db.insert(Person(id=3, name="Pedro", age=25, is_active=True))

        result = db.get_by_field(age=25, is_active=True)
        assert len(result) == 2

    def test_get_by_field_no_match(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        result = db.get_by_field(name="NoExiste")
        assert len(result) == 0

    def test_get_by_field_empty_returns_all(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        result = db.get_by_field()
        assert len(result) == 1


class TestUpdate:
    """Tests para el método update()."""

    def test_update_record(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        db.update(1, Person(id=1, name="Juan", age=31, is_active=False))

        result = db.get_by_field(id=1)[0]
        assert result.age == 31
        assert result.is_active is False

    def test_update_non_existent(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        db.update(999, Person(id=999, name="NoExiste", age=20, is_active=True))

        result = db.get_all()
        assert len(result) == 1


class TestDelete:
    """Tests para el método delete()."""

    def test_delete_record(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))
        db.insert(Person(id=2, name="Ana", age=25, is_active=True))

        db.delete(1)

        result = db.get_all()
        assert len(result) == 1
        assert result[0].name == "Ana"

    def test_delete_non_existent(self):
        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30, is_active=True))

        db.delete(999)

        result = db.get_all()
        assert len(result) == 1


class TestNullHandling:
    """Tests para el manejo de valores NULL."""

    def test_null_handling_string(self):
        class PersonOptional(BaseModel):
            id: int
            name: str
            nickname: str

        cleanup_table("personoptional")
        db = WPostgreSQL(PersonOptional, DB_CONFIG)

        import psycopg2

        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("INSERT INTO personoptional (id, name) VALUES (1, 'Juan')")
        cursor.close()
        conn.close()

        result = db.get_all()
        assert result[0].nickname == ""

    def test_null_handling_int(self):
        class PersonOptional(BaseModel):
            id: int
            name: str
            age: int

        cleanup_table("personoptional")
        db = WPostgreSQL(PersonOptional, DB_CONFIG)

        import psycopg2

        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("INSERT INTO personoptional (id, name) VALUES (1, 'Juan')")
        cursor.close()
        conn.close()

        result = db.get_all()
        assert result[0].age == 0

    def test_null_handling_bool(self):
        class PersonOptional(BaseModel):
            id: int
            name: str
            is_active: bool

        cleanup_table("personoptional")
        db = WPostgreSQL(PersonOptional, DB_CONFIG)

        import psycopg2

        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("INSERT INTO personoptional (id, name) VALUES (1, 'Juan')")
        cursor.close()
        conn.close()

        result = db.get_all()
        assert result[0].is_active is False
