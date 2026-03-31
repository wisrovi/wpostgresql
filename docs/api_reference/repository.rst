.. _wpostgresql-class:

WPostgreSQL Class
=================

The main interface for interacting with your PostgreSQL database using wpostgresql.
This class provides both synchronous and asynchronous methods for all database operations,
automatic table creation and synchronization, and built-in transaction management.

.. autoclass:: wpostgresql.WPostgreSQL
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :member-order: bysource
   :noindex:

.. tab-set::

   .. tab-item:: Constructor
      :sync: true

      .. autoclass:: wpostgresql.WPostgreSQL
         :members: __init__
         :noindex:

   .. tab-item:: CRUD Operations
      :sync: true

      .. autosummary::
         :nosignatures:
         :toctree: generated/

         insert
         insert_many
         get_all
         get_by_field
         get_by_id
         update
         update_many
         delete
         delete_many
         count

   .. tab-item:: Async Operations
      :sync: true

      .. autosummary::
         :nosignatures:
         :toctree: generated/

         insert_async
         insert_many_async
         get_all_async
         get_by_field_async
         get_by_id_async
         update_async
         update_many_async
         delete_async
         delete_many_async
         count_async

   .. tab-item:: Utility Methods
      :sync: true

      .. autosummary::
         :nosignatures:
         :toctree: generated/

         table_exists
         create_table
         drop_table
         get_table_info
         execute_query
         execute_query_raw
         with_transaction
         with_transaction_async

.. raw:: html

   <div class="section-separator"></div>

.. _constructor:

Constructor
-----------

.. automethod:: wpostgresql.WPostgreSQL.__init__
   :nosignature:
   :noindex:

.. raw:: html

   <div class="section-separator"></div>

.. _crud-operations:

CRUD Operations
===============

Create Operations
-----------------

.. automethod:: wpostgresql.WPostgreSQL.insert
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.insert_many
   :noindex:

Read Operations
---------------

.. automethod:: wpostgresql.WPostgreSQL.get_all
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.get_by_field
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.get_by_id
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.get_paginated
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.get_page
   :noindex:

Update Operations
-----------------

.. automethod:: wpostgresql.WPostgreSQL.update
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.update_many
   :noindex:

Delete Operations
-----------------

.. automethod:: wpostgresql.WPostgreSQL.delete
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.delete_many
   :noindex:

Count Operations
----------------

.. automethod:: wpostgresql.WPostgreSQL.count
   :noindex:

.. raw:: html

   <div class="section-separator"></div>

.. _async-operations:

Asynchronous Operations
=======================

All synchronous methods have asynchronous counterparts prefixed with ``_async``.
These methods provide the same functionality but return awaitable objects for use
with Python's async/await syntax.

Create Operations
-----------------

.. automethod:: wpostgresql.WPostgreSQL.insert_async
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.insert_many_async
   :noindex:

Read Operations
---------------

.. automethod:: wpostgresql.WPostgreSQL.get_all_async
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.get_by_field_async
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.get_by_id_async
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.get_paginated_async
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.get_page_async
   :noindex:

Update Operations
-----------------

.. automethod:: wpostgresql.WPostgreSQL.update_async
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.update_many_async
   :noindex:

Delete Operations
-----------------

.. automethod:: wpostgresql.WPostgreSQL.delete_async
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.delete_many_async
   :noindex:

Count Operations
----------------

.. automethod:: wpostgresql.WPostgreSQL.count_async
   :noindex:

.. raw:: html

   <div class="section-separator"></div>

.. _utility-methods:

Utility Methods
===============

Transaction Management
----------------------

.. automethod:: wpostgresql.WPostgreSQL.execute_transaction
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.with_transaction
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.execute_transaction_async
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.with_transaction_async
   :noindex:

Table Management
----------------

.. automethod:: wpostgresql.WPostgreSQL.table_exists
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.create_table
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.drop_table
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.get_table_info
   :noindex:

Query Execution
---------------

.. automethod:: wpostgresql.WPostgreSQL.execute_query
   :noindex:

.. automethod:: wpostgresql.WPostgreSQL.execute_query_raw
   :noindex:

.. raw:: html

   <div class="section-separator"></div>

.. _method-details:

Detailed Method Documentation
=============================

.. toctree::
   :maxdepth: 2
   :caption: Method Documentation
   :hidden:

   insert
   insert_many
   get_all
   get_by_field
   update
   delete
   count
   insert_async
   insert_many_async
   get_all_async
   get_by_field_async
   update_async
   delete_async
   count_async
   execute_transaction
   with_transaction
   execute_transaction_async
   with_transaction_async