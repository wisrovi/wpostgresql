# Hoja de Ruta - Solución Stress Test y Pool Configurable

## Problema Actual

### Stress Test Results (100 usuarios × 100 requests = 10,000 ops)
- **Total Requests**: 10,000
- **Exitosas**: 6,600 (66%)
- **Fallidas**: 3,400 (34%)

### Desglose por Operación
| Operación | Total | Exitosas | Fallidas |
|-----------|-------|----------|----------|
| INSERT    | 3,400 | 0        | 3,400    |
| GET       | 3,300 | 3,300    | 0        |
| COUNT     | 3,300 | 3,300    | 0        |

**Conclusión**: 100% de inserciones fallan bajo carga concurrente.

---

## Causas Raíz

### 1. Pool Size Muy Pequeño
- Pool default: `max_size=20`
- 100 usuarios concurrentes agotan el pool inmediatamente

### 2. Operaciones de Escritura Agotan el Pool
- INSERT requiere más tiempo (execute + commit)
- GET/COUNT son más rápidos y "roban" conexiones

### 3. PostgreSQL Docker
- PostgreSQL 13.2 con 0.5 CPU y 1GB RAM
- `max_connections` por defecto: ~100

---

## Solución: Pool Configurable (Opción B)

### Objetivo
Agregar parámetro `pool_config` a `WPostgreSQL` **sin romper** el código de los 18,000 usuarios existentes.

### Backward Compatibility Garantizada
```python
# Código existente NO se rompe
db = WPostgreSQL(Model, db_config)  # Funciona igual

# Nuevo código con pool personalizado
db = WPostgreSQL(Model, db_config, {"min_size": 10, "max_size": 200})
```

---

## Plan de Implementación

### Fase 1: Código
1. **`src/wpostgresql/core/repository.py`**
   - Agregar `pool_config: Optional[dict] = None` al `__init__`
   - Pasar `pool_config` a `TableSync`

2. **`src/wpostgresql/core/connection.py`**
   - Agregar `pool_config` parameter a `_get_global_sync_pool()`
   - Agregar `pool_config` parameter a `_get_global_async_pool()`
   - Agregar `pool_config` parameter a `get_connection()`
   - Agregar `pool_config` parameter a `get_async_connection()`

3. **`src/wpostgresql/core/sync.py`**
   - Agregar `pool_config` parameter a `TableSync.__init__()`
   - Agregar `pool_config` parameter a `AsyncTableSync.__init__()`

4. **`src/wpostgresql/__init__.py`**
   - Exportar `DEFAULT_POOL_CONFIG`

### Fase 2: Tests
5. Crear test unitario para `pool_config`
6. Ejecutar todos los tests existentes (verificar backward compatibility)
7. Modificar `stress_test.py` para usar pool personalizado
8. Ejecutar stress test sync y async

### Fase 3: Documentación
9. Actualizar `README.md` con ejemplo de `pool_config`
10. Actualizar `index.html` con nuevos resultados
11. Actualizar `CHANGELOG.md` con versión 1.0.1

---

## Configuración Recomendada

### Para Producción
```python
pool_config = {
    "min_size": 10,
    "max_size": 100,
}
```

### Para Stress Test
```python
pool_config = {
    "min_size": 20,
    "max_size": 200,
}
```

---

## Resultados Esperados

### Antes
- INSERT: 0% éxito
- GET: 100% éxito
- COUNT: 100% éxito

### Después
- INSERT: 100% éxito
- GET: 100% éxito
- COUNT: 100% éxito

---

## Archivos a Modificar

1. `src/wpostgresql/core/repository.py`
2. `src/wpostgresql/core/connection.py`
3. `src/wpostgresql/core/sync.py`
4. `src/wpostgresql/__init__.py`
5. `stress_test.py`
6. `test/unit/test_connection.py`
7. `README.md`
8. `index.html`
9. `CHANGELOG.md`
