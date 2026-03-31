"""Tests for async methods in WPostgreSQL.

This module contains unit tests to verify the existence and signatures of
asynchronous methods in WPostgreSQL and AsyncTableSync classes.
"""

import inspect
from typing import List

from loguru import logger
from pydantic import BaseModel

from wpostgresql import AsyncTableSync, WPostgreSQL


class Person(BaseModel):
    """Simple model for testing purposes."""

    id: int
    name: str
    age: int


class TestAsyncMethodsExist:
    """Tests to verify that necessary async methods exist in the classes.

    This class groups tests that ensure WPostgreSQL and AsyncTableSync
    implement the required asynchronous interface.
    """

    def test_wpostgresql_has_async_methods(self) -> None:
        """Test that WPostgreSQL has all expected async methods.

        This test iterates through a list of mandatory async methods and
        asserts their presence in the WPostgreSQL class.
        """
        logger.info("Verifying WPostgreSQL async methods...")
        db_methods: List[str] = dir(WPostgreSQL)
        async_methods: List[str] = [
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
        logger.success("All WPostgreSQL async methods are present.")

    def test_async_table_sync_exists(self) -> None:
        """Test that AsyncTableSync class exists and has its core methods.

        Verifies that AsyncTableSync provides the expected methods for
        asynchronous table and index management.
        """
        logger.info("Verifying AsyncTableSync async methods...")
        assert hasattr(AsyncTableSync, "create_if_not_exists_async")
        assert hasattr(AsyncTableSync, "sync_with_model_async")
        assert hasattr(AsyncTableSync, "table_exists_async")
        assert hasattr(AsyncTableSync, "drop_table_async")
        assert hasattr(AsyncTableSync, "get_columns_async")
        assert hasattr(AsyncTableSync, "create_index_async")
        assert hasattr(AsyncTableSync, "drop_index_async")
        assert hasattr(AsyncTableSync, "get_indexes_async")
        logger.success("All AsyncTableSync async methods are present.")

    def test_wpostgresql_async_method_signatures(self) -> None:
        """Test that async methods in WPostgreSQL have correct signatures.

        Checks the parameters of key asynchronous methods using introspection.
        """
        logger.info("Checking WPostgreSQL async method signatures...")

        # Check insert_async signature
        sig = inspect.signature(WPostgreSQL.insert_async)
        params: List[str] = list(sig.parameters.keys())
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
        logger.success("WPostgreSQL signatures are correct.")


class TestAsyncTableSyncMethods:
    """Tests for AsyncTableSync method signatures.

    This class groups tests that verify the signature of methods within
    the AsyncTableSync class.
    """

    def test_async_table_sync_create_signature(self) -> None:
        """Test create_if_not_exists_async signature.

        Ensures that the method correctly expects 'self'.
        """
        logger.info("Checking AsyncTableSync.create_if_not_exists_async signature...")
        sig = inspect.signature(AsyncTableSync.create_if_not_exists_async)
        params: List[str] = list(sig.parameters.keys())
        assert "self" in params
        logger.success("Signature for create_if_not_exists_async is correct.")

    def test_async_table_sync_sync_signature(self) -> None:
        """Test sync_with_model_async signature.

        Ensures that the method correctly expects 'self'.
        """
        logger.info("Checking AsyncTableSync.sync_with_model_async signature...")
        sig = inspect.signature(AsyncTableSync.sync_with_model_async)
        params: List[str] = list(sig.parameters.keys())
        assert "self" in params
        logger.success("Signature for sync_with_model_async is correct.")

    def test_async_table_sync_exists_method_signature(self) -> None:
        """Test table_exists_async signature.

        Ensures that the method correctly expects 'self' and returns a bool-like type.
        """
        logger.info("Checking AsyncTableSync.table_exists_async signature...")
        sig = inspect.signature(AsyncTableSync.table_exists_async)
        params: List[str] = list(sig.parameters.keys())
        assert "self" in params
        assert "return" in str(sig) or "bool" in str(sig)
        logger.success("Signature for table_exists_async is correct.")
