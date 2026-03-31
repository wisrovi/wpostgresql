# Update - Update Records

This example demonstrates how to update an existing record.

## Usage

```bash
python example.py
```

## Explanation

The `update(record_id, data)` method receives:
- `record_id`: The ID of the record to update
- `data`: A BaseModel object with the new values

## Note

The `update` method updates the record where `id = record_id`.

## Expected Output

```
Before update: [User(id=1, name='John Doe', age=30, is_active=True)]
After update: [User(id=1, name='John Doe', age=31, is_active=False)]
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
