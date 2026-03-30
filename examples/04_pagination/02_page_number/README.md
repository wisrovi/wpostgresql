# Paginación por Número de Página

Este ejemplo muestra cómo paginar resultados usando número de página.

## Uso

```bash
python example.py
```

## API propuesta

```python
page_size = 5

# Página 1 (registros 1-5)
db.get_all(page=1, page_size=page_size)

# Página 2 (registros 6-10)
db.get_all(page=2, page_size=page_size)

# Página 3 (registros 11-15)
db.get_all(page=3, page_size=page_size)
```

## Retorna

Una tupla con: (registros, total_páginas, total_registros)

```
Página 1: ([User(...), ...], 4, 20)
```
