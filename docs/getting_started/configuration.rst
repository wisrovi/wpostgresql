==============
Configuration
==============

Database Configuration
-----------------------

wpostgresql uses a simple dictionary-based configuration system:

.. code-block:: python

    db_config = {
        "dbname": "your_database",
        "user": "your_user",
        "password": "your_password",
        "host": "localhost",
        "port": 5432,
    }

Environment Variables
---------------------

You can also use environment variables:

.. code-block:: python

    import os
    import wpostgresql

    db_config = {
        "dbname": os.getenv("POSTGRES_DB", "mydb"),
        "user": os.getenv("POSTGRES_USER", "user"),
        "password": os.getenv("POSTGRES_PASSWORD", "password"),
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
    }

Connection Pool Configuration
------------------------------

wpostgresql automatically manages connection pooling:

.. code-block:: python

    from wpostgresql.core.connection import ConnectionPool

    pool = ConnectionPool(
        "dbname=test user=admin password=secret",
        min_size=2,
        max_size=20,
    )

SSL Configuration
------------------

For secure connections:

.. code-block:: python

    db_config = {
        "dbname": "mydb",
        "user": "user",
        "password": "pass",
        "host": "localhost",
        "sslmode": "require",
    }

Testing Configuration
---------------------

Use a separate test database:

.. code-block:: python

    import os

    test_config = {
        "dbname": "test_" + os.getenv("POSTGRES_DB", "mydb"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST", "localhost"),
    }