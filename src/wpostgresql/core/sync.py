"""Table synchronization with Pydantic models."""

from typing import Optional

from wpostgresql.core.connection import get_async_connection, get_connection
from wpostgresql.types.sql_types import get_field_foreign_key, get_sql_type


FORENSIC_COLUMNS = {
    "create_by": "INTEGER DEFAULT 1",
    "create_in": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
    "update_by": "INTEGER DEFAULT NULL",
    "update_in": "TIMESTAMP WITH TIME ZONE DEFAULT NULL",
    "delete_by": "INTEGER DEFAULT NULL",
    "delete_in": "TIMESTAMP WITH TIME ZONE DEFAULT NULL",
    "status": "INTEGER DEFAULT 1",
}


def get_model_dependencies(model: type) -> set[str]:
    """Extract table name dependencies from foreign key fields and __depends_on__ in a model."""
    deps = set()
    # Check explicit view dependencies from @view(depends_on=[...])
    view_deps = getattr(model, "__depends_on__", None)
    if view_deps:
        for dep in view_deps:
            if isinstance(dep, str):
                deps.add(dep.lower())
            elif hasattr(dep, "__view_name__"):
                deps.add(dep.__view_name__.lower())
            elif hasattr(dep, "__tablename__"):
                deps.add(dep.__tablename__.lower())
            elif hasattr(dep, "__name__"):
                deps.add(dep.__name__.lower())

    for field_info in model.model_fields.values():
        fk = get_field_foreign_key(field_info)
        if fk is not None:
            if isinstance(fk, str):
                deps.add(fk.split(".")[0].lower())
            elif hasattr(fk, "__tablename__"):
                deps.add(fk.__tablename__.lower())
            elif hasattr(fk, "__name__"):
                deps.add(fk.__name__.lower())
    return deps


def sort_models_by_dependencies(models: list[type]) -> list[type]:
    """Sort models topologically so parent tables are created before child tables."""
    model_map = {
        getattr(m, "__view_name__", getattr(m, "__tablename__", m.__name__.lower())): m
        for m in models
    }
    sorted_models = []
    visited = set()
    visiting = set()

    def visit(m):
        name = getattr(
            m, "__view_name__", getattr(m, "__tablename__", m.__name__.lower())
        )
        if name in visited:
            return
        if name in visiting:
            # Cycle detected, return to prevent infinite loop
            return
        visiting.add(name)
        deps = get_model_dependencies(m)
        for dep_name in deps:
            if dep_name in model_map and dep_name != name:
                visit(model_map[dep_name])
        visiting.remove(name)
        visited.add(name)
        sorted_models.append(m)

    for m in models:
        visit(m)

    return sorted_models


class TableSync:
    """Handles table synchronization between Pydantic models and PostgreSQL (sync)."""

    def __init__(
        self,
        model,
        db_config: dict,
        pool_config: Optional[dict] = None,
        forensic: bool = False,
    ):
        """Initialize table sync."""
        self.model = model
        self.db_config = db_config
        self.pool_config = pool_config
        self.forensic = forensic
        self.table_name = getattr(
            model,
            "__view_name__",
            getattr(model, "__tablename__", model.__name__.lower()),
        )

    def create_audit_table_if_not_exists(self):
        """Create global forensic audit log ghost table (_forensic_audit_log)."""
        query = (
            "CREATE TABLE IF NOT EXISTS _forensic_audit_log ("
            "id SERIAL PRIMARY KEY, "
            "table_name TEXT NOT NULL, "
            "action_type TEXT NOT NULL, "
            "record_id TEXT, "
            "data_before TEXT, "
            "data_after TEXT, "
            "create_by INTEGER DEFAULT 1, "
            "create_in TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, "
            "status INTEGER DEFAULT 1"
            ")"
        )
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def create_if_not_exists(self):
        """Create the table or view if it doesn't exist."""
        view_query = getattr(self.model, "__view_query__", None)
        view_name = getattr(self.model, "__view_name__", self.table_name)
        if view_query:
            query = f"CREATE OR REPLACE VIEW {view_name} AS {view_query}"
            with get_connection(self.db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                conn.commit()
            return

        field_defs = []

        # Auto-synthesize Primary Key id column if not defined in Pydantic model
        if "id" not in self.model.model_fields:
            field_defs.append("id SERIAL PRIMARY KEY")

        for field, typ in self.model.model_fields.items():
            field_defs.append(f"{field} {get_sql_type(typ)}")

        if self.forensic:
            self.create_audit_table_if_not_exists()
            model_fields = set(self.model.model_fields.keys())
            if "id" not in model_fields:
                model_fields.add("id")
            for f_name, f_sql in FORENSIC_COLUMNS.items():
                if f_name not in model_fields:
                    field_defs.append(f"{f_name} {f_sql}")

        fields = ", ".join(field_defs)
        query = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({fields})"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def sync_with_model(self):
        """Sync the table with the Pydantic model, adding new columns if necessary."""
        if getattr(self.model, "__view_query__", None):
            return
        query = (
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
        )
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (self.table_name,))
            rows = cursor.fetchall()
            existing_columns = {row[0] for row in rows}

        model_fields = set(self.model.model_fields.keys())
        if "id" not in model_fields:
            model_fields.add("id")

        if self.forensic:
            expected_fields = model_fields | set(FORENSIC_COLUMNS.keys())
        else:
            expected_fields = model_fields

        new_fields = expected_fields - existing_columns

        if new_fields:
            with get_connection(self.db_config) as conn:
                with conn.cursor() as cursor:
                    for field in new_fields:
                        if field in FORENSIC_COLUMNS:
                            field_type = FORENSIC_COLUMNS[field]
                        elif field == "id":
                            field_type = "SERIAL PRIMARY KEY"
                        else:
                            field_type = f"{get_sql_type(self.model.model_fields[field])} DEFAULT NULL"
                        alter_query = f"ALTER TABLE {self.table_name} ADD COLUMN {field} {field_type}"
                        cursor.execute(alter_query)
                conn.commit()

    def table_exists(self) -> bool:
        """Check if the table exists in the database.

        Returns:
            True if the table exists, False otherwise.
        """
        query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (self.table_name,))
            return cursor.fetchone()[0]

    def drop_table(self):
        """Drop the table from the database."""
        query = f"DROP TABLE IF EXISTS {self.table_name} CASCADE"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def get_columns(self) -> list[str]:
        """Get list of column names in the table.

        Returns:
            List of column names.
        """
        query = (
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = %s ORDER BY ordinal_position"
        )
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (self.table_name,))
            return [row[0] for row in cursor.fetchall()]

    def create_index(
        self, columns: list[str], index_name: Optional[str] = None, unique: bool = False
    ):
        """Create an index on the specified columns.

        Args:
            columns: List of column names to index.
            index_name: Name for the index. If None, auto-generated.
            unique: Whether to create a unique index.
        """
        if index_name is None:
            index_name = f"idx_{self.table_name}_{'_'.join(columns)}"

        columns_str = ", ".join(columns)
        unique_str = "UNIQUE " if unique else ""
        query = f"CREATE {unique_str}INDEX IF NOT EXISTS {index_name} ON {self.table_name} ({columns_str})"

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def drop_index(self, index_name: str):
        """Drop an index from the table.

        Args:
            index_name: Name of the index to drop.
        """
        query = f"DROP INDEX IF EXISTS {index_name}"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
            conn.commit()

    def get_indexes(self) -> list[dict]:
        """Get list of indexes on the table.

        Returns:
            List of dictionaries with index information.
        """
        query = "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = %s"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (self.table_name,))
            return [{"name": row[0], "definition": row[1]} for row in cursor.fetchall()]


