.. _getting-started:

Getting Started with wpostgresql
================================

.. hero::
   :title: Get Started with wpostgresql
   :subtitle: A high-performance, type-safe PostgreSQL ORM with Pydantic integration
   :image: _static/logo.png
   :alt: wpostgresql logo
   :btn1_text: Installation Guide
   :btn1_url: #installation
   :btn2_text: View Examples
   :btn2_url: #examples
   :btn2_alt: Examples
   :btn2_class: btn-secondary
   :btn1_class: btn-primary
   :color: primary

.. tab-set::

   .. tab-item:: Installation
      :sync: true

      .. include:: installation.rst

   .. tab-item:: Quickstart
      :sync: true

      .. include:: quickstart.rst

   .. tab-item:: Configuration
      :sync: true

      .. include:: configuration.rst

   .. tab-item:: Basic Usage
      :sync: true

      .. include:: basic_usage.rst

.. section-separator::

.. _examples:

Examples Gallery
================

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

      .. button-ref:: ../tutorials/crud_operations
         :color: primary
         :expand:

         View CRUD Tutorial

   .. grid-item-card::
      :title: Transactions & Bulk Operations
      :class-card: wpostgresql-card
      :img-top: _static/transactions.png
      ^^^

      Master database transactions and efficient bulk data processing.
      Covers async transactions and performance optimization.

      +++

      .. button-ref:: ../tutorials/transactions
         :color: primary
         :expand:

         View Transactions Tutorial

   .. grid-item-card::
      :title: Relationships & Advanced Features
      :class-card: wpostgresql-card
      :img-top: _static/relationships.png
      ^^^

      Explore model relationships, soft deletes, timestamps, and more advanced ORM features.

      +++

      .. button-ref:: ../tutorials/relationships
         :color: primary
         :expand:

         View Relationships Tutorial

   .. grid-item-card::
      :title: Connection Pooling & Async
      :class-card: wpostgresql-card
      :img-top: _static/async.png
      ^^^

      Learn how to configure connection pools and leverage async operations for high-performance applications.

      +++

      .. button-ref:: ../tutorials/async_operations
         :color: primary
         :expand:

         View Async Tutorial

.. section-separator::

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   installation
   quickstart
   configuration
   basic_usage