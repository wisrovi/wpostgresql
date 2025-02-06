# Examples

This directory contains a collection of examples that demonstrate the usage of various modules and functionalities in this project. Each subfolder corresponds to a specific module and includes example scripts to help you understand how to use that module.

## Directory Structure

The examples are organized as follows:

```
examples/
    wpostgresql/
        crupd.py
        new_columns.py
        with_restrictions.py
```

## How to Use

1. Navigate to the module folder of interest, e.g., `examples/module1/`.
2. Open the `README.md` in that folder to get detailed information about the examples.
3. Run the scripts directly using:
   ```bash
   python example1.py
   ```

## Modules and Examples

### wpostgresql

#### Description
This module demonstrates specific functionalities.


- **crupd.py**: Example demonstrating functionality.
```python
from pydantic import BaseModel
from wpostgresql import WPostgreSQL  # Asegúrate de tener definida la clase WPostgreSQL

# Configuración de conex                                            ión a PostgreSQL
db_config = {
    'dbname': 'wpostgresql',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

# Definir el modelo sin restricciones adicionales
class SimpleModel2(BaseModel):
    id: int
    name: str
    age: int
    is_active: bool

# Crear la base de datos y la tabla (se crean o sincronizan automáticamente)
db = WPostgreSQL(SimpleModel2, db_config)

# Insertar datos
db.insert(SimpleModel2(id=1, name="Juan Pérez", age=30, is_active=True))
db.insert(SimpleModel2(id=2, name="Ana López", age=25, is_active=True))
db.insert(SimpleModel2(id=3, name="Pedro Gómez", age=40, is_active=False))

# Consultar todos los registros
print("Todos los usuarios:", db.get_all())

# Consultar por un campo específico
print("Usuarios llamados Juan Pérez:", db.get_by_field(name="Juan Pérez"))

# Consultar por múltiples filtros
print("Usuarios activos con 25 años:", db.get_by_field(age=25, is_active=True))

# Actualizar un usuario (por ejemplo, actualizando el registro con id=1)
db.update(1, SimpleModel2(id=1, name="Juan Pérez", age=31, is_active=False))
print("Usuario actualizado (id=1):", db.get_by_field(id=1))

# Eliminar un usuario (por ejemplo, el de id=3)
db.delete(3)
print("Usuarios después de eliminar a Pedro Gómez:", db.get_all())
  ```


- **new_columns.py**: Example demonstrating functionality.
```python
from pydantic import BaseModel, Field
from typing import Optional
from wpostgresql import WPostgreSQL

db_config = {
    'dbname': 'wpostgresql',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

# Modelo inicial sin el campo email
class SimpleModel4(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool

# Crear la tabla con el modelo inicial e insertar un registro
db = WPostgreSQL(SimpleModel4, db_config)
db.insert(SimpleModel4(id=1, name="Ana López", age=25, is_active=True))

# === AHORA SE AÑADE UN NUEVO CAMPO AL MODELO ===
class SimpleModel4(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool
    email: Optional[str]  # Nuevo campo sin restricciones en la base de datos

# Al instanciar nuevamente WPostgreSQL con el modelo actualizado se sincroniza la tabla
db = WPostgreSQL(SimpleModel4, db_config)

# Insertar un nuevo registro que incluya el nuevo campo
db.insert(SimpleModel4(id=2, name="Ana López", age=25, is_active=True, email="ana@example.com"))

# Mostrar todos los registros después de la actualización
print("Usuarios después de actualizar el modelo:", db.get_all())
  ```


- **with_restrictions.py**: Example demonstrating functionality.
```python
from pydantic import BaseModel, Field
from typing import Optional
from wpostgresql import WPostgreSQL

db_config = {
    'dbname': 'wpostgresql',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

# Definir el modelo con restricciones
class SimpleModel5(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool
    email: Optional[str] = Field(None, description="UNIQUE")  # Email debe ser único

# Crear la base de datos y sincronizar con el modelo
db = WPostgreSQL(SimpleModel5, db_config)

# Insertar un registro válido
db.insert(SimpleModel5(id=1, name="Juan Pérez", age=30, is_active=True, email="juan@example.com"))

# Intentar insertar un registro con un email duplicado (esto debería fallar)
try:
    db.insert(SimpleModel5(id=2, name="Ana López", age=25, is_active=True, email="juan@example.com"))
except Exception as e:
    print("Error al insertar usuario duplicado:", e)

# Insertar otro registro con un email único (esto funcionará)
db.insert(SimpleModel5(id=3, name="Pedro Gómez", age=40, is_active=False, email="pedro@example.com"))

# Mostrar los registros almacenados
print("Usuarios en la base de datos:", db.get_all())
  ```


