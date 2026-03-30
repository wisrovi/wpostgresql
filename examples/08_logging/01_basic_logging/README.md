# Logging

Este ejemplo muestra cómo configurar y usar logging.

## Uso

```bash
python example.py
```

## API propuesta

```python
from wpostgresql import configure_logging

# Configuración básica
configure_logging(level="INFO")

# Configuración avanzada
configure_logging(
    level="DEBUG",
    format="json",
    file="logs/wpostgresql.log",
    rotation="10 MB",
    retention="7 days"
)

# Niveles disponibles: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Beneficios

- **Debug**: Rastrear problemas en producción
- **Auditoría**: Registrar quién hizo qué operación
- **Monitoreo**: Observar patrones de uso

## Ejemplo de salida

```
2025-03-30 10:00:00 | INFO | wpostgresql | INSERT INTO user VALUES (...) | 0.023s
2025-03-30 10:00:01 | DEBUG | wpostgresql | SELECT * FROM user | 0.015s
2025-03-30 10:00:02 | WARNING | wpostgresql | Connection pool near limit
```
