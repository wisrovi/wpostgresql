.. wpostgresql documentation master file
..   # wpostgresql documentation master file, created by
..   sphinx-quickstart on Tue Mar 31 2026.
..   You can adapt this file completely to your liking, but it should at least
..   contain the root `toctree` directive.

.. hero::
   :title: wpostgresql
   :subtitle: A high-performance, type-safe PostgreSQL ORM with Pydantic integration
   :image: _static/logo.png
   :alt: wpostgresql logo
   :btn1_text: Get Started
   :btn1_url: getting_started/index.html
   :btn2_text: View on GitHub
   :btn2_url: https://github.com/wisrovi/wpostgresql
   :btn2_alt: GitHub
   :btn2_class: btn-secondary
   :btn1_class: btn-primary
   :color: primary

.. only:: html

   .. cards::
      :margin: 2
      :column: col-lg-4 col-md-6 d-flex align-items-stretch

      .. card::
         :title: Getting Started
         :subtitle: Begin your journey with wpostgresql
         :link: getting_started/index.html
         :link_type: ref

         +++

         Learn how to install, configure, and start using wpostgresql in your projects.
         Follow our step-by-step guide to set up your first database connection and perform basic operations.

      .. card::
         :title: Tutorials
         :subtitle: Hands-on examples and guides
         :link: tutorials/index.html
         :link_type: ref

         +++

         Dive into practical tutorials covering CRUD operations, transactions, bulk operations, and more.
         Each tutorial includes runnable code samples and expected outputs.

      .. card::
         :title: API Reference
         :subtitle: Complete documentation of all classes and methods
         :link: api_reference/index.html
         :link_type: ref

         +++

         Explore the full API reference with detailed descriptions, parameter information, and usage examples
         for every component of wpostgresql.

      .. card::
         :title: Examples
         :subtitle: Real-world code samples
         :link: examples/README.html
         :link_type: ref

         +++

         Browse through a collection of practical examples demonstrating common use cases and advanced features.
         Each example is self-contained and ready to run.

      .. card::
         :title: Best Practices
         :subtitle: Guidelines for optimal usage
         :link: tutorials/advanced_features.html#best-practices
         :link_type: ref

         +++

         Discover recommended patterns and techniques for getting the most out of wpostgresql
         in terms of performance, maintainability, and scalability.

      .. card::
         :title: Contributing
         :subtitle: Help improve wpostgresql
         :link: https://github.com/wisrovi/wpostgresql/blob/main/CONTRIBUTING.md
         :link_type: url

         +++

         Want to contribute? Learn how to report issues, submit pull requests, and help make wpostgresql better.

.. section-separator::

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card::
      :title: Why Choose wpostgresql?
      :class-card: wpostgresql-card
      :img-top: _static/why-choose.png
      ^^^

      wpostgresql combines the power of PostgreSQL with the simplicity of Pydantic models to deliver
      a developer-friendly ORM that doesn't compromise on performance or type safety.

      .. icon-links::
         :class: txt-center

         - :icon: fa-solid fa-database
           :title: PostgreSQL Powered
           :description: Built on top of psycopg 3 for optimal PostgreSQL performance

         - :icon: fa-solid fa-magnifying-glass
           :title: Type Safe
           :description: Full Pydantic integration ensures data validity at every step

         - :icon: fa-solid fa-rocket
           :title: High Performance
           :description: Connection pooling and bulk operations for maximum throughput

         - :icon: fa-solid fa-shield-halved
           :title: Secure
           :description: Built-in SQL injection prevention and security best practices

   .. grid-item-card::
      :title: Key Features at a Glance
      :class-card: wpostgresql-card
      :img-top: _static/features.png
      ^^^

      .. grid:: 1 2 2 2
         :gutter: 2

         .. grid-item-card::
            :text: 🔄 **Auto Table Synchronization**
               Tables are automatically created and updated based on your Pydantic models

         .. grid-item-card::
            :text: ⚡ **Async/Await Support**
               Complete async API for high-performance applications

         .. grid-item-card::
            :text: 📦 **Bulk Operations**
               Efficient bulk insert, update, and delete operations

         .. grid-item-card::
            :text: 🔒 **Transaction Management**
               Robust transaction support with automatic rollback on failure

         .. grid-item-card::
            :text: 🔍 **Query Builder**
               Safe SQL construction with injection prevention

         .. grid-item-card::
            :text: 💻 **CLI Tool**
               Command-line interface for database management and migrations

         .. grid-item-card::
            :text: 📊 **Pagination**
               LIMIT/OFFSET and page-number based pagination for large datasets

         .. grid-item-card::
            :text: 🛡️ **Constraint Support**
               Primary Key, UNIQUE, and NOT NULL constraints via field descriptions

.. section-separator::

.. include:: ../README.md
   :start-line: 24
   :end-line: 40

.. section-separator::

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:

   getting_started/index
   api_reference/index
   tutorials/index
   faq
   bibliography

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`