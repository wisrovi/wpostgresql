# Paginación con LIMIT y OFFSET

Este ejemplo muestra cómo paginar resultados usando limit y offset.

## Uso

```bash
python example.py
```

## API propuesta

```python
# Obtener solo los primeros 5 registros
db.get_all(limit=5)

# Saltar los primeros 5 y obtener 3
db.get_all(offset=5, limit=3)

# Offset sin limit (saltar primeros N)
db.get_all(offset=10)
```

## Resultado esperado

```
Primeros 5 usuarios: [User(id=1, ...), User(id=2, ...), User(id=3, ...), User(id=4, ...), User(id=5, ...)]
Saltar primeros 5, mostrar 3: [User(id=6, ...), User(id=7, ...), User(id=8, ...)]
```
