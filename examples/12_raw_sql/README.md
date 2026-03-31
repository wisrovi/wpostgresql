# 12 - Raw SQL

This folder contains examples of how to execute **raw SQL** with **wpostgresql** when more control or complex queries are needed.

---

## 1. 🚶 Diagram Walkthrough

```mermaid
flowchart LR
    A[Raw SQL] --> B[Execute]
    B --> C[Results]
```

## 2. 🗺️ System Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant WP as WPostgreSQL
    participant PG as PostgreSQL

    U->>WP: execute_raw(sql, params)
    WP->>PG: Execute SQL
    PG-->>WP: Results
    WP-->>U: Results
```

## 3. 🏗️ Architecture Components

```mermaid
graph LR
    subgraph RawSQL
        ER[01_execute_raw]
    end
    
    ER --> PG[PostgreSQL]
```

## 4. ⚙️ Container Lifecycle

### Build Process
- Example written

### Runtime Process
1. User writes SQL
2. Parameters validated
3. Query executed
4. Results returned

## 5. 📂 File-by-File Guide

| Folder | Purpose |
|--------|---------|
| `01_execute_raw/` | Direct SQL execution |

---

## Contents

| Folder | Description |
|--------|-------------|
| [01_execute_raw](01_execute_raw/) | Direct SQL execution examples |

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
