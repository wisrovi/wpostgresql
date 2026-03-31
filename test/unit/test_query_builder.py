"""Tests for QueryBuilder.

This module contains unit tests for the QueryBuilder class, ensuring that
SQL queries are built correctly and securely for various clauses.
"""



import pytest
from loguru import logger

from wpostgresql.builders.query_builder import QueryBuilder
from wpostgresql.exceptions import SQLInjectionError


class TestQueryBuilderInit:
    """Tests for QueryBuilder initialization and validation.

    Ensures that table names are correctly validated upon instantiation.
    """

    def test_init_valid_table_name(self) -> None:
        """Test initialization with valid table name.

        Verifies that a simple table name is correctly assigned.
        """
        logger.info("Testing QueryBuilder init with valid table name...")
        qb = QueryBuilder("users")
        assert qb.table_name == "users"
        logger.success("Valid table name test passed.")

    def test_init_invalid_table_name(self) -> None:
        """Test initialization with invalid table name.

        Ensures that an SQLInjectionError is raised for potentially malicious table names.
        """
        logger.info("Testing QueryBuilder init with invalid table name...")
        with pytest.raises(SQLInjectionError):
            QueryBuilder("users; DROP TABLE users;--")
        logger.success("Invalid table name test passed.")


class TestQueryBuilderWhere:
    """Tests for WHERE clause building.

    This class groups tests that verify various operators (EQUALS, LIKE, IN, NULL)
    within the WHERE clause.
    """

    def test_where_equals(self) -> None:
        """Test WHERE with equals operator.

        Verifies correct placeholder generation and value mapping.
        """
        logger.info("Testing WHERE equals...")
        qb = QueryBuilder("users").where("name", "=", "John")
        query, values = qb.build_select()
        assert "WHERE name = %s" in query
        assert values == ("John",)
        logger.success("WHERE equals test passed.")

    def test_where_greater_than(self) -> None:
        """Test WHERE with greater than operator.

        Verifies comparison operators.
        """
        logger.info("Testing WHERE greater than...")
        qb = QueryBuilder("users").where("age", ">", 18)
        query, values = qb.build_select()
        assert "WHERE age > %s" in query
        assert values == (18,)
        logger.success("WHERE greater than test passed.")

    def test_where_like(self) -> None:
        """Test WHERE with LIKE operator.

        Verifies pattern matching queries.
        """
        logger.info("Testing WHERE LIKE...")
        qb = QueryBuilder("users").where("name", "LIKE", "%John%")
        query, values = qb.build_select()
        assert "WHERE name LIKE %s" in query
        assert values == ("%John%",)
        logger.success("WHERE LIKE test passed.")

    def test_where_in(self) -> None:
        """Test WHERE with IN operator.

        Verifies that lists are correctly handled for IN clauses.
        """
        logger.info("Testing WHERE IN...")
        qb = QueryBuilder("users").where("id", "IN", [1, 2, 3])
        query, values = qb.build_select()
        assert "WHERE id IN %s" in query
        assert values == (1, 2, 3)
        logger.success("WHERE IN test passed.")

    def test_where_is_null(self) -> None:
        """Test WHERE with IS NULL operator.

        Verifies that NULL checks don't include unnecessary placeholders.
        """
        logger.info("Testing WHERE IS NULL...")
        qb = QueryBuilder("users").where("email", "IS NULL", None)
        query, values = qb.build_select()
        assert "WHERE email IS NULL" in query
        assert values == ()
        logger.success("WHERE IS NULL test passed.")

    def test_where_is_not_null(self) -> None:
        """Test WHERE with IS NOT NULL operator.

        Verifies that NOT NULL checks are correctly formatted.
        """
        logger.info("Testing WHERE IS NOT NULL...")
        qb = QueryBuilder("users").where("email", "IS NOT NULL", None)
        query, values = qb.build_select()
        assert "WHERE email IS NOT NULL" in query
        assert values == ()
        logger.success("WHERE IS NOT NULL test passed.")

    def test_where_invalid_operator(self) -> None:
        """Test WHERE with invalid operator.

        Ensures a ValueError is raised for unsupported SQL operators.
        """
        logger.info("Testing WHERE with invalid operator...")
        with pytest.raises(ValueError):
            QueryBuilder("users").where("id", "INVALID", 1)
        logger.success("Invalid operator test passed.")

    def test_where_in_requires_list(self) -> None:
        """Test WHERE IN requires list.

        Ensures that non-list types raise a ValueError when using the IN operator.
        """
        logger.info("Testing WHERE IN requirement...")
        with pytest.raises(ValueError):
            QueryBuilder("users").where("id", "IN", 1)
        logger.success("WHERE IN requirement test passed.")

    def test_multiple_where_clauses(self) -> None:
        """Test multiple WHERE clauses.

        Verifies that multiple filters are combined with AND.
        """
        logger.info("Testing multiple WHERE clauses...")
        qb = QueryBuilder("users").where("age", ">", 18).where("city", "=", "NYC")
        query, values = qb.build_select()
        assert "AND" in query
        assert values == (18, "NYC")
        logger.success("Multiple WHERE clauses test passed.")


