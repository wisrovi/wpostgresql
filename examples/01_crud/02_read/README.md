# Read - Query Records

This example demonstrates how to query records from the database.

## Available Methods

### get_all()
Returns all records from the table.

### get_by_field(**filters)
Returns records matching the specified filters.

## Usage

```bash
python example.py
```

## Filter Examples

```python
# Single filter
db.get_by_field(name="John Doe")

# Multiple filters
db.get_by_field(age=25, is_active=True)

# No filters (equivalent to get_all)
db.get_by_field()
```

## Expected Output

```
All users: [User(id=1, name='John Doe', ...), ...]
User by name: [User(id=1, name='John Doe', ...)]
Active users aged 25: [User(id=2, name='Jane Doe', ...)]
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
