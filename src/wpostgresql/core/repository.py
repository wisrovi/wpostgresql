"""Main repository class for PostgreSQL operations."""

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional, Union

from pydantic import BaseModel

from wpostgresql.core.connection import (
    AsyncTransaction,
    Transaction,
    get_async_connection,
    get_connection,
    get_transaction,
)
from wpostgresql.core.sync import TableSync
from wpostgresql.exceptions import SQLInjectionError, TransactionError

logger = logging.getLogger(__name__)


def validate_identifier(identifier: str) -> None:
    """Validate SQL identifier to prevent SQL injection.

    Args:
        identifier: Table or column name to validate.

    Raises:
        SQLInjectionError: If identifier contains invalid characters.
    """
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        raise SQLInjectionError(f"Invalid identifier: {identifier}")


class ForensicModel(BaseModel):
    """Base Pydantic model with forensic audit fields for WPostgreSQL.

    Inheriting from this model automatically enables forensic mode in WPostgreSQL.
    """

    create_by: Optional[int] = 1
    create_in: Optional[datetime] = None
    update_by: Optional[int] = None
    update_in: Optional[datetime] = None
    delete_by: Optional[int] = None
    delete_in: Optional[datetime] = None
    status: int = 1


# pylint: disable=too-many-public-methods
class WPostgreSQL:
    """PostgreSQL repository using Pydantic models.

    Provides a simple and type-safe interface for CRUD operations on PostgreSQL tables,
    with automatic table creation, schema synchronization, and single/multi-table management.

    Single-table example:
        db = WPostgreSQL(User, db_config)
        db.insert(User(id=1, name="John", email="john@example.com"))

    Multi-table example:
        db = WPostgreSQL([User, Product, Order], db_config)
        db[User].insert(User(id=1, name="John", email="john@example.com"))
        db.product.get_all()
    """

    def __init__(
        self,
        target: Optional[
            Union[
                type[BaseModel],
                list[type[BaseModel]],
                tuple[type[BaseModel], ...],
                dict,
            ]
        ] = None,
        db_config: Optional[dict] = None,
        pool_config: Optional[dict] = None,
        forensic: Optional[bool] = None,
        models: Optional[
            Union[list[type[BaseModel]], tuple[type[BaseModel], ...]]
        ] = None,
        model: Optional[type[BaseModel]] = None,
    ):
        """Initialize WPostgreSQL repository or multitabla database manager.

        Args:
            target: Single Pydantic model class, list of model classes, or db_config dict.
            db_config: PostgreSQL connection configuration dictionary.
            pool_config: Optional connection pool configuration dictionary.
            forensic: Optional boolean to explicitly enable or disable forensic audit columns.
            models: Optional list of Pydantic model classes for multi-table mode.
            model: Optional single Pydantic model class for single-table mode.
        """
        from wpostgresql.core.connection import DEFAULT_POOL_CONFIG

        resolved_db_config = db_config
        resolved_models: Optional[list[type[BaseModel]]] = (
            list(models) if models is not None else None
        )
        resolved_model: Optional[type[BaseModel]] = model

        if isinstance(target, dict) and resolved_db_config is None:
            resolved_db_config = target
        elif isinstance(target, (list, tuple)):
            resolved_models = list(target)
        elif isinstance(target, type) and issubclass(target, BaseModel):
            resolved_model = target

        if resolved_db_config is None:
            raise ValueError(
                "db_config dictionary must be provided to initialize WPostgreSQL."
            )

        self.db_config = resolved_db_config
        self.pool_config = pool_config or DEFAULT_POOL_CONFIG
        self.forensic_setting = forensic

        self._repositories: dict[Union[type[BaseModel], str], "WPostgreSQL"] = {}
        self._repositories_by_name: dict[str, "WPostgreSQL"] = {}

        if resolved_models is not None:
            self.is_multi_table = True
            self.model = None
            self.table_name = None
            self.forensic = False
            self._sync = None
            for m in resolved_models:
                self.register_model(m)
        elif resolved_model is not None:
            self.is_multi_table = False
            self.model = resolved_model
            self.table_name = getattr(
                resolved_model, "__tablename__", resolved_model.__name__.lower()
            )

            if forensic is None:
                self.forensic = (
                    issubclass(resolved_model, ForensicModel)
                    if isinstance(resolved_model, type)
                    and issubclass(resolved_model, BaseModel)
                    else False
                )
            else:
                self.forensic = forensic

            self._sync = TableSync(
                resolved_model, self.db_config, self.pool_config, forensic=self.forensic
            )
            self._sync.create_if_not_exists()
            self._sync.sync_with_model()
            self._register_repository_references(resolved_model, self)
        else:
            self.is_multi_table = True
            self.model = None
            self.table_name = None
            self.forensic = False
            self._sync = None

    def register_model(
        self, model: type[BaseModel], forensic: Optional[bool] = None
    ) -> "WPostgreSQL":
        """Register a model and create/sync its table in multi-table mode.

        Args:
            model: Pydantic BaseModel class defining the table schema.
            forensic: Optional boolean to override forensic audit setting for this table.

        Returns:
            WPostgreSQL: The single-table repository instance for the registered model.
        """
        use_forensic = forensic if forensic is not None else self.forensic_setting
        repo = WPostgreSQL(
            model=model,
            db_config=self.db_config,
            pool_config=self.pool_config,
            forensic=use_forensic,
        )
        self._register_repository_references(model, repo)
        return repo

    def register_models(
        self,
        *models: Union[
            type[BaseModel], list[type[BaseModel]], tuple[type[BaseModel], ...]
        ],
    ) -> list["WPostgreSQL"]:
        """Register multiple models at once.

        Args:
            *models: Pydantic model classes or lists of model classes.

        Returns:
            list[WPostgreSQL]: Registered repository instances.
        """
        registered = []
        for item in models:
            if isinstance(item, (list, tuple)):
                for sub_m in item:
                    registered.append(self.register_model(sub_m))
            elif isinstance(item, type) and issubclass(item, BaseModel):
                registered.append(self.register_model(item))
        return registered

    def _register_repository_references(
        self, model: type[BaseModel], repo: "WPostgreSQL"
    ) -> None:
        table_name = getattr(model, "__tablename__", model.__name__.lower())
        model_name = model.__name__.lower()

        self._repositories[model] = repo
        self._repositories[model_name] = repo
        self._repositories[table_name] = repo
        self._repositories_by_name[model_name] = repo
        self._repositories_by_name[table_name] = repo

    def __getitem__(self, item: Union[type[BaseModel], str]) -> "WPostgreSQL":
        """Access table repository using Pydantic model class or table/model name.

        Example:
            db[User].insert(...)
            db["user"].get_all()
        """
        if isinstance(item, type) and issubclass(item, BaseModel):
            if item in self._repositories:
                return self._repositories[item]
        elif isinstance(item, str):
            item_lower = item.lower()
            if item_lower in self._repositories:
                return self._repositories[item_lower]

        if not self.is_multi_table and self.model:
            if item == self.model or (
                isinstance(item, str)
                and item.lower() in (self.table_name, self.model.__name__.lower())
            ):
                return self

        raise KeyError(
            f"Model or table '{item}' is not registered in WPostgreSQL multitabla registry."
        )

    def __getattr__(self, name: str) -> Any:
        """Access table repository as a direct attribute.

        Example:
            db.user.insert(...)
            db.product.get_all()
        """
        if name.startswith("_"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        repositories = getattr(self, "_repositories_by_name", {})
        name_lower = name.lower()
        if name_lower in repositories:
            return repositories[name_lower]

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def table(self, item: Union[type[BaseModel], str]) -> "WPostgreSQL":
        """Get repository for a specific model or table name."""
        return self[item]

    def get_repository(self, item: Union[type[BaseModel], str]) -> "WPostgreSQL":
        """Get repository for a specific model or table name."""
        return self[item]

    def _default_value(self, field: str) -> Any:
        """Get default value for a field when database value is NULL.

        Args:
            field: The name of the field.

        Returns:
            Any: A safe default value based on the field type.
        """
        field_info = self.model.model_fields.get(field)
        if not field_info:
            return None
        field_type = field_info.annotation
        if field_type is str:
            return ""
        if field_type is int:
            return 0
        if field_type is bool:
            return False
        return None

    def _map_row_to_model(self, colnames: list[str], row: tuple) -> BaseModel:
        """Map database row values to a Pydantic model instance."""
        row_dict = dict(zip(colnames, row))
        kwargs = {}
        for key in self.model.model_fields.keys():
            if key in row_dict and row_dict[key] is not None:
                kwargs[key] = row_dict[key]
            else:
                kwargs[key] = self._default_value(key)
        return self.model(**kwargs)

    def insert(self, data: BaseModel, user_id: Optional[int] = None) -> None:
        """Insert a new record into the database.

        Args:
            data: Pydantic model instance containing the data to insert.
            user_id: Optional ID of the user performing the insertion for forensic tracking.
        """
        if getattr(self, "is_multi_table", False):
            model_cls = type(data)
            if model_cls in self._repositories:
                return self._repositories[model_cls].insert(data, user_id=user_id)
            raise KeyError(
                f"No registered repository found for model type '{model_cls.__name__}'."
            )

        data_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        if self.forensic:
            data_dict.setdefault(
                "create_by",
                user_id if user_id is not None else getattr(data, "create_by", 1) or 1,
            )
            data_dict.setdefault("create_in", datetime.now(timezone.utc))
            data_dict.setdefault("status", getattr(data, "status", 1) or 1)

        fields = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))
        values = tuple(data_dict.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
            conn.commit()

    def get_all(self, include_deleted: bool = False) -> list[BaseModel]:
        """Get all records from the table.

        Args:
            include_deleted: If True, includes soft-deleted records (status=99) in forensic mode.

        Returns:
            List[BaseModel]: A list of model instances populated from the database.
        """
        where_clause = (
            " WHERE status != 99" if (self.forensic and not include_deleted) else ""
        )
        query = f"SELECT * FROM {self.table_name}{where_clause}"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            colnames = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )

        return [self._map_row_to_model(colnames, row) for row in rows]

    def get_by_field(self, include_deleted: bool = False, **filters) -> list[BaseModel]:
        """Get records filtered by specified fields.

        Args:
            include_deleted: If True, includes soft-deleted records in forensic mode.
            **filters: Keyword arguments mapping column names to filter values.

        Returns:
            List[BaseModel]: A list of matching model instances.
        """
        conditions = []
        values = []

        if self.forensic and not include_deleted and "status" not in filters:
            conditions.append("status != %s")
            values.append(99)

        for key, val in filters.items():
            conditions.append(f"{key} = %s")
            values.append(val)

        where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT * FROM {self.table_name}{where_clause}"

        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, tuple(values))
            rows = cursor.fetchall()
            colnames = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )

        return [self._map_row_to_model(colnames, row) for row in rows]

    def update(
        self, record_id: int, data: BaseModel, user_id: Optional[int] = None
    ) -> None:
        """Update a record in the database.

        Args:
            record_id: The ID of the record to update.
            data: Pydantic model instance containing the new data.
            user_id: Optional ID of the user performing the update for forensic tracking.
        """
        data_dict = data.model_dump()
        if self.forensic:
            data_dict["update_by"] = user_id if user_id is not None else 1
            data_dict["update_in"] = datetime.now(timezone.utc)

        fields = ", ".join(f"{key} = %s" for key in data_dict)
        values = tuple(data_dict.values()) + (record_id,)
        query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
            conn.commit()

    def delete(
        self, record_id: int, user_id: Optional[int] = None, hard: bool = False
    ) -> None:
        """Delete a record from the database by its ID.

        Args:
            record_id: The ID of the record to remove.
            user_id: Optional ID of the user performing the deletion for forensic tracking.
            hard: If True, performs a physical DELETE FROM query instead of soft-delete (status=99).
        """
        if self.forensic and not hard:
            query = f"UPDATE {self.table_name} SET status = 99, delete_by = %s, delete_in = %s WHERE id = %s"
            values = (
                user_id if user_id is not None else 1,
                datetime.now(timezone.utc),
                record_id,
            )
        else:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            values = (record_id,)

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
            conn.commit()

    def get_paginated(
        self,
        limit: int = 10,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
    ) -> list[BaseModel]:
        """Get records with pagination and optional ordering.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            order_by: Optional column name for sorting.
            order_desc: Whether to sort in descending order.
            include_deleted: Whether to include soft-deleted records in forensic mode.

        Returns:
            List[BaseModel]: A page of model instances.
        """
        validate_identifier(self.table_name)
        where_clause = (
            " WHERE status != 99" if (self.forensic and not include_deleted) else ""
        )

        if order_by:
            validate_identifier(order_by)
            order_clause = f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'}"
        else:
            order_clause = ""

        query = f"SELECT * FROM {self.table_name}{where_clause}{order_clause} LIMIT %s OFFSET %s"

        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()
            colnames = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )

        return [self._map_row_to_model(colnames, row) for row in rows]

    def get_page(
        self, page: int = 1, per_page: int = 10, include_deleted: bool = False
    ) -> list[BaseModel]:
        """Get records by page number.

        Args:
            page: The page number (starting from 1).
            per_page: Number of records per page.
            include_deleted: Whether to include soft-deleted records in forensic mode.

        Returns:
            List[BaseModel]: A list of model instances for the requested page.
        """
        page = max(page, 1)
        per_page = max(per_page, 1)
        offset = (page - 1) * per_page
        return self.get_paginated(
            limit=per_page, offset=offset, include_deleted=include_deleted
        )

    def count(self, include_deleted: bool = False) -> int:
        """Get total number of records in the table.

        Args:
            include_deleted: Whether to include soft-deleted records in forensic mode.

        Returns:
            int: The total count of records.
        """
        validate_identifier(self.table_name)
        where_clause = (
            " WHERE status != 99" if (self.forensic and not include_deleted) else ""
        )
        query = f"SELECT COUNT(*) FROM {self.table_name}{where_clause}"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
        return result[0] if result else 0

    def insert_many(
        self, data_list: list[BaseModel], user_id: Optional[int] = None
    ) -> None:
        """Insert multiple records in a single transaction.

        Args:
            data_list: A list of model instances to insert.
            user_id: Optional user ID performing insertion in forensic mode.
        """
        if not data_list:
            return

        data_dicts = []
        for data in data_list:
            d = {k: v for k, v in data.model_dump().items() if v is not None}
            if self.forensic:
                d.setdefault(
                    "create_by",
                    (
                        user_id
                        if user_id is not None
                        else getattr(data, "create_by", 1) or 1
                    ),
                )
                d.setdefault("create_in", datetime.now(timezone.utc))
                d.setdefault("status", getattr(data, "status", 1) or 1)
            data_dicts.append(d)

        fields = ", ".join(data_dicts[0].keys())
        placeholders = ", ".join(["%s"] * len(data_dicts[0]))

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                for data_dict in data_dicts:
                    values = tuple(data_dict.values())
                    cursor.execute(query, values)
            conn.commit()

    def update_many(
        self, updates: list[tuple[BaseModel, int]], user_id: Optional[int] = None
    ) -> int:
        """Update multiple records efficiently.

        Args:
            updates: A list of tuples containing (new_data_model, record_id).
            user_id: Optional user ID performing updates in forensic mode.

        Returns:
            int: The total number of records updated.
        """
        if not updates:
            return 0

        validate_identifier(self.table_name)
        total_updated = 0

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                for data, record_id in updates:
                    data_dict = data.model_dump()
                    if self.forensic:
                        data_dict["update_by"] = user_id if user_id is not None else 1
                        data_dict["update_in"] = datetime.now(timezone.utc)
                    fields = ", ".join(f"{key} = %s" for key in data_dict)
                    values = tuple(data_dict.values()) + (record_id,)
                    query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"
                    cursor.execute(query, values)
                    total_updated += cursor.rowcount
            conn.commit()

        return total_updated

    def delete_many(
        self, record_ids: list[int], user_id: Optional[int] = None, hard: bool = False
    ) -> int:
        """Delete multiple records by their IDs.

        Args:
            record_ids: A list of IDs to remove.
            user_id: Optional user ID performing deletion in forensic mode.
            hard: If True, performs physical DELETE FROM queries instead of soft-delete.

        Returns:
            int: The number of records deleted.
        """
        if not record_ids:
            return 0

        validate_identifier(self.table_name)

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                for record_id in record_ids:
                    if self.forensic and not hard:
                        query = f"UPDATE {self.table_name} SET status = 99, delete_by = %s, delete_in = %s WHERE id = %s"
                        values = (
                            user_id if user_id is not None else 1,
                            datetime.now(timezone.utc),
                            record_id,
                        )
                    else:
                        query = f"DELETE FROM {self.table_name} WHERE id = %s"
                        values = (record_id,)
                    cursor.execute(query, values)
            conn.commit()

        return len(record_ids)

    def execute_transaction(self, operations: list[tuple[str, tuple]]) -> list[Any]:
        """Execute multiple SQL operations in a single transaction.

        Args:
            operations: A list of (sql_query, values_tuple) to execute.

        Returns:
            List[Any]: Results of the operations that returned data.

        Raises:
            TransactionError: If the transaction fails and is rolled back.
        """
        results = []
        try:
            with get_transaction(self.db_config) as txn:
                for query, values in operations:
                    result = txn.execute(query, values)
                    if result is not None:
                        results.append(result)
                txn.commit()
                logger.info("Transaction completed with %d operations", len(operations))
        except Exception as e:
            logger.error("Transaction failed: %s", e)
            raise TransactionError(f"Transaction failed: {e}") from e
        return results

    def with_transaction(self, func: Callable[[Transaction], Any]) -> Any:
        """Execute a custom function within a transaction block.

        Args:
            func: A callable that accepts a Transaction instance.

        Returns:
            Any: The return value of the provided function.

        Raises:
            TransactionError: If the function raises an exception.
        """
        try:
            with get_transaction(self.db_config) as txn:
                result = func(txn)
                txn.commit()
                logger.info("Transaction completed successfully")
                return result
        except Exception as e:
            logger.error("Transaction failed: %s", e)
            raise TransactionError(f"Transaction failed: {e}") from e

    async def insert_async(
        self, data: BaseModel, user_id: Optional[int] = None
    ) -> None:
        """Asynchronously insert a new record into the database.

        Args:
            data: Model instance containing data to insert.
            user_id: Optional user ID for forensic tracking.
        """
        if getattr(self, "is_multi_table", False):
            model_cls = type(data)
            if model_cls in self._repositories:
                return await self._repositories[model_cls].insert_async(
                    data, user_id=user_id
                )
            raise KeyError(
                f"No registered repository found for model type '{model_cls.__name__}'."
            )

        data_dict = {k: v for k, v in data.model_dump().items() if v is not None}
        if self.forensic:
            data_dict.setdefault(
                "create_by",
                user_id if user_id is not None else getattr(data, "create_by", 1) or 1,
            )
            data_dict.setdefault("create_in", datetime.now(timezone.utc))
            data_dict.setdefault("status", getattr(data, "status", 1) or 1)

        fields = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))
        values = tuple(data_dict.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
        conn = await get_async_connection(self.db_config)
        async with conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
            await conn.commit()

    async def get_all_async(self, include_deleted: bool = False) -> list[BaseModel]:
        """Asynchronously retrieve all records from the table.

        Args:
            include_deleted: If True, includes soft-deleted records in forensic mode.

        Returns:
            List[BaseModel]: List of model instances.
        """
        where_clause = (
            " WHERE status != 99" if (self.forensic and not include_deleted) else ""
        )
        query = f"SELECT * FROM {self.table_name}{where_clause}"
        conn = await get_async_connection(self.db_config)
        async with conn, conn.cursor() as cursor:
            await cursor.execute(query)
            rows = await cursor.fetchall()
            colnames = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )

        return [self._map_row_to_model(colnames, row) for row in rows]

    async def get_by_field_async(
        self, include_deleted: bool = False, **filters
    ) -> list[BaseModel]:
        """Asynchronously get records filtered by specified fields.

        Args:
            include_deleted: If True, includes soft-deleted records in forensic mode.
            **filters: Field names and values to filter by.

        Returns:
            List[BaseModel]: List of matching model instances.
        """
        conditions = []
        values = []

        if self.forensic and not include_deleted and "status" not in filters:
            conditions.append("status != %s")
            values.append(99)

        for key, val in filters.items():
            conditions.append(f"{key} = %s")
            values.append(val)

        where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT * FROM {self.table_name}{where_clause}"

        conn = await get_async_connection(self.db_config)
        async with conn, conn.cursor() as cursor:
            await cursor.execute(query, tuple(values))
            rows = await cursor.fetchall()
            colnames = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )

        return [self._map_row_to_model(colnames, row) for row in rows]

    async def update_async(
        self, record_id: int, data: BaseModel, user_id: Optional[int] = None
    ) -> None:
        """Asynchronously update a record in the database.

        Args:
            record_id: ID of the record to update.
            data: Model instance with new data.
            user_id: Optional user ID performing update for forensic tracking.
        """
        data_dict = data.model_dump()
        if self.forensic:
            data_dict["update_by"] = user_id if user_id is not None else 1
            data_dict["update_in"] = datetime.now(timezone.utc)

        fields = ", ".join(f"{key} = %s" for key in data_dict)
        values = tuple(data_dict.values()) + (record_id,)
        query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"

        conn = await get_async_connection(self.db_config)
        async with conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
            await conn.commit()

    async def delete_async(
        self, record_id: int, user_id: Optional[int] = None, hard: bool = False
    ) -> None:
        """Asynchronously delete a record from the database.

        Args:
            record_id: ID of the record to delete.
            user_id: Optional user ID for forensic tracking.
            hard: If True, performs physical DELETE FROM queries instead of soft-delete.
        """
        if self.forensic and not hard:
            query = f"UPDATE {self.table_name} SET status = 99, delete_by = %s, delete_in = %s WHERE id = %s"
            values = (
                user_id if user_id is not None else 1,
                datetime.now(timezone.utc),
                record_id,
            )
        else:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            values = (record_id,)

        conn = await get_async_connection(self.db_config)
        async with conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
            await conn.commit()

    async def get_paginated_async(
        self,
        limit: int = 10,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        include_deleted: bool = False,
    ) -> list[BaseModel]:
        """Asynchronously get records with pagination and sorting.

        Args:
            limit: Max records.
            offset: Skip records.
            order_by: Column to sort.
            order_desc: Descending order if True.
            include_deleted: Whether to include soft-deleted records in forensic mode.

        Returns:
            List[BaseModel]: A page of results.
        """
        validate_identifier(self.table_name)
        where_clause = (
            " WHERE status != 99" if (self.forensic and not include_deleted) else ""
        )

        if order_by:
            validate_identifier(order_by)
            order_clause = f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'}"
        else:
            order_clause = ""

        query = f"SELECT * FROM {self.table_name}{where_clause}{order_clause} LIMIT %s OFFSET %s"

        conn = await get_async_connection(self.db_config)
        async with conn, conn.cursor() as cursor:
            await cursor.execute(query, (limit, offset))
            rows = await cursor.fetchall()
            colnames = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )

        return [self._map_row_to_model(colnames, row) for row in rows]

    async def get_page_async(
        self, page: int = 1, per_page: int = 10, include_deleted: bool = False
    ) -> list[BaseModel]:
        """Asynchronously get records by page number.

        Args:
            page: Page number (1-based).
            per_page: Records per page.
            include_deleted: Whether to include soft-deleted records in forensic mode.

        Returns:
            List[BaseModel]: Page of results.
        """
        page = max(page, 1)
        per_page = max(per_page, 1)
        offset = (page - 1) * per_page
        return await self.get_paginated_async(
            limit=per_page, offset=offset, include_deleted=include_deleted
        )

    async def count_async(self, include_deleted: bool = False) -> int:
        """Asynchronously count total records in the table.

        Args:
            include_deleted: Whether to include soft-deleted records in forensic mode.

        Returns:
            int: Total record count.
        """
        validate_identifier(self.table_name)
        where_clause = (
            " WHERE status != 99" if (self.forensic and not include_deleted) else ""
        )
        query = f"SELECT COUNT(*) FROM {self.table_name}{where_clause}"
        conn = await get_async_connection(self.db_config)
        async with conn, conn.cursor() as cursor:
            await cursor.execute(query)
            result = await cursor.fetchone()
        return result[0] if result else 0

    async def insert_many_async(
        self, data_list: list[BaseModel], user_id: Optional[int] = None
    ) -> None:
        """Asynchronously insert multiple records in one transaction.

        Args:
            data_list: List of models to insert.
            user_id: Optional user ID for forensic tracking.
        """
        if not data_list:
            return

        data_dicts = []
        for data in data_list:
            d = {k: v for k, v in data.model_dump().items() if v is not None}
            if self.forensic:
                d.setdefault(
                    "create_by",
                    (
                        user_id
                        if user_id is not None
                        else getattr(data, "create_by", 1) or 1
                    ),
                )
                d.setdefault("create_in", datetime.now(timezone.utc))
                d.setdefault("status", getattr(data, "status", 1) or 1)
            data_dicts.append(d)

        fields = ", ".join(data_dicts[0].keys())
        placeholders = ", ".join(["%s"] * len(data_dicts[0]))

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"

        conn = await get_async_connection(self.db_config)
        async with conn:
            async with conn.cursor() as cursor:
                for data_dict in data_dicts:
                    values = tuple(data_dict.values())
                    await cursor.execute(query, values)
            await conn.commit()

    async def update_many_async(
        self, updates: list[tuple[BaseModel, int]], user_id: Optional[int] = None
    ) -> int:
        """Asynchronously update multiple records.

        Args:
            updates: List of (model, id) tuples.
            user_id: Optional user ID for forensic tracking.

        Returns:
            int: Number of records updated.
        """
        if not updates:
            return 0

        validate_identifier(self.table_name)
        total_updated = 0

        conn = await get_async_connection(self.db_config)
        async with conn:
            async with conn.cursor() as cursor:
                for data, record_id in updates:
                    data_dict = data.model_dump()
                    if self.forensic:
                        data_dict["update_by"] = user_id if user_id is not None else 1
                        data_dict["update_in"] = datetime.now(timezone.utc)
                    fields = ", ".join(f"{key} = %s" for key in data_dict)
                    values = tuple(data_dict.values()) + (record_id,)
                    query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"
                    await cursor.execute(query, values)
                    total_updated += cursor.rowcount
            await conn.commit()

        return total_updated

    async def delete_many_async(
        self, record_ids: list[int], user_id: Optional[int] = None, hard: bool = False
    ) -> int:
        """Asynchronously delete multiple records by ID.

        Args:
            record_ids: List of IDs to delete.
            user_id: Optional user ID for forensic tracking.
            hard: If True, performs physical DELETE FROM queries.

        Returns:
            int: Number of IDs deleted.
        """
        if not record_ids:
            return 0

        validate_identifier(self.table_name)

        conn = await get_async_connection(self.db_config)
        async with conn:
            async with conn.cursor() as cursor:
                for record_id in record_ids:
                    if self.forensic and not hard:
                        query = f"UPDATE {self.table_name} SET status = 99, delete_by = %s, delete_in = %s WHERE id = %s"
                        values = (
                            user_id if user_id is not None else 1,
                            datetime.now(timezone.utc),
                            record_id,
                        )
                    else:
                        query = f"DELETE FROM {self.table_name} WHERE id = %s"
                        values = (record_id,)
                    await cursor.execute(query, values)
            conn.commit()

        return len(record_ids)

    async def execute_transaction_async(
        self, operations: list[tuple[str, tuple]]
    ) -> list[Any]:
        """Asynchronously execute multiple SQL operations in one transaction.

        Args:
            operations: List of (query, values).

        Returns:
            List[Any]: Results of queries.
        """
        results = []
        try:
            conn = await get_async_connection(self.db_config)
            async with conn:
                async with conn.cursor() as cursor:
                    for query, values in operations:
                        await cursor.execute(query, values)
                        if cursor.description:
                            result = await cursor.fetchall()
                            results.append(result)
                await conn.commit()
                logger.info(
                    "Async transaction completed with %d operations", len(operations)
                )
        except Exception as e:
            logger.error("Async transaction failed: %s", e)
            raise TransactionError(f"Async transaction failed: {e}") from e
        return results

    async def with_transaction_async(
        self, func: Callable[[AsyncTransaction], Any]
    ) -> Any:
        """Asynchronously execute a custom function in a transaction.

        Args:
            func: Async function accepting AsyncTransaction.

        Returns:
            Any: Function result.
        """
        try:
            conn = await get_async_connection(self.db_config)
            async with conn:
                txn = AsyncTransaction(self.db_config)
                txn.conn = conn
                result = await func(txn)
                await txn.commit()
                logger.info("Async transaction completed successfully")
                return result
        except Exception as e:
            logger.error("Async transaction failed: %s", e)
            raise TransactionError(f"Async transaction failed: {e}") from e

    def backup_to_sqlite(
        self, sqlite_path: Union[str, Path], update: bool = False
    ) -> int:
        """Backup table records to an SQLite database using wsqlite.

        Args:
            sqlite_path: Path to target SQLite database file.
            update: If True, updates existing SQLite database table in place without replacing file.
                    If False (default), creates a temporary backup file and atomically replaces destination file.

        Returns:
            int: Number of records backed up.
        """
        from wpostgresql.core.backup import backup_to_sqlite as _backup_to_sqlite

        return _backup_to_sqlite(self, sqlite_path, update=update)

    async def backup_to_sqlite_async(
        self, sqlite_path: Union[str, Path], update: bool = False
    ) -> int:
        """Asynchronously backup table records to an SQLite database using wsqlite.

        Args:
            sqlite_path: Path to target SQLite database file.
            update: If True, updates existing SQLite database table in place without replacing file.
                    If False (default), creates a temporary backup file and atomically replaces destination file.

        Returns:
            int: Number of records backed up.
        """
        from wpostgresql.core.backup import (
            backup_to_sqlite_async as _backup_to_sqlite_async,
        )

        return await _backup_to_sqlite_async(self, sqlite_path, update=update)
