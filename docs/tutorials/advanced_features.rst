=================
Advanced Features
=================

SQL Injection Prevention
-------------------------

All identifiers are automatically validated to prevent SQL injection:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL
    from wpostgresql.exceptions import SQLInjectionError

    db_config = {
        "dbname": "wpostgresql",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432,
    }

    class Person(BaseModel):
        id: int
        name: str
        age: int

    db = WPostgreSQL(Person, db_config)

    # This will be blocked
    try:
        db.get_by_field(**{"invalid; DROP TABLE users;--": "value"})
    except SQLInjectionError as e:
        print(f"Blocked SQL injection attempt: {e}")

    # Valid field names work normally
    valid_users = db.get_by_field(name="John")

Custom Field Handling with Pydantic
------------------------------------

Leverage Pydantic's validation features:

.. code-block:: python

    from pydantic import BaseModel, Field, field_validator
    from typing import Optional

    class User(BaseModel):
        id: int
        name: str = Field(max_length=100)
        email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
        age: Optional[int] = Field(ge=0, le=150)
        is_active: bool = True
        created_at: Optional[str] = None

        @field_validator('name')
        @classmethod
        def name_must_be_capitalized(cls, v):
            if not v[0].isupper():
                raise ValueError('Name must start with capital letter')
            return v

    db = WPostgreSQL(User, db_config)

    # This will validate before inserting
    valid_user = User(id=1, name="John", email="john@example.com", age=25)
    db.insert(valid_user)

    # This will fail validation
    try:
        invalid_user = User(id=2, name="john", email="invalid", age=25)
    except Exception as e:
        print(f"Validation error: {e}")

Connection Pool Management
---------------------------

wpostgresql uses automatic connection pooling. Here's how to manage it:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL
    from wpostgresql.core.connection import (
        get_connection,
        get_async_connection,
        close_global_pools,
    )

    db_config = {
        "dbname": "wpostgresql",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
    }

    class Person(BaseModel):
        id: int
        name: str
        age: int

    # Automatic pooling (default)
    db = WPostgreSQL(Person, db_config)

    # Use get_connection directly for raw SQL
    with get_connection(db_config) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM person WHERE age > %s", (25,))
        results = cursor.fetchall()
        for row in results:
            print(f"  {row}")

    # Clean up pools when done (e.g., at application shutdown)
    close_global_pools()
    print("Pools closed")

Connection Pooling - Advanced
------------------------------

Custom pool configuration for high-performance scenarios:

.. code-block:: python

    from wpostgresql import WPostgreSQL
    from wpostgresql.core.connection import ConnectionManager, close_global_pools
    from pydantic import BaseModel

    db_config = {
        "dbname": "wpostgresql",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
    }

    class Person(BaseModel):
        id: int
        name: str
        age: int

    # Create custom pool with specific settings
    pool = ConnectionManager(
        db_config,
        min_connections=5,
        max_connections=50
    )

    # Use pool directly
    conn = pool.get_connection()
    print(f"Got connection from pool: {conn}")

    # Release back to pool
    pool.release_connection(conn)

    # Close pool when done
    pool.close_all()

    # Or close all global pools
    close_global_pools()

Raw SQL Execution
-----------------

Execute raw SQL when you need more control:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL
    from wpostgresql.core.connection import get_connection

    db_config = {
        "dbname": "wpostgresql",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
    }

    class Person(BaseModel):
        id: int
        name: str
        age: int

    db = WPostgreSQL(Person, db_config)

    # Simple query
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM person")
            rows = cursor.fetchall()
            print("All records:")
            for row in rows:
                print(f"  {row}")

    # Query with parameters
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM person WHERE age > %s", (26,))
            rows = cursor.fetchall()
            print("\nPeople older than 26:")
            for row in rows:
                print(f"  {row}")

    # INSERT with RETURNING
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO person (name, age) VALUES (%s, %s) RETURNING id, name",
                ("Charlie", 35)
            )
            row = cursor.fetchone()
            print(f"\nInserted: id={row[0]}, name={row[1]}")
        conn.commit()

    # UPDATE with RETURNING
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE person SET age = %s WHERE name = %s RETURNING id, name, age",
                (36, "Charlie")
            )
            row = cursor.fetchone()
            print(f"Updated: {row}")
        conn.commit()

    # DELETE with RETURNING
    with get_connection(db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM person WHERE name = %s RETURNING id, name", ("Bob",))
            row = cursor.fetchone()
            print(f"Deleted: {row}")
        conn.commit()

Logging
-------

Enable detailed logging for debugging:

.. code-block:: python

    import logging
    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("wpostgresql")
    logger.setLevel(logging.DEBUG)

    # Also set psycopg logging
    psycopg_logger = logging.getLogger("psycopg")
    psycopg_logger.setLevel(logging.DEBUG)

    class Person(BaseModel):
        id: int
        name: str
        age: int

    db = WPostgreSQL(Person, db_config)

    # Operations will now be logged
    db.insert(Person(id=1, name="Test", age=25))
    people = db.get_all()

    # Check logs for:
    # - Connection pool creation
    # - SQL queries executed
    # - Transaction commits/rollbacks

Logging Configuration with Loguru
----------------------------------

Use Loguru for more modern logging:

.. code-block:: python

    from loguru import logger
    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    # Configure Loguru
    logger.add("wpostgresql.log", rotation="500 MB", retention="10 days")

    class Person(BaseModel):
        id: int
        name: str
        age: int

    db = WPostgreSQL(Person, db_config)

    logger.info("Starting database operations")
    db.insert(Person(id=1, name="John", age=30))
    logger.info("Insert complete")

    people = db.get_all()
    logger.info(f"Retrieved {len(people)} people")

CLI Usage
---------

The package includes a CLI for common operations:

.. code-block:: bash

    # Show help
    wpostgresql --help

    # Initialize a new database with a model
    wpostgresql init --config db_config.json

    # Sync schema
    wpostgresql sync --model myapp.models

    # Show version
    wpostgresql --version

Error Handling
--------------

Proper error handling for production applications:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL
    from wpostgresql.exceptions import (
        WPostgreSQLError,
        ConnectionError,
        OperationError,
        TransactionError,
        SQLInjectionError,
    )

    db_config = {
        "dbname": "wpostgresql",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
    }

    class Person(BaseModel):
        id: int
        name: str
        age: int

    try:
        db = WPostgreSQL(Person, db_config)
    except ConnectionError as e:
        print(f"Failed to connect: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    try:
        db.insert(Person(id=1, name="John", age=30))
    except OperationError as e:
        print(f"Operation failed: {e}")

    try:
        db.execute_transaction([
            ("INVALID SQL", None),
        ])
    except TransactionError as e:
        print(f"Transaction failed: {e}")

Type Hints and IDE Support
--------------------------

wpostgresql is fully typed for IDE support:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class Person(BaseModel):
        id: int
        name: str
        age: int

    db: WPostgreSQL = WPostgreSQL(Person, db_config)

    # IDE will suggest methods
    # - insert()
    # - get_all()
    # - get_by_field()
    # - update()
    # - delete()
    # - etc.

    # Return types are clear
    people: list[Person] = db.get_all()
    person: list[Person] = db.get_by_field(name="John")
    count: int = db.count()

    # Async methods
    async def get_people() -> list[Person]:
        return await db.get_all_async()