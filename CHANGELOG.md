# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0 (LTS)] - 2026-03-31

### Added
- **Full Type Hinting**: Comprehensive static typing for both core and test modules.
- **Loguru Integration**: Structured and readable logging for the test suite.
- **Enhanced Documentation**: Google Style Docstrings applied project-wide for better IDE support.
- **Security Hardening**: Bandit audit passed with 0 high-severity findings; enforced SQL identifier validation.

### Changed
- **Code Quality Refactor**: Deep cleanup reaching a **Pylint score of 9.67/10** on core and **9.92/10** on tests.
- **Improved Test Suite**: Modularized `QueryBuilder` tests and resolved class redefinition conflicts.
- **Refined Repository logic**: Optimization of pagination and null-handling logic.
- **Badge metrics**: Added PyPI downloads and versioning badges to README and index.html.

### Fixed
- Unspecified encoding in file operations (enforced UTF-8).
- Unused imports, variables, and arguments across the repository.
- Non-lazy logging formatting for better performance.

---

## [0.3.0] - 2026-03-25

### Added
- **Asynchronous API**: Support for `async/await` in all repository operations.
- **Connection Pooling**: Built-in pooling for both synchronous and asynchronous connections.
- **Advanced Pagination**: Support for `LIMIT/OFFSET` and page-number based data retrieval.
- **Bulk Operations**: Efficient `insert_many`, `update_many`, and `delete_many` methods.
- **CLI Interface**: New command-line tool for basic database operations (init, count, list).

### Changed
- Migrated core ORM logic to `psycopg 3.x`.
- Improved table synchronization engine for dynamic Pydantic models.

### Fixed
- Handling of primary keys and unique constraints in table creation.
- Connection leak in transaction context managers.

---

## [0.2.0] - 2026-03-10

### Added
- **Table Synchronization**: Basic auto-creation of tables from Pydantic models.
- **Transaction Support**: Synchronous transaction context managers.
- **Basic CRUD**: Implementation of `insert`, `get_all`, `update`, and `delete`.

---

## [0.1.0] - 2026-02-28

### Added
- **Core Library**: Initial release with Pydantic-to-SQL mapping.
- **Connection Manager**: Basic PostgreSQL connection handling.
