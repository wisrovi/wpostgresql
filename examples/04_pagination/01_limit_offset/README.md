# Pagination with LIMIT and OFFSET

This example demonstrates how to paginate results using limit and offset.

## Usage

```bash
python example.py
```

## Proposed API

```python
# Get only first 5 records
db.get_all(limit=5)

# Skip first 5 and get 3
db.get_all(offset=5, limit=3)

# Offset without limit (skip first N)
db.get_all(offset=10)
```

## Expected Output

```
First 5 users: [User(id=1, ...), User(id=2, ...), User(id=3, ...), User(id=4, ...), User(id=5, ...)]
Skip first 5, show 3: [User(id=6, ...), User(id=7, ...), User(id=8, ...)]
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
