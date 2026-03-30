from pydantic import BaseModel

from wpostgresql import WPostgreSQL

db_config = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


class Person(BaseModel):
    id: int
    name: str
    balance: float


db = WPostgreSQL(Person, db_config)
db.insert(Person(id=1, name="Alice", balance=1000))
db.insert(Person(id=2, name="Bob", balance=500))

try:
    result = db.execute_transaction(
        [
            ("UPDATE person SET balance = balance - 100 WHERE id = 1", None),
            ("UPDATE person SET balance = balance + 100 WHERE id = 2", None),
        ]
    )
    print("Transacción exitosa")
except Exception as e:
    print("Transacción fallida:", e)

print("Saldo final Alice:", db.get_by_field(id=1)[0].balance)
print("Saldo final Bob:", db.get_by_field(id=2)[0].balance)
