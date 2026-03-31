"""Tests for async methods in WPostgreSQL."""

import pytest
from pydantic import BaseModel

from wpostgresql import WPostgreSQL, AsyncTableSync


class Person(BaseModel):
    id: int
    name: str
    age: int


class TestAsyncMethodsExist:
    """Tests to verify async methods exist."""

    def test_wpostgresql_has_async_methods(self):
        """Test that WPostgreSQL has all async methods."""
        db_methods = dir(WPostgreSQL)
        async_methods = [
            "insert_async",
            "get_all_async",
            "get_by_field_async",
            "update_async",
            "delete_async",
            "get_paginated_async",
            "get_page_async",
            "count_async",
            "insert_many_async",
            "update_many_async",
            "delete_many_async",
            "execute_transaction_async",
            "with_transaction_async",
        ]

        for method in async_methods:
            assert method in db_methods, f"Missing method: {method}"

    def test_async_table_sync_exists(self):
        """Test that AsyncTableSync class exists."""
        assert hasattr(AsyncTableSync, "create_if_not_exists_async")
        assert hasattr(AsyncTableSync, "sync_with_model_async")
        assert hasattr(AsyncTableSync, "table_exists_async")
        assert hasattr(AsyncTableSync, "drop_table_async")
        assert hasattr(AsyncTableSync, "get_columns_async")
        assert hasattr(AsyncTableSync, "create_index_async")
        assert hasattr(AsyncTableSync, "drop_index_async")
        assert hasattr(AsyncTableSync, "get_indexes_async")

    def test_wpostgresql_async_method_signatures(self):
        """Test that async methods have correct signatures."""
        import inspect

        # Check insert_async signature
        sig = inspect.signature(WPostgreSQL.insert_async)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "data" in params

        # Check get_all_async signature
        sig = inspect.signature(WPostgreSQL.get_all_async)
        params = list(sig.parameters.keys())
        assert "self" in params

        # Check count_async signature
        sig = inspect.signature(WPostgreSQL.count_async)
        params = list(sig.parameters.keys())
        assert "self" in params


class TestAsyncTableSyncMethods:
    """Tests for AsyncTableSync methods."""

    def test_async_table_sync_create_signature(self):
        """Test create_if_not_exists_async signature."""
        import inspect

        sig = inspect.signature(AsyncTableSync.create_if_not_exists_async)
        params = list(sig.parameters.keys())
        assert "self" in params

    def test_async_table_sync_sync_signature(self):
        """Test sync_with_model_async signature."""
        import inspect

        sig = inspect.signature(AsyncTableSync.sync_with_model_async)
        params = list(sig.parameters.keys())
        assert "self" in params

    def test_async_table_sync_exists_method_signature(self):
        """Test table_exists_async signature."""
        import inspect

        sig = inspect.signature(AsyncTableSync.table_exists_async)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "return" in str(sig) or "bool" in str(sig)
