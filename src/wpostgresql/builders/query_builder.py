"""Query builder for constructing SQL queries safely."""

import re
from typing import Any, Optional

from wpostgresql.exceptions import SQLInjectionError


def validate_identifier(identifier: str) -> None:
    """Validate SQL identifier to prevent SQL injection."""
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        raise SQLInjectionError(f"Invalid identifier: {identifier}")


class QueryBuilder:
    """Builder for constructing SQL queries safely."""

    def __init__(self, table_name: str):
        """Initialize query builder.

        Args:
            table_name: Name of the table to query.
        """
        validate_identifier(table_name)
        self.table_name = table_name
        self._where_clauses: list[str] = []
        self._where_values: list[Any] = []
        self._order_by: Optional[str] = None
        self._order_desc: bool = False
        self._limit_value: Optional[int] = None
        self._offset_value: Optional[int] = None

    def where(self, field: str, operator: str, value: Any) -> "QueryBuilder":
        """Add WHERE condition.

        Args:
            field: Field name.
            operator: Operator (=, <, >, <=, >=, !=, LIKE, IN).
            value: Value to compare.

        Returns:
            Self for chaining.
        """
        validate_identifier(field)
        valid_operators = {"=", "<", ">", "<=", ">=", "!=", "LIKE", "IN", "IS NULL", "IS NOT NULL"}
        if operator.upper() not in valid_operators:
            raise ValueError(f"Invalid operator: {operator}")

        if operator.upper() == "IN" and not isinstance(value, (list, tuple)):
            raise ValueError("IN operator requires a list or tuple")

        if operator.upper() in ("IS NULL", "IS NOT NULL"):
            self._where_clauses.append(f"{field} {operator.upper()}")
        else:
            self._where_clauses.append(f"{field} {operator} %s")
            if operator.upper() == "IN":
                self._where_values.extend(value)
            else:
                self._where_values.append(value)

        return self

    def order_by(self, field: str, descending: bool = False) -> "QueryBuilder":
        """Add ORDER BY clause.

        Args:
            field: Field to order by.
            descending: If True, order descending.

        Returns:
            Self for chaining.
        """
        validate_identifier(field)
        self._order_by = field
        self._order_desc = descending
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """Add LIMIT clause.

        Args:
            limit: Maximum number of rows.

        Returns:
            Self for chaining.
        """
        if limit < 0:
            raise ValueError("Limit must be non-negative")
        self._limit_value = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """Add OFFSET clause.

        Args:
            offset: Number of rows to skip.

        Returns:
            Self for chaining.
        """
        if offset < 0:
            raise ValueError("Offset must be non-negative")
        self._offset_value = offset
        return self

    def build_select(self) -> tuple[str, tuple]:
        """Build SELECT query.

        Returns:
            Tuple of (query_string, values).
        """
        query = f"SELECT * FROM {self.table_name}"

        if self._where_clauses:
            query += " WHERE " + " AND ".join(self._where_clauses)

        if self._order_by:
            direction = "DESC" if self._order_desc else "ASC"
            query += f" ORDER BY {self._order_by} {direction}"

        if self._limit_value is not None:
            query += f" LIMIT {self._limit_value}"

        if self._offset_value is not None:
            query += f" OFFSET {self._offset_value}"

        return query, tuple(self._where_values)

    def build_count(self) -> tuple[str, tuple]:
        """Build COUNT query.

        Returns:
            Tuple of (query_string, values).
        """
        query = f"SELECT COUNT(*) FROM {self.table_name}"

        if self._where_clauses:
            query += " WHERE " + " AND ".join(self._where_clauses)

        return query, tuple(self._where_values)

    def build_delete(self) -> tuple[str, tuple]:
        """Build DELETE query.

        Returns:
            Tuple of (query_string, values).
        """
        if not self._where_clauses:
            raise ValueError("DELETE requires WHERE clause")

        query = f"DELETE FROM {self.table_name}"
        query += " WHERE " + " AND ".join(self._where_clauses)

        return query, tuple(self._where_values)

    def reset(self) -> "QueryBuilder":
        """Reset the builder to initial state.

        Returns:
            Self for chaining.
        """
        self._where_clauses = []
        self._where_values = []
        self._order_by = None
        self._order_desc = False
        self._limit_value = None
        self._offset_value = None
        return self
