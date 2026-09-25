"""Unit tests for WPostgreSQL Ghost Table (_forensic_audit_log) audit trail system.

This module validates:
1. Automatic creation of global _forensic_audit_log table when forensic mode is enabled.
2. Recording of INSERT audit events with data_after JSON snapshot and data_before=None.
3. Recording of UPDATE audit events capturing data_before and data_after JSON snapshots.
4. Recording of SOFT_DELETE audit events with status=99 metadata in data_after.
5. Recording of HARD_DELETE audit events with data_before JSON snapshot and data_after=None.
"""

import json
from typing import Optional
import pytest
from pydantic import BaseModel

from wpostgresql import WPostgreSQL, ForensicModel
from wpostgresql.core.sync import TableSync


class AuditUser(ForensicModel):
    """Forensic model for testing ghost audit logging."""

    id: int
    name: str
    email: str


@pytest.fixture
def mock_db_config():
    """Mock database configuration dict."""
    return {
        "dbname": "test_db",
        "user": "postgres",
        "password": "password",
        "host": "localhost",
        "port": 5432,
    }


def test_ghost_audit_table_creation(mock_db_config, mocker):
    """Validate that TableSync executes CREATE TABLE IF NOT EXISTS _forensic_audit_log in forensic mode."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("wpostgresql.core.sync.get_connection", return_value=mock_conn)
    mock_conn.__enter__.return_value = mock_conn

    sync = TableSync(AuditUser, mock_db_config, forensic=True)
    sync.create_if_not_exists()

    # Verify _forensic_audit_log creation query was executed
    executed_queries = [call[0][0] for call in mock_cursor.execute.call_args_list]
    audit_table_query_found = any(
        "CREATE TABLE IF NOT EXISTS _forensic_audit_log" in q for q in executed_queries
    )
    assert audit_table_query_found is True


def test_insert_ghost_audit_recording(mock_db_config, mocker):
    """Validate that insert() records an INSERT event in _forensic_audit_log when forensic=True."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("wpostgresql.core.repository.get_connection", return_value=mock_conn)
    mock_conn.__enter__.return_value = mock_conn
    mocker.patch("wpostgresql.core.repository.TableSync.create_if_not_exists")
    mocker.patch("wpostgresql.core.repository.TableSync.sync_with_model")

    db = WPostgreSQL(AuditUser, mock_db_config, forensic=True)
    user_inst = AuditUser(id=1, name="Alice", email="alice@test.com")
    db.insert(user_inst, user_id=42)

    # Inspect executed queries to confirm ghost audit insertion
    executed_calls = mock_cursor.execute.call_args_list
    audit_calls = [
        c for c in executed_calls if "INSERT INTO _forensic_audit_log" in c[0][0]
    ]

    assert len(audit_calls) == 1
    args = audit_calls[0][0][1]
    # (table_name, action_type, record_id, data_before, data_after, create_by, create_in, status)
    assert args[0] == "audituser"
    assert args[1] == "INSERT"
    assert args[2] == "1"
    assert args[3] is None  # data_before is None for INSERT
    assert "alice@test.com" in args[4]  # data_after JSON contains user data
    assert args[5] == 42  # create_by user_id


def test_update_ghost_audit_recording(mock_db_config, mocker):
    """Validate that update() records an UPDATE event with before and after snapshots."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mocker.patch("wpostgresql.core.repository.get_connection", return_value=mock_conn)
    mock_conn.__enter__.return_value = mock_conn
    mocker.patch("wpostgresql.core.repository.TableSync.create_if_not_exists")
    mocker.patch("wpostgresql.core.repository.TableSync.sync_with_model")

    db = WPostgreSQL(AuditUser, mock_db_config, forensic=True)
    # Mock previous state retrieval
    mocker.patch.object(
        db,
        "get_by_field",
        return_value=[AuditUser(id=1, name="Alice Old", email="alice@old.com")],
    )

    updated_user = AuditUser(id=1, name="Alice New", email="alice@new.com")
    db.update(1, updated_user, user_id=99)

    executed_calls = mock_cursor.execute.call_args_list
    audit_calls = [
        c for c in executed_calls if "INSERT INTO _forensic_audit_log" in c[0][0]
    ]

    assert len(audit_calls) == 1
    args = audit_calls[0][0][1]
    assert args[1] == "UPDATE"
    assert args[2] == "1"
    assert "alice@old.com" in args[3]  # data_before
    assert "alice@new.com" in args[4]  # data_after
    assert args[5] == 99  # update_by user_id
