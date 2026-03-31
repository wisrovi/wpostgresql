# Pagination by Page Number

This example demonstrates how to paginate results using page number.

## Usage

```bash
python example.py
```

## Proposed API

```python
page_size = 5

# Page 1 (records 1-5)
db.get_all(page=1, page_size=page_size)

# Page 2 (records 6-10)
db.get_all(page=2, page_size=page_size)

# Page 3 (records 11-15)
db.get_all(page=3, page_size=page_size)
```

## Returns

A tuple with: (records, total_pages, total_records)

```
Page 1: ([User(...), ...], 4, 20)
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
