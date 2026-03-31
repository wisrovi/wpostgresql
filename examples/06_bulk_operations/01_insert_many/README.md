# Insertar Múltiples Registros (Bulk Insert)

Este ejemplo muestra cómo insertar múltiples registros en una sola operación.

## Uso

```bash
python example.py
```

## API propuesta

```python
users = [
    User(id=1, name="Alice", age=25),
    User(id=2, name="Bob", age=30),
    User(id=3, name="Charlie", age=35),
]

db.insert_many(users)
```

## Beneficios

- **Rendimiento**: Una sola consulta SQL para múltiples registros
- **Velocidad**: Mucho más rápido que llamar `insert()` múltiples veces
- **Atomicidad**: Todos se insertan o ninguno (si hay error)

## Resultado esperado

```
Usuarios insertados: [User(id=1, name='Alice', age=25), User(id=2, name='Bob', age=30), ...]
```
