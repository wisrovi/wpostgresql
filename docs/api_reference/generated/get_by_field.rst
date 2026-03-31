.. _wpostgresql-get_by_field:

get_by_field method
===================

.. automethod:: wpostgresql.WPostgreSQL.get_by_field
   :noindex:
   :noindex-entry:

.. raw:: html

   <div class="section-separator"></div>

Description
-----------

Retrieve records from the database that match the specified field filters and return them as a list of Pydantic model instances.

Parameters
----------

**filters
   Keyword arguments mapping column names to filter values. Each filter uses equality comparison (=).

Returns
-------

List[BaseModel]
   A list of model instances that match all specified filters.

Raises
------

SQLInjectionError
   If any field name or the table name contains invalid characters (security protection).
Exception
   For any database-related errors.

Examples
--------

Single filter:

.. code-block:: python

   from pydantic import BaseModel
   from wpostgresql import WPostgreSQL

   class User(BaseModel):
       id: int
       name: str
       email: str
       is_active: bool

   db_config = {
       "dbname": "mydb",
       "user": "postgres",
       "password": "secret",
       "host": "localhost",
       "port": 5432,
   }

   db = WPostgreSQL(User, db_config)

   # Get all active users
   active_users = db.get_by_field(is_active=True)
   for user in active_users:
       print(f"{user.id}: {user.name}")

Multiple filters (AND logic):

.. code-block:: python

   # Get active users named "John"
   john_active_users = db.get_by_field(name="John", is_active=True)
   for user in john_active_users:
       print(f"{user.id}: {user.name} - Active: {user.is_active}")

See Also
--------

- :meth:`wpostgresql.WPostgreSQL.get_all` : Get all records without filters
- :meth:`wpostgresql.WPostgreSQL.get_paginated` : Get filtered records with pagination
- :meth:`wpostgresql.WPostgreSQL.get_by_field_async` : Asynchronous version