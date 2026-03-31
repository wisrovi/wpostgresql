.. _configuration:

Configuration Guide
===================

.. hero::
   :title: Configure wpostgresql
   :subtitle: Learn how to properly configure wpostgresql for your environment
   :image: _static/configuration.png
   :alt: Configuration illustration
   :btn1_text: Basic Setup
   :btn1_url: #basic-database-configuration
   :btn2_text: Advanced Options
   :btn2_url: #advanced-configuration
   :btn2_alt: Advanced Options
   :btn2_class: btn-secondary
   :btn1_class: btn-primary
   :color: primary

.. tab-set::

   .. tab-item:: Database Configuration
      :sync: true

      wpostgresql uses a simple dictionary-based configuration system for database connections:

      .. code-block:: python
         :linenos:

         db_config = {
             "dbname": "your_database",
             "user": "your_user",
             "password": "your_password",
             "host": "localhost",
             "port": 5432,
         }

      Each parameter is explained below:

      .. glossary::

         dbname
            The name of the PostgreSQL database to connect to

         user
            The username to use when connecting to the database

         password
            The password to use when connecting to the database

         host
            The hostname or IP address of the PostgreSQL server

         port
            The port number on which PostgreSQL is listening (default: 5432)

   .. tab-item:: Environment Variables
      :sync: true

      For production deployments, it's recommended to use environment variables to avoid exposing credentials:

      .. code-block:: python
         :linenos:

         import os
         import wpostgresql

         db_config = {
             "dbname": os.getenv("POSTGRES_DB", "mydb"),
             "user": os.getenv("POSTGRES_USER", "postgres"),
             "password": os.getenv("POSTGRES_PASSWORD"),
             "host": os.getenv("POSTGRES_HOST", "localhost"),
             "port": int(os.getenv("POSTGRES_PORT", 5432)),
         }

      With this approach, you can set environment variables in your deployment environment:

      .. code-block:: bash

         export POSTGRES_DB="production_db"
         export POSTGRES_USER="app_user"
         export POSTGRES_PASSWORD="secure_password"
         export POSTGRES_HOST="db.example.com"
         export POSTGRES_PORT="5432"

   .. tab-item:: Connection Pool Configuration
      :sync: true

      wpostgresql automatically manages connection pooling for optimal performance:

      .. code-block:: python
         :linenos:

         from wpostgresql.core.connection import ConnectionPool

         # Default connection pool (used if not specified)
         default_pool = ConnectionPool(
             "dbname=test user=admin password=secret",
             min_size=1,
             max_size=10,
         )

         # Custom connection pool for high-concurrency applications
         high_performance_pool = ConnectionPool(
             "dbname=test user=admin password=secret",
             min_size=5,
             max_size=50,
             timeout=60,
         )

      Pool parameters:

      .. glossary::

         conninfo
            PostgreSQL connection string (format: "dbname=... user=... password=... host=... port=...")

         min_size
            Minimum number of connections to keep open in the pool

         max_size
            Maximum number of connections allowed in the pool

         timeout
            Timeout in seconds for getting a connection from the pool

   .. tab-item:: SSL Configuration
      :sync: true

      For secure connections to your PostgreSQL database, you can enable SSL:

      .. code-block:: python
         :linenos:

         db_config = {
             "dbname": "mydb",
             "user": "user",
             "password": "pass",
             "host": "localhost",
             "sslmode": "require",  # Options: disable, allow, prefer, require, verify-ca, verify-full
         }

      SSL modes:

      .. glossary::

         disable
            Only connect without SSL

         allow
            Try non-SSL first, then SSL

         prefer
            Try SSL first, then non-SSL

         require
            Only connect with SSL

         verify-ca
            Like require, but also verify the server certificate

         verify-full
            Like verify-ca, but also verify the server host name matches the certificate

   .. tab-item:: Testing Configuration
      :sync: true

      For testing purposes, it's recommended to use a separate test database:

      .. code-block:: python
         :linenos:

         import os

         test_config = {
             "dbname": "test_" + os.getenv("POSTGRES_DB", "mydb"),
             "user": os.getenv("POSTGRES_USER"),
             "password": os.getenv("POSTGRES_PASSWORD"),
             "host": os.getenv("POSTGRES_HOST", "localhost"),
             "port": int(os.getenv("POSTGRES_PORT", 5432)),
         }

      This ensures that your tests don't interfere with development or production data.

.. section-separator::

.. _advanced-configuration:

Advanced Configuration Options
------------------------------

