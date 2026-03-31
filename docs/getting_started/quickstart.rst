============
Quickstart
============

This guide will help you get started with wpostgresql in minutes.

Basic Usage
-----------

Create a Pydantic model and initialize the database connection:

.. code-block:: python

    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    class User(BaseModel):
        id: int
        name: str
        email: str

    db_config = {
        "dbname": "mydatabase",
        "user": "myuser",
        "password": "mypassword",
        "host": "localhost",
        "port": 5432,
    }

    db = WPostgreSQL(User, db_config)

CRUD Operations
----------------

Create:

.. code-block:: python

    db.insert(User(id=1, name="John Doe", email="john@example.com"))

Read:

.. code-block:: python

    all_users = db.get_all()
    john = db.get_by_field(name="John Doe")

Update:

.. code-block:: python

    db.update(1, User(id=1, name="John Smith", email="john.smith@example.com"))

Delete:

.. code-block:: python

    db.delete(1)

Async Operations
----------------

.. code-block:: python

    import asyncio

    async def main():
        await db.insert_async(User(id=2, name="Jane", email="jane@example.com"))
        users = await db.get_all_async()

    asyncio.run(main())

Next Steps
----------

* Read the :doc:`Configuration <configuration>` guide for database setup options
* Explore :doc:`../tutorials/crud_operations` for more detailed examples
* Check the :doc:`../api_reference/index` for complete API documentation