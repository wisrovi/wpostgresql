"""Tests for new repository features."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import BaseModel

from wpostgresql.core.repository import WPostgreSQL, validate_identifier
from wpostgresql.exceptions import SQLInjectionError, TransactionError


class Person(BaseModel):
    id: int
    name: str
    age: int


class TestValidateIdentifier:
    """Tests for validate_identifier function."""

    def test_valid_identifier(self):
        """Test valid identifiers pass."""
        validate_identifier("users")
        validate_identifier("my_table")
        validate_identifier("_private")

    def test_invalid_identifier_sql_injection(self):
        """Test SQL injection attempt is blocked."""
        with pytest.raises(SQLInjectionError):
            validate_identifier("users; DROP TABLE users;--")

        with pytest.raises(SQLInjectionError):
            validate_identifier("users UNION SELECT")

        with pytest.raises(SQLInjectionError):
            validate_identifier("123table")

    def test_invalid_identifier_special_chars(self):
        """Test special characters are blocked."""
        with pytest.raises(SQLInjectionError):
            validate_identifier("my-table")

        with pytest.raises(SQLInjectionError):
            validate_identifier("my table")


class TestWPostgreSQLPagination:
    """Tests for pagination methods."""

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_get_paginated(self, mock_sync, mock_get_conn):
        """Test get_paginated method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "John", 25), (2, "Jane", 30)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        results = db.get_paginated(limit=10, offset=0)

        assert len(results) == 2

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_get_paginated_with_order(self, mock_sync, mock_get_conn):
        """Test get_paginated with ordering."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        results = db.get_paginated(limit=10, offset=0, order_by="name", order_desc=True)

        assert "ORDER BY name DESC" in mock_cursor.execute.call_args[0][0]

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_get_page(self, mock_sync, mock_get_conn):
        """Test get_page method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "John", 25), (2, "Jane", 30)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        results = db.get_page(page=1, per_page=10)

        assert len(results) == 2

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_get_page_invalid_page(self, mock_sync, mock_get_conn):
        """Test get_page with invalid page number."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        results = db.get_page(page=-1, per_page=10)

        assert len(results) == 0

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_get_page_invalid_per_page(self, mock_sync, mock_get_conn):
        """Test get_page with invalid per_page number."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        results = db.get_page(page=1, per_page=-5)

        assert len(results) == 0

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_count(self, mock_sync, mock_get_conn):
        """Test count method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (100,)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        total = db.count()

        assert total == 100


class TestWPostgreSQLBulk:
    """Tests for bulk operations."""

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_insert_many_empty(self, mock_sync, mock_get_conn):
        """Test insert_many with empty list."""
        mock_conn = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        db.insert_many([])

        mock_conn.commit.assert_not_called()

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_insert_many(self, mock_sync, mock_get_conn):
        """Test insert_many method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        persons = [Person(id=1, name="John", age=25), Person(id=2, name="Jane", age=30)]
        db.insert_many(persons)

        assert mock_cursor.execute.call_count == 2
        mock_conn.commit.assert_called_once()

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_update_many_empty(self, mock_sync, mock_get_conn):
        """Test update_many with empty list."""
        mock_conn = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        result = db.update_many([])

        assert result == 0

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_update_many(self, mock_sync, mock_get_conn):
        """Test update_many method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        persons = [Person(id=1, name="John", age=25)]
        result = db.update_many([(persons[0], 1)])

        assert result == 1
        mock_conn.commit.assert_called_once()

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_delete_many_empty(self, mock_sync, mock_get_conn):
        """Test delete_many with empty list."""
        mock_conn = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        result = db.delete_many([])

        assert result == 0

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_delete_many(self, mock_sync, mock_get_conn):
        """Test delete_many method."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        result = db.delete_many([1, 2, 3])

        assert result == 3
        mock_conn.commit.assert_called_once()


class TestWPostgreSQLTransactions:
    """Tests for transaction methods."""

    @patch("wpostgresql.core.repository.get_transaction")
    @patch("wpostgresql.core.repository.TableSync")
    def test_execute_transaction_success(self, mock_sync, mock_get_transaction):
        """Test execute_transaction successful."""
        mock_txn = MagicMock()
        mock_txn.execute.return_value = [("result",)]
        mock_get_transaction.return_value.__enter__.return_value = mock_txn
        mock_get_transaction.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        result = db.execute_transaction([("SELECT 1", ())])

        assert mock_txn.commit.called

    @patch("wpostgresql.core.repository.get_transaction")
    @patch("wpostgresql.core.repository.TableSync")
    def test_execute_transaction_failure(self, mock_sync, mock_get_transaction):
        """Test execute_transaction failure."""
        mock_txn = MagicMock()
        mock_txn.execute.side_effect = Exception("DB Error")
        mock_get_transaction.return_value.__enter__.return_value = mock_txn
        mock_get_transaction.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})

        with pytest.raises(TransactionError):
            db.execute_transaction([("SELECT 1", ())])

    @patch("wpostgresql.core.repository.get_transaction")
    @patch("wpostgresql.core.repository.TableSync")
    def test_with_transaction_success(self, mock_sync, mock_get_transaction):
        """Test with_transaction successful."""
        mock_txn = MagicMock()
        mock_txn.execute.return_value = [("result",)]
        mock_get_transaction.return_value.__enter__.return_value = mock_txn
        mock_get_transaction.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})

        def operation(txn):
            return txn.execute("SELECT 1", ())

        result = db.with_transaction(operation)

        assert mock_txn.commit.called

    @patch("wpostgresql.core.repository.get_transaction")
    @patch("wpostgresql.core.repository.TableSync")
    def test_with_transaction_failure(self, mock_sync, mock_get_transaction):
        """Test with_transaction failure."""
        mock_txn = MagicMock()
        mock_get_transaction.return_value.__enter__.return_value = mock_txn
        mock_get_transaction.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})

        def operation(txn):
            raise Exception("DB Error")

        with pytest.raises(TransactionError):
            db.with_transaction(operation)
