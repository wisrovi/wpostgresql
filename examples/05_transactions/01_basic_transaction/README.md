# Transacciones Básicas

Este ejemplo muestra cómo usar transacciones para operaciones atómicas.

## Uso

```bash
python example.py
```

## API propuesta

```python
try:
    with db.transaction() as t:
        t.execute("UPDATE user SET balance = balance - 100 WHERE id = 1")
        t.execute("UPDATE user SET balance = balance + 100 WHERE id = 2")
except Exception as e:
    print("Transacción fallida:", e)
```

## Beneficios

- **Atomicidad**: Si una operación falla, todas se revierten
- **Consistencia**: Mantiene la integridad de los datos
- **Ejemplo**: Transferencia bancaria (debitar + acreditar)

## Resultado esperado

Si todo bien:
```
Saldo final Alice: 900
Saldo final Bob: 600
```

Si falla (ej. ID no existe):
```
Transacción fallida: ...
Saldo final Alice: 1000
Saldo final Bob: 500
```