class AsyncTableSync:
    """Handles table synchronization between Pydantic models and PostgreSQL (async)."""

    def __init__(
        self,
        model,
        db_config: dict,
        pool_config: Optional[dict] = None,
        forensic: bool = False,
    ):
        """Initialize async table sync.

        Args:
            model: Pydantic BaseModel class.
            db_config: PostgreSQL connection configuration.
            pool_config: Optional pool configuration dictionary.
            forensic: Whether forensic audit columns are enabled.
        """
        self.model = model
        self.db_config = db_config
        self.pool_config = pool_config
        self.forensic = forensic
        self.table_name = getattr(model, "__tablename__", model.__name__.lower())

    async def _get_async_conn(self):
        """Get an async connection from the pool.

        Returns:
            Async connection wrapper.
        """
        return await get_async_connection(self.db_config)

    async def create_if_not_exists_async(self):
        """Create the table if it doesn't exist (async)."""
        field_defs = []
        if "id" not in self.model.model_fields:
            field_defs.append("id SERIAL PRIMARY KEY")

        for field, typ in self.model.model_fields.items():
            field_defs.append(f"{field} {get_sql_type(typ)}")

        if self.forensic:
            model_fields = set(self.model.model_fields.keys())
            if "id" not in model_fields:
                model_fields.add("id")
            for f_name, f_sql in FORENSIC_COLUMNS.items():
                if f_name not in model_fields:
                    field_defs.append(f"{f_name} {f_sql}")

        fields = ", ".join(field_defs)
        query = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({fields})"
        conn = await get_async_connection(self.db_config)
        async with conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
            await conn.commit()

    async def sync_with_model_async(self):
        """Sync the table with the Pydantic model, adding new columns if necessary (async)."""
        query = (
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
        )
        conn = await get_async_connection(self.db_config)
        async with conn, conn.cursor() as cursor:
            await cursor.execute(query, (self.table_name,))
            rows = await cursor.fetchall()
            existing_columns = {row[0] for row in rows}

        model_fields = set(self.model.model_fields.keys())
        if "id" not in model_fields:
            model_fields.add("id")

        if self.forensic:
            expected_fields = model_fields | set(FORENSIC_COLUMNS.keys())
        else:
            expected_fields = model_fields

        new_fields = expected_fields - existing_columns

        if new_fields:
            conn = await get_async_connection(self.db_config)
            async with conn:
                async with conn.cursor() as cursor:
                    for field in new_fields:
                        if field in FORENSIC_COLUMNS:
                            field_type = FORENSIC_COLUMNS[field]
                        elif field == "id":
                            field_type = "SERIAL PRIMARY KEY"
                        else:
                            field_type = f"{get_sql_type(self.model.model_fields[field])} DEFAULT NULL"
                        alter_query = f"ALTER TABLE {self.table_name} ADD COLUMN {field} {field_type}"
                        await cursor.execute(alter_query)
                await conn.commit()