class TestQueryBuilderOrderLimit:
    """Tests for ORDER BY, LIMIT, and OFFSET clauses.

    Verifies the correct generation of sorting and pagination parts of the query.
    """

    def test_order_by_ascending(self) -> None:
        """Test ORDER BY ascending.

        Verifies default sorting behavior.
        """
        logger.info("Testing ORDER BY ASC...")
        qb = QueryBuilder("users").order_by("name")
        query, _ = qb.build_select()
        assert "ORDER BY name ASC" in query
        logger.success("ORDER BY ASC test passed.")

    def test_order_by_descending(self) -> None:
        """Test ORDER BY descending.

        Verifies explicit descending sorting.
        """
        logger.info("Testing ORDER BY DESC...")
        qb = QueryBuilder("users").order_by("name", descending=True)
        query, _ = qb.build_select()
        assert "ORDER BY name DESC" in query
        logger.success("ORDER BY DESC test passed.")

    def test_order_by_invalid_column(self) -> None:
        """Test ORDER BY with invalid column name.

        Ensures column names are validated to prevent SQL injection.
        """
        logger.info("Testing ORDER BY column validation...")
        with pytest.raises(SQLInjectionError):
            QueryBuilder("users").order_by("name; DROP TABLE")
        logger.success("ORDER BY validation test passed.")

    def test_limit(self) -> None:
        """Test LIMIT clause.

        Verifies that numeric limits are correctly applied.
        """
        logger.info("Testing LIMIT clause...")
        qb = QueryBuilder("users").limit(10)
        query, _ = qb.build_select()
        assert "LIMIT 10" in query
        logger.success("LIMIT test passed.")

    def test_limit_negative(self) -> None:
        """Test LIMIT with negative value.

        Ensures that negative limits raise a ValueError.
        """
        logger.info("Testing negative LIMIT...")
        with pytest.raises(ValueError):
            QueryBuilder("users").limit(-1)
        logger.success("Negative LIMIT test passed.")

    def test_offset(self) -> None:
        """Test OFFSET clause.

        Verifies that offsets are correctly applied for pagination.
        """
        logger.info("Testing OFFSET clause...")
        qb = QueryBuilder("users").offset(20)
        query, _ = qb.build_select()
        assert "OFFSET 20" in query
        logger.success("OFFSET test passed.")

    def test_offset_negative(self) -> None:
        """Test OFFSET with negative value.

        Ensures that negative offsets raise a ValueError.
        """
        logger.info("Testing negative OFFSET...")
        with pytest.raises(ValueError):
            QueryBuilder("users").offset(-1)
        logger.success("Negative OFFSET test passed.")


class TestQueryBuilderBuild:
    """Tests for final query construction.

    Verifies build_select, build_count, build_delete, and reset functionality.
    """

    def test_build_count(self) -> None:
        """Test COUNT query construction.

        Ensures COUNT queries use correct SELECT COUNT(*) syntax.
        """
        logger.info("Testing build_count...")
        qb = QueryBuilder("users").where("age", ">", 18)
        query, values = qb.build_count()
        assert "SELECT COUNT(*)" in query
        assert values == (18,)
        logger.success("build_count test passed.")

    def test_build_delete(self) -> None:
        """Test DELETE query construction.

        Ensures DELETE queries are correctly formatted with a WHERE clause.
        """
        logger.info("Testing build_delete...")
        qb = QueryBuilder("users").where("id", "=", 1)
        query, values = qb.build_delete()
        assert "DELETE FROM users" in query
        assert "WHERE id = %s" in query
        assert values == (1,)
        logger.success("build_delete test passed.")

    def test_build_delete_without_where(self) -> None:
        """Test DELETE without WHERE clause.

        Ensures a ValueError is raised to prevent accidental full table deletion.
        """
        logger.info("Testing build_delete safety...")
        with pytest.raises(ValueError):
            QueryBuilder("users").build_delete()
        logger.success("build_delete safety test passed.")

    def test_reset(self) -> None:
        """Test reset builder state.

        Ensures that reset clears all internal clauses and values.
        """
        logger.info("Testing QueryBuilder.reset()...")
        qb = QueryBuilder("users").where("id", "=", 1).order_by("name").limit(10)
        qb.reset()
        query, values = qb.build_select()
        assert "WHERE" not in query
        assert "ORDER BY" not in query
        assert "LIMIT" not in query
        assert values == ()
        logger.success("Reset test passed.")

    def test_full_query(self) -> None:
        """Test full query building with all clauses.

        Verifies that complex queries with many clauses are correctly ordered and formatted.
        """
        logger.info("Testing full query generation...")
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
        logger.success("Full query test passed.")
