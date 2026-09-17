"""Test for example 15_backups."""

import runpy
from unittest.mock import patch


def test_backup_example(tmp_path):
    """Test running backup example script with mocked WPostgreSQL methods."""
    with patch("wpostgresql.core.repository.WPostgreSQL.__init__", return_value=None), \
         patch("wpostgresql.core.repository.WPostgreSQL.insert"), \
         patch("wpostgresql.core.repository.WPostgreSQL.backup_to_sqlite", return_value=3):
        runpy.run_path("examples/15_backups/01_sqlite_backup/example.py", run_name="__main__")
