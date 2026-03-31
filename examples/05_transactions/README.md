# 05 - Transactions

This folder contains examples of how to use **transactions** with **wpostgresql**, including commit and rollback handling.

---

## 1. 🚶 Diagram Walkthrough

```mermaid
flowchart LR
    A[BEGIN] --> B[Ops]
    B --> C{Success?}
    C -->|Yes| D[COMMIT]
    C -->|No| E[ROLLBACK]
```

## 2. 🗺️ System Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant WP as WPostgreSQL
    participant PG as PostgreSQL

    U->>WP: execute_transaction([...])
    WP->>PG: BEGIN
    WP->>PG: INSERT 1
    WP->>PG: INSERT 2
    PG-->>WP: OK
    WP->>PG: COMMIT
    WP-->>U: Success
```

## 3. 🏗️ Architecture Components

```mermaid
graph LR
    subgraph Transactions
        BT[01_basic_transaction]
        AT[02_async_transaction]
    end
```

## 4. ⚙️ Container Lifecycle

### Build Process
- Example code written

### Runtime Process
1. User calls transaction method
2. BEGIN executed
3. All operations run
4. On success: COMMIT
5. On error: ROLLBACK

## 5. 📂 File-by-File Guide

| Folder | Purpose |
|--------|---------|
| `01_basic_transaction/` | Sync transactions |
| `02_async_transaction/` | Async transactions |

---

## Contents

| Folder | Description |
|--------|-------------|
| [01_basic_transaction](01_basic_transaction/) | Synchronous transaction examples |
| [02_async_transaction](02_async_transaction/) | Asynchronous transaction examples |

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
