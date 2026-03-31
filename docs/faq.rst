===
FAQ
===

What is wpostgresql?
---------------------

wpostgresql is a lightweight PostgreSQL ORM that uses Pydantic models for schema definition and provides both synchronous and asynchronous database operations.

How does it differ from SQLAlchemy?
------------------------------------

wpostgresql is designed to be simpler and more Pythonic, leveraging Pydantic's type validation and automatic schema synchronization.

Does it support async operations?
----------------------------------

Yes! All CRUD operations have async equivalents (e.g., ``insert_async``, ``get_all_async``).

Is it production-ready?
------------------------

wpostgresql is currently in alpha (v0.3.0). It supports basic CRUD, transactions, pagination, and bulk operations. More features are planned.

How do I handle database migrations?
--------------------------------------

wpostgresql automatically synchronizes your model schema with the database. For more complex migrations, consider using a dedicated migration tool.

Can I use it with FastAPI?
---------------------------

Yes! Here's an example:

.. code-block:: python

    from fastapi import FastAPI
    from pydantic import BaseModel
    from wpostgresql import WPostgreSQL

    app = FastAPI()

    class Item(BaseModel):
        id: int
        name: str

    db = WPostgreSQL(Item, db_config)

    @app.post("/items/")
    def create_item(item: Item):
        db.insert(item)
        return item

How do I run tests?
-------------------

.. code-block:: bash

    pytest test/

Where can I get help?
---------------------

* GitHub Issues: https://github.com/wisrovi/wpostgresql/issues
* Documentation: https://wpostgresql.readthedocs.io