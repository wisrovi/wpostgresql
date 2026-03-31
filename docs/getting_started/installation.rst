.. _installation:

Installation Guide
==================

.. hero::
   :title: Install wpostgresql
   :subtitle: Get up and running with wpostgresql in just a few steps
   :image: _static/installation.png
   :alt: Installation illustration
   :btn1_text: Quick Install
   :btn1_url: #quick-install
   :btn2_text: Advanced Options
   :btn2_url: #advanced-options
   :btn2_alt: Advanced Options
   :btn2_class: btn-secondary
   :btn1_class: btn-primary
   :color: primary

.. tab-set::

   .. tab-item:: Quick Install
      :sync: true

      The fastest way to get started with wpostgresql:

      .. code-block:: bash

         pip install wpostgresql

      Verify your installation:

      .. code-block:: python

         >>> import wpostgresql
         >>> print(wpostgresql.__version__)
         0.3.0

   .. tab-item:: From Source
      :sync: true

      Install the latest development version from GitHub:

      .. code-block:: bash

         # Clone the repository
         git clone https://github.com/wisrovi/wpostgresql.git
         cd wpostgresql

         # Create and activate virtual environment
         python -m venv venv
         source venv/bin/activate  # On Windows: venv\Scripts\activate

         # Install with development dependencies
         pip install -e ".[dev]"

   .. tab-item:: Docker
      :sync: true

      Run wpostgresql with Docker for isolated development:

      .. code-block:: bash

         cd docker
         docker-compose up -d

      This starts:
      
      - PostgreSQL 13.2 on port 5432
      - pgAdmin4 on port 1717

.. section-separator::

.. _requirements:

Requirements
------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card::
      :title: Python
      :text: Python 3.9 or higher
      :class-card: wpostgresql-card
      :img-top: _static/python.png
      ^^^

   .. grid-item-card::
      :title: PostgreSQL
      :text: PostgreSQL 12 or higher
      :class-card: wpostgresql-card
      :img-top: _static/postgresql.png
      ^^^

   .. grid-item-card::
      :title: Dependencies
      :text: psycopg 3.1+, pydantic 2.0+
      :class-card: wpostgresql-card
      :img-top: _static/dependencies.png
      ^^^

   .. grid-item-card::
      :title: Optional
      :text: Docker (for containerized setup)
      :class-card: wpostgresql-card
      :img-top: _static/docker.png
      ^^^

.. section-separator::

.. _advanced-options:

Advanced Installation Options
-----------------------------

.. tab-set::

   .. tab-item:: Poetry
      :sync: true

      If you use Poetry for dependency management:

      .. code-block:: bash

         poetry add wpostgresql

   .. tab-item:: Development Extras
      :sync: true

      Install additional development dependencies:

      .. code-block:: bash

         pip install wpostgresql[dev]

      Includes: pytest, pytest-cov, pylint, mypy, bandit, ruff

   .. tab-item:: Async Extras
      :sync: true

      Install async-specific dependencies:

      .. code-block:: bash

         pip install wpostgresql[async]

      Includes: asyncio, asyncpg (if needed for specific async features)

   .. tab-item:: All Extras
      :sync: true

      Install everything including development and async dependencies:

      .. code-block:: bash

         pip install wpostgresql[dev,async]

.. section-separator::

.. _verification:

Verification
------------

After installation, verify that wpostgresql is working correctly:

.. code-block:: python

   >>> import wpostgresql
   >>> from pydantic import BaseModel
   >>>
   >>> # Define a simple model
   >>> class User(BaseModel):
   ...     id: int
   ...     name: str
   ...     email: str
   >>>
   >>> # Create a configuration (adjust for your setup)
   >>> db_config = {
   ...     "dbname": "test_db",
   ...     "user": "postgres",
   ...     "password": "postgres",
   ...     "host": "localhost",
   ...     "port": 5432,
   ... }
   >>>
   >>> # Initialize wpostgresql
   >>> db = WPostgreSQL(User, db_config)
   >>>
   >>> print("wpostgresql initialized successfully!")
   >>> print(f"Version: {wpostgresql.__version__}")

Expected output:

.. code-block:: none

   wpostgresql initialized successfully!
   Version: 0.3.0

.. section-separator::

.. _troubleshooting:

Troubleshooting
---------------

Common installation issues and their solutions:

.. tab-set::

   .. tab-item:: Connection Errors
      :sync: true

      If you encounter connection errors:

      1. Ensure PostgreSQL is running: `sudo systemctl start postgresql`
      2. Check that the database exists: `createdb test_db`
      3. Verify credentials in your connection config
      4. Check firewall settings if connecting remotely

   .. tab-item:: Permission Denied
      :sync: true

      If you get permission denied errors:

      1. Check that your user has privileges on the database
      2. For new databases, ensure you're connecting as a user with CREATEDB privileges
      3. Consider using the postgres superuser for initial setup

   .. tab-item:: Version Conflicts
      :sync: true

      If you encounter version conflicts:

      1. Ensure you're using Python 3.9+: `python --version`
      2. Check for conflicting packages: `pip list | grep -E "(psycopg|pydantic)"`
      3. Consider creating a fresh virtual environment

.. section-separator::

.. _next-steps:

Next Steps
----------

Now that you have wpostgresql installed, you can:

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
      :title: Configuration
      :link: configuration.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Explore advanced configuration options for production use.

   .. grid-item-card::
      :title: Tutorials
      :link: ../tutorials/index.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Dive into comprehensive tutorials covering all features.

   .. grid-item-card::
      :title: Examples
      :link: ../examples/index.html
      :link-type: ref
      :class-card: wpostgresql-card

      +++

      Browse through practical examples demonstrating real-world usage.