"""Tests for Forensic audit features and ForensicModel.

This module contains unit tests to verify that WPostgreSQL correctly handles:
1. Default disabled forensic mode (forensic=False).
2. Explicitly enabled forensic mode via ForensicModel inheritance or forensic=True flag.
3. Automatic schema creation and column synchronization for forensic fields.
4. Soft delete behavior with status=99 and audit metadata (delete_by, delete_in).
5. Automatic insertion metadata (create_by, create_in, status=1).
6. Automatic update metadata (update_by, update_in).
7. Filtering out soft-deleted records by default, and including them when requested.
"""

import os
import sys
from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from loguru import logger
from pydantic import BaseModel

# Ensure we can import from the parent directory for conftest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import DB_CONFIG, cleanup_table

from wpostgresql import ForensicModel, WPostgreSQL


class StandardProduct(BaseModel):
    """Standard model without forensic fields."""

    id: int
    name: str
    price: int


class ForensicProduct(ForensicModel):
    """Product model inheriting from ForensicModel."""

    id: int
    name: str
    price: int


@pytest.fixture(autouse=True)
def setup_teardown() -> Generator[None, None, None]:
    """Fixture to clean up test tables before and after each test.

    Yields:
        None: Execution context for the test.
    """
    logger.info("Setting up Forensic test environment...")
    cleanup_table("standardproduct")
    cleanup_table("forensicproduct")
    cleanup_table("explicitforensicproduct")
    yield
    logger.info("Tearing down Forensic test environment...")
    cleanup_table("standardproduct")
    cleanup_table("forensicproduct")
    cleanup_table("explicitforensicproduct")


class TestForensicMode:
    """Suite of tests validating forensic mode features and default behavior."""

    def test_default_disabled_forensic_mode(self):
        """Validates that forensic mode is disabled by default for standard BaseModel.

        This test creates a repository with a standard BaseModel, inserts a record,
        deletes it, and verifies that a physical DELETE FROM occurs without injecting
        forensic columns or status=99.
        """
        db = WPostgreSQL(StandardProduct, DB_CONFIG)
        assert db.forensic is False

        p = StandardProduct(id=1, name="Laptop", price=1000)
        db.insert(p)

        products = db.get_all()
        assert len(products) == 1
        assert products[0].name == "Laptop"

        # Deleting should physically remove the record
        db.delete(1)
        assert len(db.get_all()) == 0
        assert db.count() == 0

    def test_forensic_model_inheritance_activates_forensic_mode(self):
        """Validates that inheriting from ForensicModel automatically enables forensic mode.

        This test verifies that:
        - db.forensic is automatically True.
        - Insert automatically populates create_by, create_in, and status=1.
        - Update automatically populates update_by and update_in.
        - Delete performs a soft delete setting status=99, delete_by, and delete_in.
        - Standard get_all() excludes status=99, while get_all(include_deleted=True) includes it.
        """
        db = WPostgreSQL(ForensicProduct, DB_CONFIG)
        assert db.forensic is True

        # 1. Test Insert
        item = ForensicProduct(id=101, name="Keyboard", price=50)
        db.insert(item, user_id=42)

        records = db.get_all()
        assert len(records) == 1
        rec = records[0]
        assert rec.id == 101
        assert rec.create_by == 42
        assert rec.status == 1
        assert rec.create_in is not None

        # 2. Test Update
        updated_item = ForensicProduct(id=101, name="Mechanical Keyboard", price=80)
        db.update(101, updated_item, user_id=99)

        updated_records = db.get_all()
        assert len(updated_records) == 1
        u_rec = updated_records[0]
        assert u_rec.name == "Mechanical Keyboard"
        assert u_rec.update_by == 99
        assert u_rec.update_in is not None

        # 3. Test Soft Delete
        db.delete(101, user_id=777)

        # Standard query should now be empty (excludes status=99)
        assert len(db.get_all()) == 0
        assert db.count() == 0

        # Querying with include_deleted=True should return the soft-deleted row
        deleted_records = db.get_all(include_deleted=True)
        assert len(deleted_records) == 1
        d_rec = deleted_records[0]
        assert d_rec.status == 99
        assert d_rec.delete_by == 777
        assert d_rec.delete_in is not None

    def test_explicit_forensic_flag_on_standard_model(self):
        """Validates enabling forensic mode via forensic=True parameter on a standard BaseModel.

        This test verifies that passing forensic=True to WPostgreSQL creates forensic
        columns in PostgreSQL and performs soft deletion with status=99 even if the
        model does not inherit from ForensicModel.
        """
        db = WPostgreSQL(StandardProduct, DB_CONFIG, forensic=True)
        assert db.forensic is True

        p = StandardProduct(id=201, name="Mouse", price=25)
        db.insert(p, user_id=10)

        assert len(db.get_all()) == 1
        assert db.count() == 1

        db.delete(201, user_id=20)
        # Excluded from active queries
        assert len(db.get_all()) == 0
        assert db.count() == 0

        # Included when requesting deleted records
        all_recs = db.get_all(include_deleted=True)
        assert len(all_recs) == 1

    def test_hard_delete_in_forensic_mode(self):
        """Validates that passing hard=True to delete() physically removes the record even in forensic mode.

        This test verifies that hard=True overrides soft-delete and executes a physical DELETE FROM.
        """
        db = WPostgreSQL(ForensicProduct, DB_CONFIG)
        p = ForensicProduct(id=301, name="Monitor", price=200)
        db.insert(p)

        assert len(db.get_all()) == 1
        db.delete(301, hard=True)

        # Record is completely gone even with include_deleted=True
        assert len(db.get_all(include_deleted=True)) == 0
        assert db.count(include_deleted=True) == 0
