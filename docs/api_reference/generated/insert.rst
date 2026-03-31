.. _wpostgresql-insert:

insert method
=============

.. automethod:: wpostgresql.WPostgreSQL.insert
   :noindex:
   :noindex-entry:

.. raw:: html

   <div class="section-separator"></div>

Description
-----------

Insert a new record into the database. This method automatically validates the data using the Pydantic model before insertion.

Parameters
----------

data : BaseModel
   The Pydantic model instance containing the data to insert.

Returns
-------

None

Raises
------

ValidationError
   If the data fails Pydantic validation.
SQLInjectionError
   If the table name contains invalid characters (security protection).
Exception
   For any database-related errors.

Examples
--------

Basic usage:

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

   # Insert a new user
   user = User(id=1, name="John Doe", email="john@example.com")
   db.insert(user)

   # Insert with automatic ID generation (if your model supports it)
   # db.insert(User(name="Jane Smith", email="jane@example.com"))

See Also
--------

- :meth:`wpostgresql.WPostgreSQL.insert_many` : Insert multiple records
- :meth:`wpostgresql.WPostgreSQL.update` : Update existing records
- :meth:`wpostgresql.WPostgreSQL.insert_async` : Asynchronous version