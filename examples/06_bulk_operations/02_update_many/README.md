# Actualizar Múltiples Registros (Bulk Update)

Este ejemplo muestra cómo actualizar múltiples registros en una sola operación.

## Uso

```bash
python example.py
```

## API propuesta

```python
# Actualizar varios registros con mismos valores
updates = [
    {"id": 1, "status": "inactive"},
    {"id": 2, "status": "inactive"},
]
db.update_many(updates)

# O con condición
db.update_many(updates, where={"status": "active"})
```

## Beneficios

- **Rendimiento**: Una sola consulta SQL
- **Conveniencia**: Actualizar muchos registros fácilmente

## Resultado esperado

```
Usuarios actualizados: [User(id=1, name='Alice', status='inactive'), User(id=2, name='Bob', status='inactive'), User(id=3, name='Charlie', status='active')]
```
