import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Union
import wsqlite


def backup_to_sqlite(
    repo: Any, sqlite_path: Union[str, Path], update: bool = False
) -> int:
    """Backup all records from a WPostgreSQL repository to an SQLite database file.

    Uses wsqlite.WSQLite to manage SQLite table schema creation and batch insert.

    Args:
        repo: An instance of WPostgreSQL.
        sqlite_path: File path for the SQLite database.
        update: If True, updates existing SQLite database table in place without replacing file.
                If False (default), creates a temporary backup file and atomically replaces destination file.

    Returns:
        int: Number of records backed up.
    """
    records = repo.get_all()
    if not records:
        return 0

    dest_path = Path(sqlite_path)

    if update:
        sqlite_db = wsqlite.WSQLite(model=repo.model, db_path=str(dest_path))
        # Clear existing records using wsqlite methods without introducing raw sqlite3 dependency
        existing_records = sqlite_db.get_all()
        if existing_records:
            existing_ids = [
                getattr(rec, "id")
                for rec in existing_records
                if hasattr(rec, "id") and getattr(rec, "id") is not None
            ]
            if existing_ids:
                sqlite_db.delete_many(existing_ids)
            else:
                for rec in existing_records:
                    if hasattr(rec, "id") and getattr(rec, "id") is not None:
                        sqlite_db.delete(getattr(rec, "id"))
        sqlite_db.insert_many(records)
        return len(records)

    # Atomic replace via temporary file
    temp_dir = dest_path.parent if dest_path.parent.exists() else Path(".")
    temp_fd, temp_file = tempfile.mkstemp(dir=temp_dir, suffix=".db.tmp")
    os.close(temp_fd)
    temp_path = Path(temp_file)

    try:
        sqlite_db = wsqlite.WSQLite(model=repo.model, db_path=str(temp_path), use_pool=False)
        sqlite_db.insert_many(records)
        if hasattr(wsqlite, "close_pool"):
            wsqlite.close_pool()
        shutil.move(str(temp_path), str(dest_path))
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass

    return len(records)


async def backup_to_sqlite_async(
    repo: Any, sqlite_path: Union[str, Path], update: bool = False
) -> int:
    """Asynchronously backup all records from WPostgreSQL to SQLite via WSQLite.

    Args:
        repo: An instance of WPostgreSQL.
        sqlite_path: File path for the SQLite database.
        update: If True, updates existing SQLite database table in place without replacing file.
                If False (default), creates a temporary backup file and atomically replaces destination file.

    Returns:
        int: Number of records backed up.
    """
    records = await repo.get_all_async()
    if not records:
        return 0

    dest_path = Path(sqlite_path)

    if update:
        sqlite_db = wsqlite.WSQLite(model=repo.model, db_path=str(dest_path))
        existing_records = sqlite_db.get_all()
        if existing_records:
            existing_ids = [
                getattr(rec, "id")
                for rec in existing_records
                if hasattr(rec, "id") and getattr(rec, "id") is not None
            ]
            if existing_ids:
                sqlite_db.delete_many(existing_ids)
            else:
                for rec in existing_records:
                    if hasattr(rec, "id") and getattr(rec, "id") is not None:
                        sqlite_db.delete(getattr(rec, "id"))
        sqlite_db.insert_many(records)
        return len(records)

    temp_dir = dest_path.parent if dest_path.parent.exists() else Path(".")
    temp_fd, temp_file = tempfile.mkstemp(dir=temp_dir, suffix=".db.tmp")
    os.close(temp_fd)
    temp_path = Path(temp_file)

    try:
        sqlite_db = wsqlite.WSQLite(model=repo.model, db_path=str(temp_path), use_pool=False)
        sqlite_db.insert_many(records)
        if hasattr(wsqlite, "close_pool"):
            wsqlite.close_pool()
        shutil.move(str(temp_path), str(dest_path))
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass

    return len(records)

