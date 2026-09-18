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
    dest_path = Path(sqlite_path)
    table_name = getattr(repo, "table_name", getattr(repo.model, "__tablename__", repo.model.__name__.lower()))

    if update:
        sqlite_db = wsqlite.WSQLite(
            model=repo.model, db_path=str(dest_path), table_name=table_name
        )
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
        if records:
            sqlite_db.insert_many(records)
        return len(records) if records else 0

    # Atomic replace via temporary file
    temp_dir = dest_path.parent if dest_path.parent.exists() else Path(".")
    temp_fd, temp_file = tempfile.mkstemp(dir=temp_dir, suffix=".db.tmp")
    os.close(temp_fd)
    temp_path = Path(temp_file)

    try:
        sqlite_db = wsqlite.WSQLite(
            model=repo.model, db_path=str(temp_path), table_name=table_name, use_pool=False
        )
        if records:
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

    return len(records) if records else 0


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
    dest_path = Path(sqlite_path)
    table_name = getattr(repo, "table_name", getattr(repo.model, "__tablename__", repo.model.__name__.lower()))

    if update:
        sqlite_db = wsqlite.WSQLite(
            model=repo.model, db_path=str(dest_path), table_name=table_name
        )
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
        if records:
            sqlite_db.insert_many(records)
        return len(records) if records else 0

    temp_dir = dest_path.parent if dest_path.parent.exists() else Path(".")
    temp_fd, temp_file = tempfile.mkstemp(dir=temp_dir, suffix=".db.tmp")
    os.close(temp_fd)
    temp_path = Path(temp_file)

    try:
        sqlite_db = wsqlite.WSQLite(
            model=repo.model, db_path=str(temp_path), table_name=table_name, use_pool=False
        )
        if records:
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

    return len(records) if records else 0


def backup_db_to_sqlite(
    models: list[type],
    db_config: dict,
    sqlite_path: Union[str, Path],
    update: bool = True,
) -> dict[str, int]:
    """Backup multiple Pydantic models (entire database tables) into a single SQLite database.

    Args:
        models: List of Pydantic BaseModel classes representing database tables.
        db_config: PostgreSQL database configuration dictionary.
        sqlite_path: Destination SQLite database file path.
        update: If True (default for multi-table backup), updates/synchronizes each table in-place.

    Returns:
        dict[str, int]: Dictionary mapping table/model name to backed up record count.
    """
    from wpostgresql.core.repository import WPostgreSQL

    dest_path = Path(sqlite_path)
    results = {}

    for model in models:
        repo = WPostgreSQL(model, db_config)
        table_name = getattr(model, "__tablename__", model.__name__.lower())
        results[table_name] = repo.backup_to_sqlite(dest_path, update=update)

    return results


async def backup_db_to_sqlite_async(
    models: list[type],
    db_config: dict,
    sqlite_path: Union[str, Path],
    update: bool = True,
) -> dict[str, int]:
    """Asynchronously backup multiple Pydantic models into a single SQLite database.

    Args:
        models: List of Pydantic BaseModel classes representing database tables.
        db_config: PostgreSQL database configuration dictionary.
        sqlite_path: Destination SQLite database file path.
        update: If True (default), updates/synchronizes each table in-place.

    Returns:
        dict[str, int]: Dictionary mapping table/model name to backed up record count.
    """
    from wpostgresql.core.repository import WPostgreSQL

    dest_path = Path(sqlite_path)
    results = {}

    for model in models:
        repo = WPostgreSQL(model, db_config)
        table_name = getattr(model, "__tablename__", model.__name__.lower())
        results[table_name] = await repo.backup_to_sqlite_async(dest_path, update=update)

    return results


