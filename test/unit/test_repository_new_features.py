"""Tests for new repository features.

This module contains unit tests for pagination, bulk operations, and
transaction management in the WPostgreSQL repository class.
"""

from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from loguru import logger
from pydantic import BaseModel

from wpostgresql.core.repository import WPostgreSQL, validate_identifier
from wpostgresql.exceptions import SQLInjectionError, TransactionError


class Person(BaseModel):
    """Simple model for testing purposes."""

    id: int
    name: str
    age: int


class TestValidateIdentifier:
    """Tests for validate_identifier function.

    Ensures that table and column names are safe from SQL injection.
    """

    def test_valid_identifier(self) -> None:
        """Test valid identifiers pass.

        Verifies that alphanumeric and underscore names are accepted.
        """
        logger.info("Testing valid identifiers...")
        validate_identifier("users")
        validate_identifier("my_table")
        validate_identifier("_private")
        logger.success("Valid identifiers test passed.")

    def test_invalid_identifier_sql_injection(self) -> None:
        """Test SQL injection attempt is blocked.

        Ensures that common SQL keywords and delimiters raise an SQLInjectionError.
        """
        logger.info("Testing SQL injection prevention...")
        with pytest.raises(SQLInjectionError):
            validate_identifier("users; DROP TABLE users;--")

        with pytest.raises(SQLInjectionError):
            validate_identifier("users UNION SELECT")

        with pytest.raises(SQLInjectionError):
            validate_identifier("123table")
        logger.success("SQL injection prevention test passed.")

    def test_invalid_identifier_special_chars(self) -> None:
        """Test special characters are blocked.

        Ensures that spaces and hyphens are not allowed in identifiers.
        """
        logger.info("Testing special characters block...")
        with pytest.raises(SQLInjectionError):
            validate_identifier("my-table")

        with pytest.raises(SQLInjectionError):
            validate_identifier("my table")
        logger.success("Special characters block test passed.")


