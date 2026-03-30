import os
import sys
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from wpostgresql import WPostgreSQL

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import psycopg2
from conftest import DB_CONFIG, cleanup_table


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("person")
    cleanup_table("newtable")
    yield
    cleanup_table("person")
    cleanup_table("newtable")


class TestSyncTable:
    """Tests para la sincronización de tablas."""

    def test_add_new_column_to_existing_table(self):
        cleanup_table("person")

        class Person(BaseModel):
            id: int = Field(..., description="Primary Key")
            name: str
            age: int

        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan", age=30))

        class Person(BaseModel):
            id: int = Field(..., description="Primary Key")
            name: str
            age: int
            email: Optional[str]

        db2 = WPostgreSQL(Person, DB_CONFIG)

        pg_conn = psycopg2.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        cursor = pg_conn.cursor()
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'person'"
        )
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()
        pg_conn.close()

        assert "email" in columns

    def test_insert_with_new_column(self):
        cleanup_table("person")

        class Person(BaseModel):
            id: int = Field(..., description="Primary Key")
            name: str

        db = WPostgreSQL(Person, DB_CONFIG)
        db.insert(Person(id=1, name="Juan"))

        class Person(BaseModel):
            id: int = Field(..., description="Primary Key")
            name: str
            email: Optional[str]

        db2 = WPostgreSQL(Person, DB_CONFIG)
        db2.insert(Person(id=2, name="Ana", email="ana@example.com"))

        result = db2.get_by_field(id=2)
        assert len(result) == 1
        assert result[0].email == "ana@example.com"

    def test_multiple_new_columns(self):
        cleanup_table("person")

        class Person(BaseModel):
            id: int = Field(..., description="Primary Key")
            name: str

        db = WPostgreSQL(Person, DB_CONFIG)

        class Person(BaseModel):
            id: int = Field(..., description="Primary Key")
            name: str
            email: Optional[str]
            phone: Optional[str]
            address: Optional[str]

        db2 = WPostgreSQL(Person, DB_CONFIG)

        pg_conn = psycopg2.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        cursor = pg_conn.cursor()
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'person' ORDER BY ordinal_position"
        )
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()
        pg_conn.close()

        assert "email" in columns
        assert "phone" in columns
        assert "address" in columns


class TestCreateTable:
    """Tests para la creación de tablas."""

    def test_create_table_if_not_exists(self):
        class NewTable(BaseModel):
            id: int
            name: str

        cleanup_table("newtable")

        db = WPostgreSQL(NewTable, DB_CONFIG)

        pg_conn = psycopg2.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        cursor = pg_conn.cursor()
        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'newtable')"
        )
        exists = cursor.fetchone()[0]
        cursor.close()
        pg_conn.close()

        assert exists is True

    def test_create_table_does_not_fail_if_exists(self):
        class NewTable(BaseModel):
            id: int
            name: str

        db = WPostgreSQL(NewTable, DB_CONFIG)
        db2 = WPostgreSQL(NewTable, DB_CONFIG)

        result = db2.get_all()
        assert isinstance(result, list)
