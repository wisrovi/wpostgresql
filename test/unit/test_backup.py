"""Unit tests for wpostgresql SQLite backup feature using wsqlite."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from pydantic import BaseModel, Field

from wpostgresql.core.backup import backup_to_sqlite, backup_to_sqlite_async
from wpostgresql.core.repository import WPostgreSQL


class SampleModel(BaseModel):
    """Sample model for testing backup."""
    id: int = Field(description="Primary Key")
    name: str = Field(description="NOT NULL")
    age: int = 0


@pytest.fixture
def sample_records():
    """Sample records for testing."""
    return [
        SampleModel(id=1, name="Alice", age=30),
        SampleModel(id=2, name="Bob", age=25),
    ]


def test_backup_to_sqlite_sync(tmp_path, sample_records):
    """Test backing up PostgreSQL data to SQLite via wsqlite synchronously.

    This test verifies that:
    1. All records retrieved from PostgreSQL are inserted into WSQLite.
    2. The exact count of backed up records is returned.
    3. Works with both atomic file replacement (update=False) and update mode (update=True).
    """
    db_path = str(tmp_path / "backup_test.db")

    mock_repo = MagicMock(spec=WPostgreSQL)
    mock_repo.model = SampleModel
    mock_repo.get_all.return_value = sample_records

    with patch("wsqlite.WSQLite") as mock_wsqlite_cls:
        mock_wsqlite_instance = MagicMock()
        mock_wsqlite_cls.return_value = mock_wsqlite_instance

        # Test default atomic replace
        count = backup_to_sqlite(mock_repo, db_path)
        assert count == 2
        mock_wsqlite_instance.insert_many.assert_called_once_with(sample_records)

        # Test update mode
        mock_wsqlite_cls.reset_mock()
        mock_wsqlite_instance.reset_mock()
        mock_wsqlite_instance.get_all.return_value = sample_records

        count_update = backup_to_sqlite(mock_repo, db_path, update=True)
        assert count_update == 2
        mock_wsqlite_cls.assert_called_once_with(model=SampleModel, db_path=db_path)
        mock_wsqlite_instance.get_all.assert_called_once()
        mock_wsqlite_instance.delete_many.assert_called_once_with([1, 2])
        mock_wsqlite_instance.insert_many.assert_called_once_with(sample_records)


@pytest.mark.asyncio
async def test_backup_to_sqlite_async(tmp_path, sample_records):
    """Test backing up PostgreSQL data to SQLite via wsqlite asynchronously.

    This test verifies that:
    1. get_all_async fetches the records.
    2. Records are inserted into WSQLite.
    3. Works with both atomic file replacement and update mode.
    """
    db_path = str(tmp_path / "backup_test_async.db")

    mock_repo = MagicMock()
    mock_repo.model = SampleModel

    async def mock_get_all_async():
        return sample_records

    mock_repo.get_all_async = mock_get_all_async

    with patch("wsqlite.WSQLite") as mock_wsqlite_cls:
        mock_wsqlite_instance = MagicMock()
        mock_wsqlite_cls.return_value = mock_wsqlite_instance

        # Test default atomic replace
        count = await backup_to_sqlite_async(mock_repo, db_path)
        assert count == 2
        mock_wsqlite_instance.insert_many.assert_called_once_with(sample_records)

        # Test update mode
        mock_wsqlite_cls.reset_mock()
        mock_wsqlite_instance.reset_mock()
        mock_wsqlite_instance.get_all.return_value = sample_records

        count_update = await backup_to_sqlite_async(mock_repo, db_path, update=True)
        assert count_update == 2
        mock_wsqlite_cls.assert_called_once_with(model=SampleModel, db_path=db_path)
        mock_wsqlite_instance.get_all.assert_called_once()
        mock_wsqlite_instance.delete_many.assert_called_once_with([1, 2])
        mock_wsqlite_instance.insert_many.assert_called_once_with(sample_records)


def test_backup_db_to_sqlite(tmp_path, sample_records):
    """Test backing up multiple models into a single SQLite database."""
    from wpostgresql.core.backup import backup_db_to_sqlite

    db_path = tmp_path / "full_db_backup.db"

    with patch("wpostgresql.core.repository.WPostgreSQL") as mock_wpost_cls:
        mock_repo = MagicMock()
        mock_repo.backup_to_sqlite.return_value = 2
        mock_wpost_cls.return_value = mock_repo

        results = backup_db_to_sqlite([SampleModel], {}, db_path)

        assert results == {"samplemodel": 2}
        mock_repo.backup_to_sqlite.assert_called_once_with(db_path, update=True)


def test_export_to_sql_script(tmp_path, sample_records):
    """Test exporting models to a .sql reconstruction script."""
    from wpostgresql.core.backup import export_to_sql_script

    sql_path = tmp_path / "schema.sql"

    with patch("wpostgresql.core.repository.WPostgreSQL") as mock_wpost_cls:
        mock_repo = MagicMock()
        mock_repo.table_name = "samplemodel"
        mock_repo.get_all.return_value = sample_records
        mock_wpost_cls.return_value = mock_repo

        script_path = export_to_sql_script([SampleModel], {}, sql_path)

        assert Path(script_path).exists()
        content = Path(script_path).read_text()
        assert "CREATE TABLE IF NOT EXISTS samplemodel" in content
        assert "INSERT INTO samplemodel" in content
        assert "'Alice'" in content