class TestWPostgreSQLPagination:
    """Tests for pagination methods.

    Verifies get_paginated, get_page, and count methods with different parameters.
    """

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_get_paginated(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test get_paginated method.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing get_paginated...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "John", 25), (2, "Jane", 30)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        results: list[Person] = db.get_paginated(limit=10, offset=0)

        assert len(results) == 2
        logger.success("get_paginated test passed.")

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_get_paginated_with_order(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test get_paginated with ordering.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing get_paginated with ORDER BY...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        _ = db.get_paginated(limit=10, offset=0, order_by="name", order_desc=True)

        assert "ORDER BY name DESC" in mock_cursor.execute.call_args[0][0]
        logger.success("get_paginated with ORDER BY test passed.")

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_get_page(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test get_page method.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing get_page...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "John", 25), (2, "Jane", 30)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        results: list[Person] = db.get_page(page=1, per_page=10)

        assert len(results) == 2
        logger.success("get_page test passed.")

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_get_page_invalid_page(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test get_page with invalid page number.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing get_page with invalid page...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        results: list[Person] = db.get_page(page=-1, per_page=10)

        assert len(results) == 0
        logger.success("get_page with invalid page test passed.")

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_get_page_invalid_per_page(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test get_page with invalid per_page number.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing get_page with invalid per_page...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        results: list[Person] = db.get_page(page=1, per_page=-5)

        assert len(results) == 0
        logger.success("get_page with invalid per_page test passed.")

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_count(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test count method.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing count...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (100,)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        total: int = db.count()

        assert total == 100
        logger.success("count test passed.")


class TestWPostgreSQLBulk:
    """Tests for bulk operations.

    Verifies insert_many, update_many, and delete_many methods.
    """

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_insert_many_empty(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test insert_many with empty list.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing insert_many with empty list...")
        mock_conn = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        db.insert_many([])

        mock_conn.commit.assert_not_called()
        logger.success("insert_many empty test passed.")

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_insert_many(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test insert_many method.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing insert_many with data...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        persons: list[Person] = [
            Person(id=1, name="John", age=25),
            Person(id=2, name="Jane", age=30),
        ]
        db.insert_many(persons)

        assert mock_cursor.execute.call_count == 2
        mock_conn.commit.assert_called_once()
        logger.success("insert_many test passed.")

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_update_many_empty(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test update_many with empty list.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing update_many with empty list...")
        mock_conn = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        result: int = db.update_many([])

        assert result == 0
        logger.success("update_many empty test passed.")

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_update_many(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test update_many method.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing update_many with data...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        persons: list[Person] = [Person(id=1, name="John", age=25)]
        result: int = db.update_many([(persons[0], 1)])

        assert result == 1
        mock_conn.commit.assert_called_once()
        logger.success("update_many test passed.")

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_delete_many_empty(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test delete_many with empty list.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing delete_many with empty list...")
        mock_conn = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        result: int = db.delete_many([])

        assert result == 0
        logger.success("delete_many empty test passed.")

    @patch("wpostgresql.core.repository.get_connection")
    @patch("wpostgresql.core.repository.TableSync")
    def test_delete_many(self, _mock_sync: Mock, mock_get_conn: Mock) -> None:
        """Test delete_many method.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_conn: Mocked get_connection function.
        """
        logger.info("Testing delete_many with data...")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_get_conn.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        result: int = db.delete_many([1, 2, 3])

        assert result == 3
        mock_conn.commit.assert_called_once()
        logger.success("delete_many test passed.")


class TestWPostgreSQLTransactions:
    """Tests for transaction methods.

    Verifies execute_transaction and with_transaction success and failure cases.
    """

    @patch("wpostgresql.core.repository.get_transaction")
    @patch("wpostgresql.core.repository.TableSync")
    def test_execute_transaction_success(
        self, _mock_sync: Mock, mock_get_transaction: Mock
    ) -> None:
        """Test execute_transaction successful.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_transaction: Mocked get_transaction function.
        """
        logger.info("Testing execute_transaction success...")
        mock_txn = MagicMock()
        mock_txn.execute.return_value = [("result",)]
        mock_get_transaction.return_value.__enter__.return_value = mock_txn
        mock_get_transaction.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})
        _ = db.execute_transaction([("SELECT 1", ())])

        assert mock_txn.commit.called
        logger.success("execute_transaction success test passed.")

    @patch("wpostgresql.core.repository.get_transaction")
    @patch("wpostgresql.core.repository.TableSync")
    def test_execute_transaction_failure(
        self, _mock_sync: Mock, mock_get_transaction: Mock
    ) -> None:
        """Test execute_transaction failure.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_transaction: Mocked get_transaction function.
        """
        logger.info("Testing execute_transaction failure...")
        mock_txn = MagicMock()
        mock_txn.execute.side_effect = RuntimeError("DB Error")
        mock_get_transaction.return_value.__enter__.return_value = mock_txn
        mock_get_transaction.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})

        with pytest.raises(TransactionError):
            db.execute_transaction([("SELECT 1", ())])
        logger.success("execute_transaction failure test passed.")

    @patch("wpostgresql.core.repository.get_transaction")
    @patch("wpostgresql.core.repository.TableSync")
    def test_with_transaction_success(self, _mock_sync: Mock, mock_get_transaction: Mock) -> None:
        """Test with_transaction successful.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_transaction: Mocked get_transaction function.
        """
        logger.info("Testing with_transaction success...")
        mock_txn = MagicMock()
        mock_txn.execute.return_value = [("result",)]
        mock_get_transaction.return_value.__enter__.return_value = mock_txn
        mock_get_transaction.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})

        def operation(txn: Any) -> list[tuple[Any, ...]]:
            """Dummy operation."""
            return txn.execute("SELECT 1", ())

        _ = db.with_transaction(operation)

        assert mock_txn.commit.called
        logger.success("with_transaction success test passed.")

    @patch("wpostgresql.core.repository.get_transaction")
    @patch("wpostgresql.core.repository.TableSync")
    def test_with_transaction_failure(self, _mock_sync: Mock, mock_get_transaction: Mock) -> None:
        """Test with_transaction failure.

        Args:
            _mock_sync: Mocked TableSync class.
            mock_get_transaction: Mocked get_transaction function.
        """
        logger.info("Testing with_transaction failure...")
        mock_txn = MagicMock()
        mock_get_transaction.return_value.__enter__.return_value = mock_txn
        mock_get_transaction.return_value.__exit__.return_value = False

        db = WPostgreSQL(Person, {"dbname": "test"})

        def operation(_txn: Any) -> None:
            """Failing operation."""
            raise RuntimeError("DB Error")

        with pytest.raises(TransactionError):
            db.with_transaction(operation)
        logger.success("with_transaction failure test passed.")
