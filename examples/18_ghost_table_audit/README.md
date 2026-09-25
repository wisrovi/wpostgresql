# 18 - Enterprise Ghost Table Audit Trail (`_forensic_audit_log`)

This example demonstrates how **wpostgresql** automatically manages a central audit trail table (`_forensic_audit_log`) whenever forensic mode is active (`ForensicModel` or `forensic=True`).

---

## 🛠️ Key Technologies & Libraries

* **Python 3.10+**: Core programming language.
* **WPostgreSQL**: Enterprise-grade forensic ORM and automatic change data capture (CDC) engine.
* **Pydantic**: Schema definition and JSON serialization (`BaseModel`, `ForensicModel`).
* **Psycopg 3**: High-performance PostgreSQL database adapter for Python.
* **Psycopg Pool**: Efficient connection pooling for transactional integrity.

---

## 🚀 How it Works

When `forensic=True` (or inheriting from `ForensicModel`), `wpostgresql` automatically creates and populates a central ghost table `_forensic_audit_log`:

```sql
CREATE TABLE IF NOT EXISTS _forensic_audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    action_type TEXT NOT NULL,  -- INSERT, UPDATE, SOFT_DELETE, HARD_DELETE
    record_id TEXT,
    data_before TEXT,          -- JSON snapshot before change
    data_after TEXT,           -- JSON snapshot after change
    create_by INTEGER DEFAULT 1,
    create_in TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status INTEGER DEFAULT 1
);
```

Every operation (`insert`, `update`, `delete`) automatically records a full before/after snapshot within the same database transaction.

---

## 📋 Running the Example

```bash
python examples/18_ghost_table_audit/example.py
```

---

## 👨‍💻 Author

**William Rodríguez** - AI Leader & Solutions Architect
