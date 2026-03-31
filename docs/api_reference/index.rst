.. _api-reference:

API Reference
=============

.. hero::
   :title: wpostgresql API Reference
   :subtitle: Complete documentation of all classes, methods, and modules
   :image: _static/api.png
   :alt: API reference illustration
   :btn1_text: WPostgreSQL Class
   :btn1_url: #wpostgresql-class
   :btn2_text: Module Index
   :btn2_url: #module-index
   :btn2_alt: Module Index
   :btn2_class: btn-secondary
   :btn1_class: btn-primary
   :color: primary

.. raw:: html

   <div class="section-separator"></div>

.. _wpostgresql-class:

WPostgreSQL Class
=================

The main interface for interacting with your PostgreSQL database using wpostgresql.

.. autoclass:: wpostgresql.WPostgreSQL
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :member-order: bysource

.. tab-set::

   .. tab-item:: Constructor
      :sync: true

      .. automethod:: wpostgresql.WPostgreSQL.__init__
         :nosignature:

   .. tab-item:: CRUD Operations
      :sync: true

      .. autosummary::
         :nosignatures:

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

         table_exists
         create_table
         drop_table
         get_table_info
         execute_query
         execute_query_raw

.. raw:: html

   <div class="section-separator"></div>

.. _connection-module:

Connection Module
=================

.. automodule:: wpostgresql.core.connection
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :member-order: bysource

.. raw:: html

   <div class="section-separator"></div>

.. _sync-module:

Sync Module
===========

.. automodule:: wpostgresql.core.sync
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :member-order: bysource

.. raw:: html

   <div class="section-separator"></div>

.. _exceptions-module:

Exceptions Module
=================

.. automodule:: wpostgresql.exceptions
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :member-order: bysource

.. raw:: html

   <div class="section-separator"></div>

.. _query-builder-module:

Query Builder Module
====================

.. automodule:: wpostgresql.builders.query_builder
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :member-order: bysource

.. raw:: html

   <div class="section-separator"></div>

.. _module-index:

Module Index
============

.. moduleindex::
   :maxdepth: 2

.. raw:: html

   <div class="section-separator"></div>

.. _code-examples:

Code Examples
=============

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card::
      :title: Basic Usage
      :link: ../getting_started/quickstart.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Learn the basics of using wpostgresql with synchronous operations.

   .. grid-item-card::
      :title: Async Usage
      :link: ../getting_started/quickstart.html#asynchronous
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      See how to use wpostgresql with async/await for high-performance applications.

   .. grid-item-card::
      :title: Configuration
      :link: ../getting_started/configuration.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Explore advanced configuration options for production use.

   .. grid-item-card::
      :title: Examples Gallery
      :link: ../examples/index.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Browse through practical examples demonstrating all features.

.. raw:: html

   <div class="section-separator"></div>

.. include:: ../examples/01_crud/README.md
   :start-line: 90
   :end-line: 114