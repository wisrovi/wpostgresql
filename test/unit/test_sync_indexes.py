"""Tests for sync module indexes.

This module contains unit tests for the TableSync class, focusing on
index management, table existence checks, and schema metadata retrieval.
"""

from unittest.mock import MagicMock, Mock, patch

from loguru import logger
from pydantic import BaseModel

from wpostgresql.core.sync import TableSync


class Person(BaseModel):
    """Simple model for testing purposes."""

    id: int
    name: str
    age: int


class TestTableSyncIndexes:
    """Tests for TableSync index and table management methods.

    This class groups tests that verify the correct generation of SQL
    for index creation/deletion and table schema operations.
    """

    @patch("wpostgresql.core.sync.get_connection")
    def test_create_index(self, mock_get_conn: Mock) -> None:
        """Test create_index method.

        Verifies that an index is correctly created with a specified name.
        """
        logger.info("Testing create_index with explicit name...")
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
        logger.success("create_index test passed.")

    @patch("wpostgresql.core.sync.get_connection")
    def test_create_unique_index(self, mock_get_conn: Mock) -> None:
        """Test create_index with unique=True.

        Verifies that the UNIQUE keyword is present in the generated SQL.
        """
        logger.info("Testing create_index with UNIQUE constraint...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        sync.create_index(["email"], unique=True)

        call_args: str = mock_cursor.execute.call_args[0][0]
        assert "UNIQUE" in call_args
        logger.success("create_unique_index test passed.")

    @patch("wpostgresql.core.sync.get_connection")
    def test_create_index_auto_name(self, mock_get_conn: Mock) -> None:
        """Test create_index auto-generates index name.

        Verifies that the generated name follows the expected pattern.
        """
        logger.info("Testing create_index with auto-generated name...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        sync.create_index(["name", "age"])

        call_args: str = mock_cursor.execute.call_args[0][0]
        assert "idx_person_name_age" in call_args
        logger.success("create_index_auto_name test passed.")

    @patch("wpostgresql.core.sync.get_connection")
    def test_drop_index(self, mock_get_conn: Mock) -> None:
        """Test drop_index method.

        Verifies that the DROP INDEX statement is correctly formatted.
        """
        logger.info("Testing drop_index...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        sync.drop_index("idx_name")

        call_args: str = mock_cursor.execute.call_args[0][0]
        assert "DROP INDEX" in call_args
        assert "idx_name" in call_args
        logger.success("drop_index test passed.")

    @patch("wpostgresql.core.sync.get_connection")
    def test_get_indexes(self, mock_get_conn: Mock) -> None:
        """Test get_indexes method.

        Verifies that index metadata is correctly parsed into a list of dictionaries.
        """
        logger.info("Testing get_indexes metadata retrieval...")
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
        indexes: list[dict[str, str]] = sync.get_indexes()

        assert len(indexes) == 2
        assert indexes[0]["name"] == "idx_name"
        assert indexes[1]["definition"] == "CREATE INDEX idx_age ON person (age)"
        logger.success("get_indexes test passed.")

    @patch("wpostgresql.core.sync.get_connection")
    def test_table_exists_true(self, mock_get_conn: Mock) -> None:
        """Test table_exists returns True.

        Verifies that the method correctly interprets a positive result from the database.
        """
        logger.info("Testing table_exists (True case)...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (True,)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        exists: bool = sync.table_exists()

        assert exists is True
        logger.success("table_exists (True) test passed.")

    @patch("wpostgresql.core.sync.get_connection")
    def test_table_exists_false(self, mock_get_conn: Mock) -> None:
        """Test table_exists returns False.

        Verifies that the method correctly interprets a negative result from the database.
        """
        logger.info("Testing table_exists (False case)...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (False,)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        exists: bool = sync.table_exists()

        assert exists is False
        logger.success("table_exists (False) test passed.")

    @patch("wpostgresql.core.sync.get_connection")
    def test_drop_table(self, mock_get_conn: Mock) -> None:
        """Test drop_table method.

        Verifies that the DROP TABLE statement is correctly executed and committed.
        """
        logger.info("Testing drop_table...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        sync.drop_table()

        call_args: str = mock_cursor.execute.call_args[0][0]
        assert "DROP TABLE" in call_args
        mock_conn.commit.assert_called_once()
        logger.success("drop_table test passed.")

    @patch("wpostgresql.core.sync.get_connection")
    def test_get_columns(self, mock_get_conn: Mock) -> None:
        """Test get_columns method.

        Verifies that the list of column names is correctly retrieved.
        """
        logger.info("Testing get_columns...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("id",), ("name",), ("age",)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        sync = TableSync(Person, {"dbname": "test"})
        columns: list[str] = sync.get_columns()

        assert columns == ["id", "name", "age"]
        logger.success("get_columns test passed.")
