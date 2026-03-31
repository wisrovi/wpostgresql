# Bulk Update - Update Multiple Records

This example demonstrates how to update multiple records in a single operation.

## Usage

```bash
python example.py
```

## Proposed API

```python
# Update multiple records with same values
updates = [
    {"id": 1, "status": "inactive"},
    {"id": 2, "status": "inactive"},
]
db.update_many(updates)

# Or with condition
db.update_many(updates, where={"status": "active"})
```

## Benefits

- **Performance**: Single SQL query
- **Convenience**: Update many records easily

## Expected Output

```
Updated users: [User(id=1, name='Alice', status='inactive'), User(id=2, name='Bob', status='inactive'), User(id=3, name='Charlie', status='active')]
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
