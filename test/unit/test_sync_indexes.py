"""Tests for sync module indexes."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import BaseModel

from wpostgresql.core.sync import TableSync


class Person(BaseModel):
    id: int
    name: str
    age: int


class TestTableSyncIndexes:
    """Tests for TableSync index methods."""

    @patch("wpostgresql.core.sync.get_connection")
    def test_create_index(self, mock_get_conn):
        """Test create_index method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        sync.create_index(["name"], index_name="idx_name")

        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch("wpostgresql.core.sync.get_connection")
    def test_create_unique_index(self, mock_get_conn):
        """Test create_index with unique=True."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        sync.create_index(["email"], unique=True)

        call_args = mock_cursor.execute.call_args[0][0]
        assert "UNIQUE" in call_args

    @patch("wpostgresql.core.sync.get_connection")
    def test_create_index_auto_name(self, mock_get_conn):
        """Test create_index auto-generates index name."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        sync.create_index(["name", "age"])

        call_args = mock_cursor.execute.call_args[0][0]
        assert "idx_person_name_age" in call_args

    @patch("wpostgresql.core.sync.get_connection")
    def test_drop_index(self, mock_get_conn):
        """Test drop_index method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        sync.drop_index("idx_name")

        call_args = mock_cursor.execute.call_args[0][0]
        assert "DROP INDEX" in call_args
        assert "idx_name" in call_args

    @patch("wpostgresql.core.sync.get_connection")
    def test_get_indexes(self, mock_get_conn):
        """Test get_indexes method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("idx_name", "CREATE INDEX idx_name ON person (name)"),
            ("idx_age", "CREATE INDEX idx_age ON person (age)"),
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        indexes = sync.get_indexes()

        assert len(indexes) == 2
        assert indexes[0]["name"] == "idx_name"
        assert indexes[1]["definition"] == "CREATE INDEX idx_age ON person (age)"

    @patch("wpostgresql.core.sync.get_connection")
    def test_table_exists_true(self, mock_get_conn):
        """Test table_exists returns True."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (True,)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        exists = sync.table_exists()

        assert exists is True

    @patch("wpostgresql.core.sync.get_connection")
    def test_table_exists_false(self, mock_get_conn):
        """Test table_exists returns False."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (False,)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        exists = sync.table_exists()

        assert exists is False

    @patch("wpostgresql.core.sync.get_connection")
    def test_drop_table(self, mock_get_conn):
        """Test drop_table method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        sync.drop_table()

        call_args = mock_cursor.execute.call_args[0][0]
        assert "DROP TABLE" in call_args
        mock_conn.commit.assert_called_once()

    @patch("wpostgresql.core.sync.get_connection")
    def test_get_columns(self, mock_get_conn):
        """Test get_columns method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("id",), ("name",), ("age",)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        columns = sync.get_columns()

        assert columns == ["id", "name", "age"]
