# Create - Insertar Registros

Este ejemplo muestra cómo insertar nuevos registros en la base de datos.

## Uso

```bash
python example.py
```

## Explicación

1. Se define un modelo Pydantic `User` con los campos: `id`, `name`, `age`, `is_active`
2. Se crea la instancia `WPostgreSQL` que automáticamente crea la tabla si no existe
3. Se usa el método `insert()` para agregar registros
4. Los registros se validan automáticamente con Pydantic

## Resultado esperado

```
Usuarios creados: [User(id=1, name='Juan Pérez', age=30, is_active=True), User(id=2, name='Ana López', age=25, is_active=True)]
```