.. tab-set::

   .. tab-item:: Logging Configuration
      :sync: true

      wpostgresql uses Loguru for logging. You can configure logging levels:

      .. code-block:: python
         :linenos:

         from loguru import logger
         import sys

         # Configure logger to output to stdout with custom format
         logger.remove()  # Remove default handler
         logger.add(
             sys.stdout,
             format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
             level="INFO"
         )

         # Or to file with rotation
         logger.add(
             "logs/wpostgresql_{time}.log",
             rotation="500 MB",
             retention="10 days",
             level="DEBUG"
         )

   .. tab-item:: Retry Configuration
      :sync: true

      Configure automatic retry behavior for transient failures:

      .. code-block:: python
         :linenos:

         from wpostgresql import WPostgreSQL
         from wpostgresql.core.connection import RetryPolicy

         # Custom retry policy
         retry_policy = RetryPolicy(
             max_attempts=3,
             base_delay=1.0,      # Base delay in seconds
             max_delay=10.0,      # Maximum delay in seconds
             jitter=0.1,          # Random jitter factor
         )

         db = WPostgreSQL(User, db_config, retry_policy=retry_policy)

   .. tab-item:: Type Configuration
      :sync: true

      Customize how wpostgresql handles specific Python types:

      .. code-block:: python
         :linenos:

         from wpostgresql import WPostgreSQL
         from wpostgresql.types.sql_types import SQLTypeMapper
         from datetime import datetime
         import uuid

         # Custom type mapper
         class CustomTypeMapper(SQLTypeMapper):
             def python_to_sql(self, python_type):
                 if python_type == uuid.UUID:
                     return "UUID"
                 return super().python_to_sql(python_type)

         db = WPostgreSQL(User, db_config, type_mapper=CustomTypeMapper())

.. section-separator::

.. _best-practices:

Best Practices for Configuration
--------------------------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card::
      :title: Use Environment Variables
      :text: Never hardcode credentials in your source code. Always use environment variables or secret management systems.
      :class-card: wpostgresql-card
      :img-top: _static/security.png
      ^^^

   .. grid-item-card::
      :title: Connection Pool Sizing
      :text: Size your connection pool based on your application's concurrent workload. Monitor pool usage and adjust as needed.
      :class-card: wpostgresql-card
      :img-top: _static/performance.png
      ^^^

   .. grid-item-card::
      :title: SSL in Production
      :text: Always use SSL when connecting to production databases, especially over public networks.
      :class-card: wpostgresql-card
      :img-top: _static/ssl.png
      ^^^

   .. grid-item-card::
      :title: Separate Test Databases
      :text: Use separate databases for development, testing, and production to prevent data contamination.
      :class-card: wpostgresql-card
      :img-top: _static/testing.png
      ^^^

.. section-separator::

.. _verification:

Verifying Your Configuration
----------------------------

After configuring wpostgresql, verify that your configuration is correct:

.. code-block:: python

   from wpostgresql import WPostgreSQL
   from pydantic import BaseModel

   class User(BaseModel):
       id: int
       name: str
       email: str

   # Your configuration here
   db_config = {
       "dbname": "test_db",
       "user": "postgres",
       "password": "postgres",
       "host": "localhost",
       "port": 5432,
   }

   try:
       db = WPostgreSQL(User, db_config)
       print("✅ Configuration successful!")
       print(f"Connected to: {db_config['host']}:{db_config['port']}/{db_config['dbname']}")
       
       # Test a simple operation
       user = User(id=1, name="Test User", email="test@example.com")
       db.insert(user)
       print("✅ Database operations working!")
       
       # Clean up
       db.delete(1)
   except Exception as e:
       print(f"❌ Configuration failed: {e}")
       print("\nTroubleshooting tips:")
       print("1. Verify PostgreSQL is running")
       print("2. Check your connection parameters")
       print("3. Ensure the database exists")
       print("4. Verify username/password are correct")

Expected output:

.. code-block:: none

   ✅ Configuration successful!
   Connected to: localhost:5432/test_db
   ✅ Database operations working!

.. section-separator::

.. _next-steps:

Next Steps
----------

Now that you have configured wpostgresql, you can:

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card::
      :title: Quickstart Guide
      :link: quickstart.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Learn the basics of wpostgresql with our hands-on quickstart guide.

   .. grid-item-card::
      :title: CRUD Operations
      :link: ../tutorials/crud_operations.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Dive into comprehensive examples of Create, Read, Update, and Delete operations.

   .. grid-item-card::
      :title: Advanced Features
      :link: ../tutorials/advanced_features.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Explore advanced features like relationships, transactions, and bulk operations.

   .. grid-item-card::
      :title: API Reference
      :link: ../api_reference/index.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Refer to the complete API documentation for detailed information on all classes and methods.