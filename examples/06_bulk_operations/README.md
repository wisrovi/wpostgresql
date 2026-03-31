# 06 - Bulk Operations

This folder contains examples of how to perform **bulk operations** with **wpostgresql** to efficiently insert, update, or delete multiple records.

---

## 1. 🚶 Diagram Walkthrough

```mermaid
flowchart LR
    A[List of records] --> B[Batch SQL]
    B --> C[Single query]
    C --> D[Execute once]
```

## 2. 🗺️ System Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant WP as WPostgreSQL
    participant PG as PostgreSQL

    U->>WP: insert_many([...])
    WP->>PG: INSERT VALUES (...), (...), (...)
    PG-->>WP: count
    WP-->>U: inserted count
```

## 3. 🏗️ Architecture Components

```mermaid
graph LR
    subgraph Bulk
        IM[01_insert_many]
        UM[02_update_many]
        AB[03_async_bulk]
    end
```

## 4. ⚙️ Container Lifecycle

### Build Process
- Example written

### Runtime Process
1. User provides list
2. Batch SQL constructed
3. Single query executed
4. Count returned

## 5. 📂 File-by-File Guide

| Folder | Purpose |
|--------|---------|
| `01_insert_many/` | Bulk insert |
| `02_update_many/` | Bulk update |
| `03_async_bulk/` | Async bulk |

---

## Contents

| Folder | Description |
|--------|-------------|
| [01_insert_many](01_insert_many/) | Bulk insert examples |
| [02_update_many](02_update_many/) | Bulk update examples |
| [03_async_bulk](03_async_bulk/) | Async bulk operations |

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
