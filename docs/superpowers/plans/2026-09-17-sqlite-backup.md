# SQLite Backup Plan for WPostgreSQL

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a backup feature in `wpostgresql` that exports table data from PostgreSQL to an SQLite database file strictly using `wsqlite` (WSQLite), create example 15_backups, add unit/integration tests, and update documentation and MCP server.

**Architecture:** Implement `backup_to_sqlite` and `backup_to_sqlite_async` methods on `WPostgreSQL` repository class, leveraging `wsqlite.WSQLite` to initialize target SQLite database schemas and perform bulk insertion. Add an example directory `examples/15_backups`, update `README.md` files (including tech stack sections), and update `wpostgresql-mcp` tools and catalog.

**Tech Stack:** Python 3.9+, PostgreSQL 13+, psycopg 3.x, Pydantic 2.x, `wsqlite` (WSQLite).

**Spec:** Goal prompt: "necesito una nueva caracteristica, que saque backups de tablas a sqlite (de wsqlite) yo entregandole el path del sqlite... siempre wsqlite nunca sqlite... en la carpeta examples, crear un 15_backups, y en el mcp y los readme, ajusta para que quede registrada la nueva funcionalidad"

## Global Constraints

- Never use standard `sqlite3` directly or SQLAlchemy/other ORMs; always use `wsqlite.WSQLite` for SQLite operations.
- Maintain Pydantic v2 model compatibility.
- Ensure all tests run with `pytest` and pass pre-commit / pylint / mypy rules.
- Update `README.md` files with relevant key technologies (including `wsqlite`).
- Git commits must follow exact rules: 1 file per commit, bracket prefix (e.g. `[FEATURE]`, `[DOCS]`, `[TEST]`).

---

### Task 1: Add `backup_to_sqlite` sync and async core methods in `wpostgresql`

**Files:**
- Create: `wpostgresql/src/wpostgresql/core/backup.py`
- Modify: `wpostgresql/src/wpostgresql/core/repository.py`
- Modify: `wpostgresql/src/wpostgresql/__init__.py`
- Test: `wpostgresql/test/unit/test_backup.py`

**Interfaces:**
- Consumes: `wsqlite.WSQLite`
- Produces: `WPostgreSQL.backup_to_sqlite(sqlite_path: str | Path, table_name: Optional[str] = None) -> int` and `WPostgreSQL.backup_to_sqlite_async(sqlite_path: str | Path, table_name: Optional[str] = None) -> int`

- [ ] **Step 1: Write the failing unit test**

Create `wpostgresql/test/unit/test_backup.py` testing sync and async backup functions using `wsqlite`.

- [ ] **Step 2: Run test to verify it fails**

Run `pytest wpostgresql/test/unit/test_backup.py`

- [ ] **Step 3: Implement `wpostgresql/src/wpostgresql/core/backup.py` and modify `repository.py`**

Implement `backup_to_sqlite` and `backup_to_sqlite_async` in `backup.py` using `WSQLite` instance to sync schema and insert records. Expose them on `WPostgreSQL` class.

- [ ] **Step 4: Run test to verify it passes**

Run `pytest wpostgresql/test/unit/test_backup.py`

- [ ] **Step 5: Commit**

Commit files one by one with bracket commit messages (`[FEATURE] Add backup_to_sqlite module`, etc.).

---

### Task 2: Create Example 15 (`examples/15_backups`)

**Files:**
- Create: `wpostgresql/examples/15_backups/01_sqlite_backup/example.py`
- Create: `wpostgresql/examples/15_backups/01_sqlite_backup/README.md`
- Create: `wpostgresql/examples/15_backups/README.md`
- Create: `wpostgresql/examples/15_backups/test_example.py`

**Interfaces:**
- Consumes: `WPostgreSQL.backup_to_sqlite`

- [ ] **Step 1: Create example code and test**
Create runnable example demonstrating backing up PostgreSQL table to SQLite file using `wsqlite`.

- [ ] **Step 2: Run example test**
Run `pytest wpostgresql/examples/15_backups/test_example.py`

- [ ] **Step 3: Commit**
Commit files one by one.

---

### Task 3: Update Documentation & MCP Server (`wpostgresql-mcp`)

**Files:**
- Modify: `wpostgresql/README.md`
- Modify: `wpostgresql/docs/API.md`
- Modify: `wpostgresql-mcp/src/wpostgresql_mcp/server.py`
- Modify: `wpostgresql-mcp/README.md`

**Interfaces:**
- Consumes: `backup_to_sqlite` documentation

- [ ] **Step 1: Update `wpostgresql/README.md` and `docs/API.md`**
Add SQLite Backup feature to features list and technical stack table (`wsqlite`).

- [ ] **Step 2: Update `wpostgresql-mcp` blueprints & catalog**
Add backup section to MCP server blueprints and README.

- [ ] **Step 3: Run full test suite & linting**
Run `pytest wpostgresql` to ensure all tests pass.

- [ ] **Step 4: Commit**
Commit modified files one by one.
