.. _wpostgresql-get_all:

get_all method
==============

.. automethod:: wpostgresql.WPostgreSQL.get_all
   :noindex:
   :noindex-entry:

.. raw:: html

   <div class="section-separator"></div>

Description
-----------

Retrieve all records from the database table and return them as a list of Pydantic model instances.

Parameters
----------

None

Returns
-------

List[BaseModel]
   A list of model instances populated with data from the database.

Raises
------

SQLInjectionError
   If the table name contains invalid characters (security protection).
Exception
   For any database-related errors.

Examples
--------

Getting all records:

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

   # Get all users
   users = db.get_all()
   for user in users:
       print(f"{user.id}: {user.name} - {user.email}")

   # Get count
   print(f"Total users: {len(users)}")

See Also
--------

- :meth:`wpostgresql.WPostgreSQL.get_by_field` : Get records with filters
- :meth:`wpostgresql.WPostgreSQL.get_paginated` : Get records with pagination
- :meth:`wpostgresql.WPostgreSQL.get_all_async` : Asynchronous version