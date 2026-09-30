# Example 20: Database Views (`examples/20_database_views`)

Este ejemplo demuestra cómo definir y utilizar **Database Views (Vistas de Base de Datos)** en PostgreSQL utilizando el decorador pitónico `@view` de **WPostgreSQL** y modelos de **Pydantic**.

---

## 🚀 Características Clave

1. **Decorador Pitónico `@view`**:
   Decorador declarativo que permite especificar el nombre de la vista en PostgreSQL, sus modelos dependientes (`depends_on`) para la creación topológica del esquema, y la consulta SQL (`query`).

2. **Ordenación Topológica por Dependencias (`depends_on`)**:
   `depends_on=[Customer, Invoice]` garantiza que WPostgreSQL cree primero las tablas base antes de intentar ejecutar `CREATE OR REPLACE VIEW`.

3. **Consultas ORM Tipadas**:
   Puedes consultar vistas como cualquier otra tabla con `.get_all()`, `.filter()`, `.get()`, etc., mapeando los resultados directamente a instancias del modelo de Pydantic.

4. **Protección de Solo Lectura (Read-Only)**:
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
from wpostgresql import ForeignType, WPostgreSQL, view
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

@view(
    name="customer_invoice_summary",
    depends_on=[Customer, Invoice],
    query="""
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
)
class CustomerInvoiceSummary(BaseModel):
    customer_id: int
    customer_name: str
    customer_email: str
    total_invoices: int
    total_spent: float

db = WPostgreSQL(models=[Customer, Invoice, CustomerInvoiceSummary], db_config=DB_CONFIG)

# Consultar vista
summaries = db[CustomerInvoiceSummary].get_all()
```

---

## ⚡ Ejecución

```bash
python examples/20_database_views/example.py
```
