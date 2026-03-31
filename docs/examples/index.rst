.. _examples:

Examples
========

.. hero::
   :title: wpostgresql Examples
   :subtitle: Practical examples demonstrating all features of wpostgresql
   :image: _static/examples.png
   :alt: wpostgresql examples
   :btn1_text: Browse Examples
   :btn1_url: #example-categories
   :btn2_text: View on GitHub
   :btn2_url: https://github.com/wisrovi/wpostgresql/tree/main/examples
   :btn2_alt: GitHub
   :btn2_class: btn-secondary
   :btn1_class: btn-primary
   :color: primary

.. raw:: html

   <div class="section-separator"></div>

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card::
      :title: CRUD Operations
      :class-card: wpostgresql-card
      :img-top: _static/crud.png
      ^^^

      Learn how to perform Create, Read, Update, and Delete operations with wpostgresql.
      Includes examples of bulk operations and advanced filtering.

      +++

      .. button-ref:: examples/01_crud
         :color: primary
         :expand:

         View CRUD Examples

   .. grid-item-card::
      :title: Bulk Operations
      :class-card: wpostgresql-card
      :img-top: _static/bulk.png
      ^^^

      Master efficient bulk insert, update, and delete operations for high-performance data processing.

      +++

      .. button-ref:: examples/06_bulk_operations
         :color: primary
         :expand:

         View Bulk Operations Examples

   .. grid-item-card::
      :title: Relationships & Advanced Features
      :class-card: wpostgresql-card
      :img-top: _static/relationships.png
      ^^^

      Explore model relationships, soft deletes, timestamps, and more advanced ORM features.

      +++

      .. button-ref:: examples/14_relationships
         :color: primary
         :expand:

         View Relationships Examples

   .. grid-item-card::
      :title: Connection Pooling & Async
      :class-card: wpostgresql-card
      :img-top: _static/async.png
      ^^^

      Learn how to configure connection pools and leverage async operations for high-performance applications.

      +++

      .. button-ref:: examples/09_async
         :color: primary
         :expand:

         View Async Examples

.. raw:: html

   <div class="section-separator"></div>

.. _example-categories:

Example Categories
------------------

.. toctree::
   :maxdepth: 2
   :caption: Example Categories
   :hidden:

   01_crud
   02_new_columns
   03_restrictions
   04_pagination
   05_transactions
   06_bulk_operations
   07_connection_pooling
   08_logging
   09_async
   10_aggregations
   11_timestamps
   12_raw_sql
   13_soft_delete
   14_relationships