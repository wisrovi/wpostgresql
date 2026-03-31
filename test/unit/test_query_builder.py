"""Tests for QueryBuilder."""

import pytest

from wpostgresql.builders.query_builder import QueryBuilder
from wpostgresql.exceptions import SQLInjectionError


class TestQueryBuilder:
    """Tests for QueryBuilder class."""

    def test_init_valid_table_name(self):
        """Test initialization with valid table name."""
        qb = QueryBuilder("users")
        assert qb.table_name == "users"

    def test_init_invalid_table_name(self):
        """Test initialization with invalid table name."""
        with pytest.raises(SQLInjectionError):
            QueryBuilder("users; DROP TABLE users;--")

    def test_where_equals(self):
        """Test WHERE with equals operator."""
        qb = QueryBuilder("users").where("name", "=", "John")
        query, values = qb.build_select()
        assert "WHERE name = %s" in query
        assert values == ("John",)

    def test_where_greater_than(self):
        """Test WHERE with greater than operator."""
        qb = QueryBuilder("users").where("age", ">", 18)
        query, values = qb.build_select()
        assert "WHERE age > %s" in query
        assert values == (18,)

    def test_where_like(self):
        """Test WHERE with LIKE operator."""
        qb = QueryBuilder("users").where("name", "LIKE", "%John%")
        query, values = qb.build_select()
        assert "WHERE name LIKE %s" in query
        assert values == ("%John%",)

    def test_where_in(self):
        """Test WHERE with IN operator."""
        qb = QueryBuilder("users").where("id", "IN", [1, 2, 3])
        query, values = qb.build_select()
        assert "WHERE id IN %s" in query
        assert values == (1, 2, 3)

    def test_where_is_null(self):
        """Test WHERE with IS NULL operator."""
        qb = QueryBuilder("users").where("email", "IS NULL", None)
        query, values = qb.build_select()
        assert "WHERE email IS NULL" in query
        assert values == ()

    def test_where_is_not_null(self):
        """Test WHERE with IS NOT NULL operator."""
        qb = QueryBuilder("users").where("email", "IS NOT NULL", None)
        query, values = qb.build_select()
        assert "WHERE email IS NOT NULL" in query
        assert values == ()

    def test_where_invalid_operator(self):
        """Test WHERE with invalid operator."""
        with pytest.raises(ValueError):
            QueryBuilder("users").where("id", "INVALID", 1)

    def test_where_in_requires_list(self):
        """Test WHERE IN requires list."""
        with pytest.raises(ValueError):
            QueryBuilder("users").where("id", "IN", 1)

    def test_multiple_where_clauses(self):
        """Test multiple WHERE clauses."""
        qb = QueryBuilder("users").where("age", ">", 18).where("city", "=", "NYC")
        query, values = qb.build_select()
        assert "AND" in query
        assert values == (18, "NYC")

    def test_order_by_ascending(self):
        """Test ORDER BY ascending."""
        qb = QueryBuilder("users").order_by("name")
        query, _ = qb.build_select()
        assert "ORDER BY name ASC" in query

    def test_order_by_descending(self):
        """Test ORDER BY descending."""
        qb = QueryBuilder("users").order_by("name", descending=True)
        query, _ = qb.build_select()
        assert "ORDER BY name DESC" in query

    def test_order_by_invalid_column(self):
        """Test ORDER BY with invalid column name."""
        with pytest.raises(SQLInjectionError):
            QueryBuilder("users").order_by("name; DROP TABLE")

    def test_limit(self):
        """Test LIMIT clause."""
        qb = QueryBuilder("users").limit(10)
        query, _ = qb.build_select()
        assert "LIMIT 10" in query

    def test_limit_negative(self):
        """Test LIMIT with negative value."""
        with pytest.raises(ValueError):
            QueryBuilder("users").limit(-1)

    def test_offset(self):
        """Test OFFSET clause."""
        qb = QueryBuilder("users").offset(20)
        query, _ = qb.build_select()
        assert "OFFSET 20" in query

    def test_offset_negative(self):
        """Test OFFSET with negative value."""
        with pytest.raises(ValueError):
            QueryBuilder("users").offset(-1)

    def test_build_count(self):
        """Test COUNT query."""
        qb = QueryBuilder("users").where("age", ">", 18)
        query, values = qb.build_count()
        assert "SELECT COUNT(*)" in query
        assert values == (18,)

    def test_build_delete(self):
        """Test DELETE query."""
        qb = QueryBuilder("users").where("id", "=", 1)
        query, values = qb.build_delete()
        assert "DELETE FROM users" in query
        assert "WHERE id = %s" in query
        assert values == (1,)

    def test_build_delete_without_where(self):
        """Test DELETE without WHERE clause."""
        with pytest.raises(ValueError):
            QueryBuilder("users").build_delete()

    def test_reset(self):
        """Test reset builder."""
        qb = QueryBuilder("users").where("id", "=", 1).order_by("name").limit(10)
        qb.reset()
        query, values = qb.build_select()
        assert "WHERE" not in query
        assert "ORDER BY" not in query
        assert "LIMIT" not in query
        assert values == ()

    def test_full_query(self):
        """Test full query building."""
        qb = (
            QueryBuilder("users")
            .where("age", ">", 18)
            .where("city", "=", "NYC")
            .order_by("name", descending=True)
            .limit(10)
            .offset(20)
        )
        query, values = qb.build_select()
        assert "SELECT * FROM users" in query
        assert "WHERE age > %s AND city = %s" in query
        assert "ORDER BY name DESC" in query
        assert "LIMIT 10" in query
        assert "OFFSET 20" in query
        assert values == (18, "NYC")
