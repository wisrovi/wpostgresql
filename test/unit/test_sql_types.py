import os
import sys

import pytest
from pydantic import BaseModel

from wpostgresql import WPostgreSQL

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import DB_CONFIG, cleanup_table


class SampleModel(BaseModel):
    id: int
    name: str
    age: int
    is_active: bool


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("samplemodel")
    yield
    cleanup_table("samplemodel")


class TestSQLTypeMapping:
    """Tests para la conversión de tipos Pydantic a SQL."""

    def test_int_maps_to_integer(self):
        db = WPostgreSQL(SampleModel, DB_CONFIG)

        conn = DB_CONFIG.copy()
        conn["dbname"] = "wpostgresql"
        import psycopg2

        pg_conn = psycopg2.connect(**conn)
        pg_conn.autocommit = True
        cursor = pg_conn.cursor()
        cursor.execute(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'samplemodel'"
        )
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        pg_conn.close()

        assert columns["id"] == "integer"
        assert columns["age"] == "integer"

    def test_str_maps_to_text(self):
        db = WPostgreSQL(SampleModel, DB_CONFIG)

        import psycopg2

        pg_conn = psycopg2.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        cursor = pg_conn.cursor()
        cursor.execute(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'samplemodel'"
        )
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        pg_conn.close()

        assert columns["name"] == "text"

    def test_bool_maps_to_boolean(self):
        db = WPostgreSQL(SampleModel, DB_CONFIG)

        import psycopg2

        pg_conn = psycopg2.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        cursor = pg_conn.cursor()
        cursor.execute(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'samplemodel'"
        )
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        pg_conn.close()

        assert columns["is_active"] == "boolean"


class TestTableName:
    """Tests para el nombre de tabla."""

    def test_table_name_is_lowercase_model_name(self):
        class MyModel(BaseModel):
            id: int
            name: str

        db = WPostgreSQL(MyModel, DB_CONFIG)
        assert db.table_name == "mymodel"

    def test_table_name_with_multiple_words(self):
        class UserProfile(BaseModel):
            id: int
            full_name: str

        db = WPostgreSQL(UserProfile, DB_CONFIG)
        assert db.table_name == "userprofile"
