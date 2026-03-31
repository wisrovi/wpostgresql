# Primary Key - Clave Primaria

Este ejemplo muestra cómo usar Primary Key para evitar IDs duplicados.

## Uso

```bash
python example.py
```

## Explicación

Se usa `Field(..., description="Primary Key")` para definir un campo como clave primaria.

## Resultado esperado

```
Error: No se puede insertar ID duplicado: ...
```
