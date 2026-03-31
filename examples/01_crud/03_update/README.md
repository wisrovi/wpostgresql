# Update - Actualizar Registros

Este ejemplo muestra cómo actualizar un registro existente.

## Uso

```bash
python example.py
```

## Explicación

El método `update(record_id, data)` recibe:
- `record_id`: El ID del registro a actualizar
- `data`: Un objeto BaseModel con los nuevos valores

## Nota

El método `update` actualiza el registro donde `id = record_id`.

## Resultado esperado

```
Antes de actualizar: [User(id=1, name='Juan Pérez', age=30, is_active=True)]
Después de actualizar: [User(id=1, name='Juan Pérez', age=31, is_active=False)]
```
