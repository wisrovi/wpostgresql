# Async / Await

Este ejemplo muestra cómo usar la versión asíncrona de la librería.

## Uso

```bash
python example.py
```

## API propuesta

```python
import asyncio
from wpostgresql import WPostgreSQLAsync

db = WPostgreSQLAsync(User, db_config)

# Todas las operaciones usan await
await db.insert(user)
await db.get_all()
await db.get_by_field(name="Alice")
await db.update(id, user)
await db.delete(id)
```

## Beneficios

- **No bloqueante**: Otras tareas pueden ejecutarse mientras espera la BD
- **Alto rendimiento**: Ideal para APIs con muchas solicitudes simultáneas
- **Concurrent**: Ejecuta múltiples consultas en paralelo

## Diferencias entre sync y async

| Sync | Async |
|------|-------|
| `db.insert(user)` | `await db.insert(user)` |
| `db.get_all()` | `await db.get_all()` |
| Bloquea el hilo | No bloquea el hilo |

## Cuándo usar Async

- APIs web con FastAPI/Flask
- Aplicaciones con muchas conexiones simultáneas
- Microservicios
- Scripts de procesamiento en paralelo

## Requisitos

```bash
pip install psycopg2[binary]  # o psycopg3
```
