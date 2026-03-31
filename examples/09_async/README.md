# 09 - Async Operations

This folder contains examples of how to use the **async API** of **wpostgresql** for non-blocking database operations.

---

## 1. 🚶 Diagram Walkthrough

```mermaid
flowchart LR
    A[async def] --> B[await operation]
    B --> C[Non-blocking]
    C --> D[Concurrent execution]
```

## 2. 🗺️ System Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant WP as WPostgreSQL
    participant PG as PostgreSQL

    U->>WP: await insert_async()
    WP->>PG: Execute query
    PG-->>WP: Result
    WP-->>U: await returns
```

## 3. 🏗️ Architecture Components

```mermaid
graph LR
    subgraph Async
        WP[WPostgreSQL]
        CM[AsyncConnectionManager]
    end
    
    WP --> CM
    CM --> PG[PostgreSQL]
```

## 4. ⚙️ Container Lifecycle

### Build Process
- Async methods available

### Runtime Process
1. User calls async method
2. Event loop continues
3. Query executes
4. Results await returned

## 5. 📂 File-by-File Guide

| Folder | Purpose |
|--------|---------|
| `01_basic_async/` | Basic async usage |

---

## Contents

| Folder | Description |
|--------|-------------|
| [01_basic_async](01_basic_async/) | Basic async operations |

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
