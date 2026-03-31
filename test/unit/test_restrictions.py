import os
import sys
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from wpostgresql import WPostgreSQL

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import DB_CONFIG, cleanup_table


@pytest.fixture(autouse=True)
def setup():
    cleanup_table("restrictedmodel")
    yield
    cleanup_table("restrictedmodel")


class TestPrimaryKey:
    """Tests para restricción Primary Key."""

    def test_primary_key_constraint(self):
        class RestrictedModel(BaseModel):
            id: int = Field(..., description="Primary Key")
            name: str

        db = WPostgreSQL(RestrictedModel, DB_CONFIG)

        import psycopg2

        pg_conn = psycopg2.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        cursor = pg_conn.cursor()
        cursor.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'restrictedmodel' AND tc.constraint_type = 'PRIMARY KEY'
        """)
        pkeys = [row[0] for row in cursor.fetchall()]
        cursor.close()
        pg_conn.close()

        assert "id" in pkeys


class TestUniqueConstraint:
    """Tests para restricción UNIQUE."""

    def test_unique_constraint(self):
        class UniqueModel(BaseModel):
            id: int = Field(..., description="Primary Key")
            email: Optional[str] = Field(None, description="UNIQUE")

        db = WPostgreSQL(UniqueModel, DB_CONFIG)

        import psycopg2

        pg_conn = psycopg2.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        cursor = pg_conn.cursor()
        cursor.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'uniquemodel' AND tc.constraint_type = 'UNIQUE'
        """)
        unique_cols = [row[0] for row in cursor.fetchall()]
        cursor.close()
        pg_conn.close()

        assert "email" in unique_cols


class TestNotNullConstraint:
    """Tests para restricción NOT NULL."""

    def test_not_null_constraint(self):
        class NotNullModel(BaseModel):
            id: int = Field(..., description="Primary Key")
            name: str = Field(..., description="NOT NULL")

        db = WPostgreSQL(NotNullModel, DB_CONFIG)

        import psycopg2

        pg_conn = psycopg2.connect(**DB_CONFIG)
        pg_conn.autocommit = True
        cursor = pg_conn.cursor()
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'notnullmodel' AND is_nullable = 'NO' AND column_name != 'id'
        """)
        not_null_cols = [row[0] for row in cursor.fetchall()]
        cursor.close()
        pg_conn.close()

        assert "name" in not_null_cols
