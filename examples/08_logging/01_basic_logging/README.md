# Logging

This example demonstrates how to configure and use logging.

## Usage

```bash
python example.py
```

## Proposed API

```python
from wpostgresql import configure_logging

# Basic configuration
configure_logging(level="INFO")

# Advanced configuration
configure_logging(
    level="DEBUG",
    format="json",
    file="logs/wpostgresql.log",
    rotation="10 MB",
    retention="7 days"
)

# Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Benefits

- **Debug**: Track issues in production
- **Audit**: Log who performed which operation
- **Monitoring**: Observe usage patterns

## Example Output

```
2025-03-30 10:00:00 | INFO | wpostgresql | INSERT INTO user VALUES (...) | 0.023s
2025-03-30 10:00:01 | DEBUG | wpostgresql | SELECT * FROM user | 0.015s
2025-03-30 10:00:02 | WARNING | wpostgresql | Connection pool near limit
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
