"""Main repository class for PostgreSQL operations."""

import logging
import re
from typing import Any, Callable, Optional

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


# pylint: disable=too-many-public-methods
class WPostgreSQL:
    """PostgreSQL repository using Pydantic models.

    Provides a simple interface for CRUD operations on PostgreSQL tables,
    with automatic table creation and schema synchronization.

    Example:
        from pydantic import BaseModel
        from wpostgresql import WPostgreSQL

        class User(BaseModel):
            id: int
            name: str
            email: str

        db = WPostgreSQL(User, db_config)
        db.insert(User(id=1, name="John", email="john@example.com"))
    """

    def __init__(
        self,
        model: type[BaseModel],
        db_config: dict,
        pool_config: Optional[dict] = None,
    ):
        """Initialize the repository with a Pydantic model.

        Args:
            model: Pydantic BaseModel class defining the table schema.
            db_config: PostgreSQL connection configuration dictionary.
                Expected keys: dbname, user, password, host, port.
            pool_config: Optional pool configuration dictionary.
                Expected keys: min_size, max_size.
                Default: {"min_size": 2, "max_size": 20}
        """
        from wpostgresql.core.connection import DEFAULT_POOL_CONFIG

        self.model = model
        self.db_config = db_config
        self.pool_config = pool_config or DEFAULT_POOL_CONFIG
        self.table_name = getattr(model, "__tablename__", model.__name__.lower())
        self._sync = TableSync(model, db_config, self.pool_config)

        self._sync.create_if_not_exists()
        self._sync.sync_with_model()

    def insert(self, data: BaseModel) -> None:
        """Insert a new record into the database.

        Args:
            data: Pydantic model instance containing the data to insert.
        """
        data_dict = data.model_dump()
        fields = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))
        values = tuple(data_dict.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
            conn.commit()

    def get_all(self) -> list[BaseModel]:
        """Get all records from the table.

        Returns:
            List[BaseModel]: A list of model instances populated from the database.
        """
        query = f"SELECT * FROM {self.table_name}"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def get_by_field(self, **filters) -> list[BaseModel]:
        """Get records filtered by specified fields.

        Args:
            **filters: Keyword arguments mapping column names to filter values.

        Returns:
            List[BaseModel]: A list of matching model instances.
        """
        if not filters:
            return self.get_all()

        conditions = " AND ".join(f"{key} = %s" for key in filters)
        values = tuple(filters.values())
        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"

        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, values)
            rows = cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def update(self, record_id: int, data: BaseModel) -> None:
        """Update a record in the database.

        Args:
            record_id: The ID of the record to update.
            data: Pydantic model instance containing the new data.
        """
        data_dict = data.model_dump()
        fields = ", ".join(f"{key} = %s" for key in data_dict)
        values = tuple(data_dict.values()) + (record_id,)
        query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
            conn.commit()

    def delete(self, record_id: int) -> None:
        """Delete a record from the database by its ID.

        Args:
            record_id: The ID of the record to remove.
        """
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (record_id,))
            conn.commit()

    def _default_value(self, field: str) -> Any:
        """Get default value for a field when database value is NULL.

        Args:
            field: The name of the field.

        Returns:
            Any: A safe default value based on the field type.
        """
        field_type = self.model.model_fields[field].annotation
        if field_type is str:
            return ""
        if field_type is int:
            return 0
        if field_type is bool:
            return False
        return None

    def get_paginated(
        self,
        limit: int = 10,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> list[BaseModel]:
        """Get records with pagination and optional ordering.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            order_by: Optional column name for sorting.
            order_desc: Whether to sort in descending order.

        Returns:
            List[BaseModel]: A page of model instances.
        """
        validate_identifier(self.table_name)
        if order_by:
            validate_identifier(order_by)
            order_clause = f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'}"
        else:
            order_clause = ""

        query = f"SELECT * FROM {self.table_name}{order_clause} LIMIT %s OFFSET %s"

        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def get_page(self, page: int = 1, per_page: int = 10) -> list[BaseModel]:
        """Get records by page number.

        Args:
            page: The page number (starting from 1).
            per_page: Number of records per page.

        Returns:
            List[BaseModel]: A list of model instances for the requested page.
        """
        page = max(page, 1)
        per_page = max(per_page, 1)
        offset = (page - 1) * per_page
        return self.get_paginated(limit=per_page, offset=offset)

    def count(self) -> int:
        """Get total number of records in the table.

        Returns:
            int: The total count of records.
        """
        validate_identifier(self.table_name)
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        with get_connection(self.db_config) as conn, conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
        return result[0] if result else 0

    def insert_many(self, data_list: list[BaseModel]) -> None:
        """Insert multiple records in a single transaction.

        Args:
            data_list: A list of model instances to insert.
        """
        if not data_list:
            return

        data_dicts = [data.model_dump() for data in data_list]
        fields = ", ".join(data_dicts[0].keys())
        placeholders = ", ".join(["%s"] * len(data_dicts[0]))

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                for data_dict in data_dicts:
                    values = tuple(data_dict.values())
                    cursor.execute(query, values)
            conn.commit()

    def update_many(self, updates: list[tuple[BaseModel, int]]) -> int:
        """Update multiple records efficiently.

        Args:
            updates: A list of tuples containing (new_data_model, record_id).

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
                    fields = ", ".join(f"{key} = %s" for key in data_dict)
                    values = tuple(data_dict.values()) + (record_id,)
                    query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"
                    cursor.execute(query, values)
                    total_updated += cursor.rowcount
            conn.commit()

        return total_updated

    def delete_many(self, record_ids: list[int]) -> int:
        """Delete multiple records by their IDs.

        Args:
            record_ids: A list of IDs to remove.

        Returns:
            int: The number of records deleted.
        """
        if not record_ids:
            return 0

        validate_identifier(self.table_name)

        with get_connection(self.db_config) as conn:
            with conn.cursor() as cursor:
                for record_id in record_ids:
                    query = f"DELETE FROM {self.table_name} WHERE id = %s"
                    cursor.execute(query, (record_id,))
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

    async def insert_async(self, data: BaseModel) -> None:
        """Asynchronously insert a new record into the database.

        Args:
            data: Model instance containing data to insert.
        """
        data_dict = data.model_dump()
        fields = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))
        values = tuple(data_dict.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
        conn = await get_async_connection(self.db_config)
        async with conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
            await conn.commit()

    async def get_all_async(self) -> list[BaseModel]:
        """Asynchronously retrieve all records from the table.

        Returns:
            List[BaseModel]: List of model instances.
        """
        query = f"SELECT * FROM {self.table_name}"
        conn = await get_async_connection(self.db_config)
        async with conn, conn.cursor() as cursor:
            await cursor.execute(query)
            rows = await cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    async def get_by_field_async(self, **filters) -> list[BaseModel]:
        """Asynchronously get records filtered by specified fields.

        Args:
            **filters: Field names and values to filter by.

        Returns:
            List[BaseModel]: List of matching model instances.
        """
        if not filters:
            return await self.get_all_async()

        conditions = " AND ".join(f"{key} = %s" for key in filters)
        values = tuple(filters.values())
        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"

        conn = await get_async_connection(self.db_config)
        async with conn, conn.cursor() as cursor:
            await cursor.execute(query, values)
            rows = await cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    async def update_async(self, record_id: int, data: BaseModel) -> None:
        """Asynchronously update a record in the database.

        Args:
            record_id: ID of the record to update.
            data: Model instance with new data.
        """
        data_dict = data.model_dump()
        fields = ", ".join(f"{key} = %s" for key in data_dict)
        values = tuple(data_dict.values()) + (record_id,)
        query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"

        conn = await get_async_connection(self.db_config)
        async with conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, values)
            await conn.commit()

    async def delete_async(self, record_id: int) -> None:
        """Asynchronously delete a record from the database.

        Args:
            record_id: ID of the record to delete.
        """
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        conn = await get_async_connection(self.db_config)
        async with conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (record_id,))
            await conn.commit()

    async def get_paginated_async(
        self,
        limit: int = 10,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> list[BaseModel]:
        """Asynchronously get records with pagination and sorting.

        Args:
            limit: Max records.
            offset: Skip records.
            order_by: Column to sort.
            order_desc: Descending order if True.

        Returns:
            List[BaseModel]: A page of results.
        """
        validate_identifier(self.table_name)
        if order_by:
            validate_identifier(order_by)
            order_clause = f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'}"
        else:
            order_clause = ""

        query = f"SELECT * FROM {self.table_name}{order_clause} LIMIT %s OFFSET %s"

        conn = await get_async_connection(self.db_config)
        async with conn, conn.cursor() as cursor:
            await cursor.execute(query, (limit, offset))
            rows = await cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    async def get_page_async(self, page: int = 1, per_page: int = 10) -> list[BaseModel]:
        """Asynchronously get records by page number.

        Args:
            page: Page number (1-based).
            per_page: Records per page.

        Returns:
            List[BaseModel]: Page of results.
        """
        page = max(page, 1)
        per_page = max(per_page, 1)
        offset = (page - 1) * per_page
        return await self.get_paginated_async(limit=per_page, offset=offset)

    async def count_async(self) -> int:
        """Asynchronously count total records in the table.

        Returns:
            int: Total record count.
        """
        validate_identifier(self.table_name)
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        conn = await get_async_connection(self.db_config)
        async with conn, conn.cursor() as cursor:
            await cursor.execute(query)
            result = await cursor.fetchone()
        return result[0] if result else 0

    async def insert_many_async(self, data_list: list[BaseModel]) -> None:
        """Asynchronously insert multiple records in one transaction.

        Args:
            data_list: List of models to insert.
        """
        if not data_list:
            return

        data_dicts = [data.model_dump() for data in data_list]
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

    async def update_many_async(self, updates: list[tuple[BaseModel, int]]) -> int:
        """Asynchronously update multiple records.

        Args:
            updates: List of (model, id) tuples.

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
                    fields = ", ".join(f"{key} = %s" for key in data_dict)
                    values = tuple(data_dict.values()) + (record_id,)
                    query = f"UPDATE {self.table_name} SET {fields} WHERE id = %s"
                    await cursor.execute(query, values)
                    total_updated += cursor.rowcount
            await conn.commit()

        return total_updated

    async def delete_many_async(self, record_ids: list[int]) -> int:
        """Asynchronously delete multiple records by ID.

        Args:
            record_ids: List of IDs to delete.

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
                    query = f"DELETE FROM {self.table_name} WHERE id = %s"
                    await cursor.execute(query, (record_id,))
            await conn.commit()

        return len(record_ids)

    async def execute_transaction_async(self, operations: list[tuple[str, tuple]]) -> list[Any]:
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
                logger.info("Async transaction completed with %d operations", len(operations))
        except Exception as e:
            logger.error("Async transaction failed: %s", e)
            raise TransactionError(f"Async transaction failed: {e}") from e
        return results

    async def with_transaction_async(self, func: Callable[[AsyncTransaction], Any]) -> Any:
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
