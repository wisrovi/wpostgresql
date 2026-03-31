# Tests - wpostgresql

Tests unitarios y de integración para la librería wpostgresql.

## Estructura

```
test/
├── conftest.py              # Configuración compartida
├── README.md                # Este archivo
├── unit/                    # Tests unitarios
│   ├── test_cli.py
│   ├── test_connection.py
│   ├── test_query_builder.py
│   ├── test_repository_new_features.py
│   ├── test_restrictions.py
│   ├── test_sql_types.py
│   └── test_sync_indexes.py
└── integration/             # Tests de integración
    ├── test_crud.py
    └── test_sync.py
```

## Ejecutar tests

```bash
# Todos los tests
python -m pytest test/ -v

# Solo unitarios
python -m pytest test/unit/ -v

# Solo integración
python -m pytest test/integration/ -v

# Coverage
python -m pytest test/ --cov=wpostgresql --cov-report=html
```

## Tests disponibles

### Unitarios (89 tests)
| Archivo | Tests | Descripción |
|---------|-------|-------------|
| test_cli.py | 14 | CLI tool tests |
| test_connection.py | 15 | Connection and Transaction tests |
| test_query_builder.py | 22 | QueryBuilder tests |
| test_repository_new_features.py | 21 | CRUD, pagination, bulk, transactions |
| test_restrictions.py | 3 | PK, UNIQUE, NOT NULL |
| test_sql_types.py | 5 | SQL type mapping |
| test_sync_indexes.py | 9 | Table sync and indexes |

### Integración
| Archivo | Descripción |
|---------|-------------|
| test_crud.py | Tests para operaciones CRUD |
| test_sync.py | Tests para sincronización de columnas |

## Requisitos

```bash
pip install -e ".[dev]"
```

## Dependencias Actualizadas (v0.3.0)

```toml
psycopg[binary]>=3.1.0
psycopg_pool>=3.1.0
pydantic>=2.0.0
loguru>=0.7.0
click>=8.0.0
```

## Base de datos

Los tests requieren PostgreSQL. Para levantarla:

```bash
cd docker
docker-compose up -d
```

Configuración:
- Host: localhost:5432
- User: postgres
- Password: postgres
- DB: wpostgresql
