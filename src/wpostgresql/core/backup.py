"""Backup module for exporting WPostgreSQL table contents into SQLite via WSQLite."""

from pathlib import Path
from typing import Any, Union
import wsqlite


def backup_to_sqlite(repo: Any, sqlite_path: Union[str, Path]) -> int:
    """Backup all records from a WPostgreSQL repository to an SQLite database file.

    Uses wsqlite.WSQLite to manage SQLite table schema creation and batch insert.

    Args:
        repo: An instance of WPostgreSQL.
        sqlite_path: File path for the SQLite database.

    Returns:
        int: Number of records backed up.
    """
    records = repo.get_all()
    if not records:
        return 0

    sqlite_db = wsqlite.WSQLite(model=repo.model, db_path=str(sqlite_path))
    sqlite_db.insert_many(records)
    return len(records)


async def backup_to_sqlite_async(repo: Any, sqlite_path: Union[str, Path]) -> int:
    """Asynchronously backup all records from WPostgreSQL to SQLite via WSQLite.

    Args:
        repo: An instance of WPostgreSQL.
        sqlite_path: File path for the SQLite database.

    Returns:
        int: Number of records backed up.
    """
    records = await repo.get_all_async()
    if not records:
        return 0

    sqlite_db = wsqlite.WSQLite(model=repo.model, db_path=str(sqlite_path))
    sqlite_db.insert_many(records)
    return len(records)
