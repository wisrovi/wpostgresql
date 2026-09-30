# Example 20: Database Views (`examples/20_database_views`)

Este ejemplo demuestra cómo definir y utilizar **Database Views (Vistas de Base de Datos)** en PostgreSQL utilizando modelos de **Pydantic** y **WPostgreSQL**.

---

## 🚀 Características Clave

1. **Definición Declarativa de Vistas**:
   Al agregar los atributos `__view_name__` y `__view_query__` a un modelo de Pydantic, WPostgreSQL creará o actualizará automáticamente la vista mediante `CREATE OR REPLACE VIEW` durante la inicialización del esquema.

2. **Consultas ORM Tipadas**:
   Puedes consultar vistas como cualquier otra tabla con `.get_all()`, `.filter()`, `.get()`, etc., mapeando los resultados directamente a instancias del modelo de Pydantic.

3. **Protección de Solo Lectura (Read-Only)**:
   WPostgreSQL bloquea las operaciones de escritura (`insert`, `update`, `delete`) sobre los repositorios de vistas lanzando un `OperationError`.

---

## 🛠️ Tecnologías y Librerías Utilizadas

- **[Python 3.10+](https://www.python.org/)** - Lenguaje principal de ejecución.
- **[Pydantic v2](https://docs.pydantic.dev/)** - Modelado de esquemas de datos y validación de tipos.
- **[Psycopg 3](https://www.psycopg.org/psycopg3/docs/)** - Driver PostgreSQL de alto rendimiento con soporte sync/async y connection pooling.
- **[WPostgreSQL](file:///home/william.rodriguez/Documents/w_libraries/w_libraries/wpostgresql_os/wpostgresql/src/wpostgresql)** - Librería ORM ligada a Pydantic y PostgreSQL.

---

## 💻 Código de Ejemplo

```python
from pydantic import BaseModel, Field
from wpostgresql import ForeignType, WPostgreSQL
from wpostgresql.exceptions import OperationError

DB_CONFIG = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}

class Customer(BaseModel):
    name: str
    email: str

class Invoice(BaseModel):
    customer_id: int = Field(
        json_schema_extra={
            "foreign_key": Customer,
            "foreign_type": ForeignType.ONE_MANY,
        }
    )
    total_amount: float

class CustomerInvoiceSummaryView(BaseModel):
    __view_name__ = "customer_invoice_summary"
    __view_query__ = """
        SELECT 
            c.id AS customer_id,
            c.name AS customer_name,
            c.email AS customer_email,
            COUNT(i.id) AS total_invoices,
            COALESCE(SUM(i.total_amount), 0.0) AS total_spent
        FROM customer c
        LEFT JOIN invoice i ON c.id = i.customer_id
        GROUP BY c.id, c.name, c.email
    """

    customer_id: int
    customer_name: str
    customer_email: str
    total_invoices: int
    total_spent: float

db = WPostgreSQL(models=[Customer, Invoice, CustomerInvoiceSummaryView], db_config=DB_CONFIG)

# Consultar vista
summaries = db[CustomerInvoiceSummaryView].get_all()
```

---

## ⚡ Ejecución

```bash
python examples/20_database_views/example.py
```
