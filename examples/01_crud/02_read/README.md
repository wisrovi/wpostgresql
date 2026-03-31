# Read - Consultar Registros

Este ejemplo muestra cómo consultar registros de la base de datos.

## Métodos disponibles

### get_all()
Retorna todos los registros de la tabla.

### get_by_field(**filters)
Retorna registros que coinciden con los filtros especificados.

## Uso

```bash
python example.py
```

## Ejemplos de filtros

```python
# Un solo filtro
db.get_by_field(name="Juan Pérez")

# Múltiples filtros
db.get_by_field(age=25, is_active=True)

# Sin filtros (equivalente a get_all)
db.get_by_field()
```

## Resultado esperado

```
Todos los usuarios: [User(id=1, name='Juan Pérez', ...), ...]
Usuario por nombre: [User(id=1, name='Juan Pérez', ...)]
Usuarios activos con 25 años: [User(id=2, name='Ana López', ...)]
```