def export_to_sql_script(
    models: list[type],
    db_config: dict,
    sql_script_path: Union[str, Path],
) -> str:
    """Generate a clean SQL reconstruction script (.sql) with DDL (CREATE TABLE) and DML (INSERT).

    Args:
        models: List of Pydantic BaseModel classes representing database tables.
        db_config: PostgreSQL database configuration dictionary.
        sql_script_path: Destination .sql file path.

    Returns:
        str: Absolute path of the created SQL script.
    """
    from wpostgresql.core.repository import WPostgreSQL
    from wpostgresql.types.sql_types import get_sql_type

    script_path = Path(sql_script_path)
    lines = ["-- WPostgreSQL Database Reconstruction Script", "-- Generated automatically\n"]

    for model in models:
        repo = WPostgreSQL(model, db_config)
        table_name = repo.table_name

        # Build CREATE TABLE DDL statement
        field_defs = [
            f"{field} {get_sql_type(typ)}" for field, typ in model.model_fields.items()
        ]
        ddl = f"CREATE TABLE IF NOT EXISTS {table_name} (\n  " + ",\n  ".join(field_defs) + "\n);"
        lines.append(f"-- Table schema for {table_name}")
        lines.append(ddl)
        lines.append("")

        # Build INSERT DML statements
        records = repo.get_all()
        if records:
            lines.append(f"-- Data dump for {table_name}")
            for rec in records:
                rec_dict = {k: v for k, v in rec.model_dump().items() if v is not None}
                if not rec_dict:
                    continue
                columns = ", ".join(rec_dict.keys())
                val_parts = []
                for v in rec_dict.values():
                    if isinstance(v, (str, bytes)):
                        escaped = str(v).replace("'", "''")
                        val_parts.append(f"'{escaped}'")
                    elif v is None:
                        val_parts.append("NULL")
                    elif isinstance(v, bool):
                        val_parts.append("TRUE" if v else "FALSE")
                    else:
                        val_parts.append(str(v))
                values_str = ", ".join(val_parts)
                lines.append(f"INSERT INTO {table_name} ({columns}) VALUES ({values_str});")
            lines.append("")

    script_path.write_text("\n".join(lines), encoding="utf-8")
    return str(script_path.resolve())


async def export_to_sql_script_async(
    models: list[type],
    db_config: dict,
    sql_script_path: Union[str, Path],
) -> str:
    """Asynchronously generate a clean SQL reconstruction script (.sql) with DDL and DML.

    Args:
        models: List of Pydantic BaseModel classes representing database tables.
        db_config: PostgreSQL database configuration dictionary.
        sql_script_path: Destination .sql file path.

    Returns:
        str: Absolute path of the created SQL script.
    """
    from wpostgresql.core.repository import WPostgreSQL
    from wpostgresql.types.sql_types import get_sql_type

    script_path = Path(sql_script_path)
    lines = ["-- WPostgreSQL Database Reconstruction Script", "-- Generated automatically\n"]

    for model in models:
        repo = WPostgreSQL(model, db_config)
        table_name = repo.table_name

        field_defs = [
            f"{field} {get_sql_type(typ)}" for field, typ in model.model_fields.items()
        ]
        ddl = f"CREATE TABLE IF NOT EXISTS {table_name} (\n  " + ",\n  ".join(field_defs) + "\n);"
        lines.append(f"-- Table schema for {table_name}")
        lines.append(ddl)
        lines.append("")

        records = await repo.get_all_async()
        if records:
            lines.append(f"-- Data dump for {table_name}")
            for rec in records:
                rec_dict = {k: v for k, v in rec.model_dump().items() if v is not None}
                if not rec_dict:
                    continue
                columns = ", ".join(rec_dict.keys())
                val_parts = []
                for v in rec_dict.values():
                    if isinstance(v, (str, bytes)):
                        escaped = str(v).replace("'", "''")
                        val_parts.append(f"'{escaped}'")
                    elif v is None:
                        val_parts.append("NULL")
                    elif isinstance(v, bool):
                        val_parts.append("TRUE" if v else "FALSE")
                    else:
                        val_parts.append(str(v))
                values_str = ", ".join(val_parts)
                lines.append(f"INSERT INTO {table_name} ({columns}) VALUES ({values_str});")
            lines.append("")

    script_path.write_text("\n".join(lines), encoding="utf-8")
    return str(script_path.resolve())

