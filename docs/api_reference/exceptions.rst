=============
Exceptions
=============

.. automodule:: wpostgresql.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Exception Hierarchy
-------------------

* :exc:`wpostgresql.WPostgreSQLError`
    * :exc:`wpostgresql.ConnectionError`
    * :exc:`wpostgresql.TableSyncError`
    * :exc:`wpostgresql.ValidationError`
    * :exc:`wpostgresql.OperationError`
    * :exc:`wpostgresql.SQLInjectionError`
    * :exc:`wpostgresql.TransactionError`

Usage Example
-------------

.. code-block:: python

    from wpostgresql import WPostgreSQL, ConnectionError

    try:
        db = WPostgreSQL(User, db_config)
    except ConnectionError as e:
        print(f"Failed to connect: {e}")