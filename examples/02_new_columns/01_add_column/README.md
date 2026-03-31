# Add Column - Add New Columns

This example demonstrates how to add new columns to the model and automatically synchronize with the database.

## Usage

```bash
python example.py
```

## Explanation

1. Initial model created without `email` field
2. Records are inserted with that model
3. Model is redefined with `email` field added
4. When creating a new `WPostgreSQL` instance, the table is automatically synchronized
5. Records can be inserted with the new field

## Expected Output

```
Users: [User(id=1, name='Jane Doe', age=25, is_active=True, email=''), User(id=2, name='John Smith', age=30, is_active=True, email='john@example.com')]
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
