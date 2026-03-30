# Tests - wpostgresql

Tests de integración para cada funcionalidad de la librería.

## Estructura

```
test/
├── conftest.py              # Configuración共享
├── 01_crud/
│   ├── test_create.py
│   ├── test_read.py
│   ├── test_update.py
│   └── test_delete.py
├── 02_new_columns/
│   └── test_add_column.py
└── 03_restrictions/
    ├── test_primary_key.py
    ├── test_unique.py
    └── test_not_null.py
```

## Requisitos

```bash
pip install pytest
```

## Ejecutar tests

```bash
# Todos los tests
cd examples/test
pytest -v

# Un archivo específico
pytest test/01_crud/test_create.py -v

# Con coverage
pytest --cov=wpostgresql -v
```

## Base de datos

Los tests requieren una base de datos PostgreSQL. Para levantarla:

```bash
cd enviroment
docker-compose up -d
```

Configuración por defecto:
- Host: localhost:5432
- User: postgres
- Password: postgres
- DB: wpostgresql
