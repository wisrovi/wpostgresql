.. _wpostgresql-insert_many:

insert_many method
==================

.. automethod:: wpostgresql.WPostgreSQL.insert_many
   :noindex:
   :noindex-entry:

.. raw:: html

   <div class="section-separator"></div>

Description
-----------

Insert multiple records into the database in a single transaction. This method is more efficient than calling ``insert`` multiple times in a loop.

Parameters
----------

data_list : List[BaseModel]
   A list of Pydantic model instances to insert.

Returns
-------

None

Raises
------

ValidationError
   If any data fails Pydantic validation.
SQLInjectionError
   If the table name contains invalid characters (security protection).
Exception
   For any database-related errors.

Examples
--------

Inserting multiple records:

.. code-block:: python

   from pydantic import BaseModel
   from wpostgresql import WPostgreSQL

   class User(BaseModel):
       id: int
       name: str
       email: str

   db_config = {
       "dbname": "mydb",
       "user": "postgres",
       "password": "secret",
       "host": "localhost",
       "port": 5432,
   }

   db = WPostgreSQL(User, db_config)

   users = [
       User(id=1, name="Alice", email="alice@example.com"),
       User(id=2, name="Bob", email="bob@example.com"),
       User(id=3, name="Charlie", email="charlie@example.com"),
   ]

   db.insert_many(users)

   # Verify insertion
   print(f"Inserted {len(users)} records")

See Also
--------

- :meth:`wpostgresql.WPostgreSQL.insert` : Insert a single record
- :meth:`wpostgresql.WPostgreSQL.insert_many_async` : Asynchronous version
- :meth:`wpostgresql.WPostgreSQL.update_many` : Update multiple records