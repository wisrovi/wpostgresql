# Add Column - Añadir Nuevas Columnas

Este ejemplo muestra cómo añadir nuevas columnas al modelo y sincronizar automáticamente con la base de datos.

## Uso

```bash
python example.py
```

## Explicación

1. Se crea el modelo inicial sin el campo `email`
2. Se insertan registros con ese modelo
3. Se redefine el modelo añadiendo el campo `email`
4. Al crear una nueva instancia de `WPostgreSQL`, la tabla se sincroniza automáticamente
5. Se pueden insertar registros con el nuevo campo

## Resultado esperado

```
Usuarios: [User(id=1, name='Ana López', age=25, is_active=True, email=''), User(id=2, name='Carlos Ruiz', age=30, is_active=True, email='carlos@example.com')]
```
