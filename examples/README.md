# Ejemplos - wpostgresql

Colección de ejemplos y tests organizados por funcionalidades para aprender a usar la librería.

## Estructura General

```
examples/
├── README.md              # Este archivo
├── test/                  # Tests de integración
│   ├── conftest.py
│   ├── 01_crud/
│   ├── 02_new_columns/
│   └── 03_restrictions/
├── 01_crud/              # Ejemplos CRUD
├── 02_new_columns/      # Ejemplos columnas dinámicas
├── 03_restrictions/      # Ejemplos restricciones
├── 04_pagination/        # ⏳ Pendiente implementación
├── 05_transactions/      # ⏳ Pendiente implementación
├── 06_bulk_operations/  # ⏳ Pendiente implementación
├── 07_connection_pooling/ # ⏳ Pendiente implementación
├── 08_logging/          # ⏳ Pendiente implementación
└── 09_async/            # ⏳ Pendiente implementación
```

---

## Ejemplos (Para aprender)

### 01_crud - Operaciones Básicas
| Ejemplo | Descripción |
|---------|-------------|
| [01_create](./01_crud/01_create/) | Insertar nuevos registros |
| [02_read](./01_crud/02_read/) | Consultar registros |
| [03_update](./01_crud/03_update/) | Actualizar registros |
| [04_delete](./01_crud/04_delete/) | Eliminar registros |

### 02_new_columns - Columnas Dinámicas
| Ejemplo | Descripción |
|---------|-------------|
| [01_add_column](./02_new_columns/01_add_column/) | Añadir nuevas columnas al modelo |

### 03_restrictions - Restricciones de Datos
| Ejemplo | Descripción |
|---------|-------------|
| [01_primary_key](./03_restrictions/01_primary_key/) | Clave primaria (evitar duplicados) |
| [02_unique](./03_restrictions/02_unique/) | Valores únicos |
| [03_not_null](./03_restrictions/03_not_null/) | Campos obligatorios |

### 04_pagination - Paginación ⭐ Nuevo
| Ejemplo | Descripción |
|---------|-------------|
| [01_limit_offset](./04_pagination/01_limit_offset/) | Limitar y offset de resultados |
| [02_page_number](./04_pagination/02_page_number/) | Paginación por número de página |

### 05_transactions - Transacciones ⭐ Nuevo
| Ejemplo | Descripción |
|---------|-------------|
| [01_basic_transaction](./05_transactions/01_basic_transaction/) | Transacciones atómicas |

### 06_bulk_operations - Operaciones en Lote ⭐ Nuevo
| Ejemplo | Descripción |
|---------|-------------|
| [01_insert_many](./06_bulk_operations/01_insert_many/) | Insertar múltiples registros |
| [02_update_many](./06_bulk_operations/02_update_many/) | Actualizar múltiples registros |

### 07_connection_pooling - Pool de Conexiones ⭐ Nuevo
| Ejemplo | Descripción |
|---------|-------------|
| [01_simple_pool](./07_connection_pooling/01_simple_pool/) | Configurar connection pooling |

### 08_logging - Logging ⭐ Nuevo
| Ejemplo | Descripción |
|---------|-------------|
| [01_basic_logging](./08_logging/01_basic_logging/) | Configurar logging |

### 09_async - Async / Await ⭐ Nuevo
| Ejemplo | Descripción |
|---------|-------------|
| [01_basic_async](./09_async/01_basic_async/) | Versión asíncrona de la librería |

---

## Tests (Para verificar)

### Ejecutar tests

```bash
# Todos los tests
python -m pytest examples/test/ -v

# Un archivo específico
python -m pytest examples/test/01_crud/test_create.py -v
```

### Tests disponibles

| Carpeta | Tests | Estado |
|---------|-------|--------|
| 01_crud | 7 tests | ✅ Pass |
| 02_new_columns | 1 test | ✅ Pass |
| 03_restrictions | 3 tests | ✅ Pass |

**Total: 11 tests**

---

## Requisitos

- Python 3.6+
- PostgreSQL
- Librerías: `wpostgresql`, `pydantic`, `psycopg2`, `pytest`

### Levantar base de datos

```bash
cd enviroment
docker-compose up -d
```

### Instalar dependencias

```bash
pip install -e .
pip install pytest
```
