# 07 - Connection Pooling

This folder contains examples of how to use **connection pooling** with **wpostgresql** to manage database connections efficiently.

---

## 1. 🚶 Diagram Walkthrough

```mermaid
flowchart LR
    A[Request] --> B{Pool has free?}
    B -->|Yes| C[Use connection]
    B -->|No| D[Create/Wait]
    C --> E[Execute query]
    E --> F[Return to pool]
```

## 2. 🗺️ System Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant CP as ConnectionPool
    participant PG as PostgreSQL

    U->>CP: Request connection
    CP->>CP: Get free connection
    CP->>PG: Execute query
    PG-->>CP: Results
    CP-->>U: Results
    CP->>CP: Return to pool
```

## 3. 🏗️ Architecture Components

```mermaid
graph TD
    subgraph Pool
        CM[ConnectionManager]
        CP[ConnectionPool]
    end
    
    CM --> CP
    CP --> PG[PostgreSQL]
```

## 4. ⚙️ Container Lifecycle

### Build Process
- Example written

### Runtime Process
1. Pool initialized with config
2. Requests managed automatically
3. Connections reused
4. Pool cleaned up on exit

## 5. 📂 File-by-File Guide

| Folder | Purpose |
|--------|---------|
| `01_simple_pool/` | Basic pool usage |

---

## Contents

| Folder | Description |
|--------|-------------|
| [01_simple_pool](01_simple_pool/) | Basic connection pool usage |

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
