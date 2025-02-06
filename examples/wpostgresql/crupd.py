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
