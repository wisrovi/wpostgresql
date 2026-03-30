# Connection Pooling

Este ejemplo muestra cómo usar connection pooling para mejor rendimiento.

## Uso

```bash
python example.py
```

## API propuesta

```python
db_config = {
    'dbname': 'wpostgresql',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432,
    'minconn': 1,    # Conexiones mínimas en pool
    'maxconn': 10,   # Conexiones máximas en pool
}

db = WPostgreSQL(User, db_config, pool_enabled=True)

# Obtener estado del pool
print(db.get_pool_status())
```

## Beneficios

- **Rendimiento**: Evita abrir/cerrar conexiones en cada operación
- **Recursos**: Comparte conexiones entre múltiples requests
- **Escalabilidad**: Maneja más usuarios simultáneos

## Parámetros

| Parámetro | Descripción |
|-----------|-------------|
| `minconn` | Mínimo de conexiones persistentes |
| `maxconn` | Máximo de conexiones en el pool |
| `pool_enabled` | Habilitar/deshabilitar pooling |

## Resultado esperado

```
Conexiones activas: {'min': 1, 'max': 10, 'used': 1}
Registros: 20
```
