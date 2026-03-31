# Bulk Insert - Insert Multiple Records

This example demonstrates how to insert multiple records in a single operation.

## Usage

```bash
python example.py
```

## Proposed API

```python
users = [
    User(id=1, name="Alice", age=25),
    User(id=2, name="Bob", age=30),
    User(id=3, name="Charlie", age=35),
]

db.insert_many(users)
```

## Benefits

- **Performance**: Single SQL query for multiple records
- **Speed**: Much faster than calling `insert()` multiple times
- **Atomicity**: All are inserted or none (if error)

## Expected Output

```
Inserted users: [User(id=1, name='Alice', age=25), User(id=2, name='Bob', age=30), ...]
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
