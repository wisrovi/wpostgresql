# Basic Transactions

This example demonstrates how to use transactions for atomic operations.

## Usage

```bash
python example.py
```

## Proposed API

```python
try:
    with db.transaction() as t:
        t.execute("UPDATE user SET balance = balance - 100 WHERE id = 1")
        t.execute("UPDATE user SET balance = balance + 100 WHERE id = 2")
except Exception as e:
    print("Transaction failed:", e)
```

## Benefits

- **Atomicity**: If one operation fails, all are rolled back
- **Consistency**: Maintains data integrity
- **Example**: Bank transfer (debit + credit)

## Expected Output

If all good:
```
Final balance Alice: 900
Final balance Bob: 600
```

If fails (e.g., ID doesn't exist):
```
Transaction failed: ...
Final balance Alice: 1000
Final balance Bob: 500
```

## Author

**William Rodríguez** - [wisrovi](mailto:wisrovi.rodriguez@gmail.com)

Technology Evangelist & Software Architect

LinkedIn: [William Rodríguez](https://www.linkedin.com/in/william-rodriguez-villamizar-572302207)
