# Tests - wpostgresql

Tests unitarios y de integración para la librería wpostgresql.

## Estructura

```
test/
├── conftest.py           # Configuración compartida
├── README.md            # Este archivo
├── unit/                # Tests unitarios
│   ├── test_sql_types.py
│   └── test_restrictions.py
└── integration/         # Tests de integración
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

### Unitarios
| Archivo | Descripción |
|---------|-------------|
| test_sql_types.py | Tests para mapeo de tipos Pydantic → SQL |
| test_restrictions.py | Tests para restricciones (PK, UNIQUE, NOT NULL) |

### Integración
| Archivo | Descripción |
|---------|-------------|
| test_crud.py | Tests para operaciones CRUD |
| test_sync.py | Tests para sincronización de columnas |

## Requisitos

```bash
pip install pytest pytest-cov
```

## Base de datos

Los tests requieren PostgreSQL. Para levantarla:

```bash
cd enviroment
docker-compose up -d
```

Configuración:
- Host: localhost:5432
- User: postgres
- Password: postgres
- DB: wpostgresql
