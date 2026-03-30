# Roadmap wpostgresql

## v0.2.0 - Estabilidad
- [ ] Tests con pytest
- [x] Connection pooling (ejemplos creados: `07_connection_pooling/`)
- [x] Logging con loguru (ejemplos creados: `08_logging/`)
- [ ] Excepciones personalizadas
- [ ] Validación anti-SQL injection

## v0.3.0 - Funcionalidad
- [ ] Paginación en get_all() (ejemplos creados: `04_pagination/`)
- [x] Soporte para transacciones (ejemplos creados: `05_transactions/`)
- [x] Métodos bulk (ejemplos creados: `06_bulk_operations/`)
- [ ] Query builder básico

## v0.4.0 - Enhancements
- [ ] Soporte para índices
- [x] Async support (ejemplos creados: `09_async/`)
- [ ] Documentación API completa
- [ ] CLI tool

## v1.0.0 - Release
- [ ] Código estable y testeado
- [ ] Documentación completa
- [ ] Cobertura de tests > 80%

---

## Ejemplos disponibles

| Carpeta | Funcionalidad | Estado |
|---------|---------------|--------|
| 01_crud | Create, Read, Update, Delete | ✅ Implementado |
| 02_new_columns | Añadir columnas | ✅ Implementado |
| 03_restrictions | PK, UNIQUE, NOT NULL | ✅ Implementado |
| 04_pagination | LIMIT/OFFSET, página | ⏳ Pendiente |
| 05_transactions | Transacciones | ⏳ Pendiente |
| 06_bulk_operations | insert_many, update_many | ⏳ Pendiente |
| 07_connection_pooling | Pool de conexiones | ⏳ Pendiente |
| 08_logging | Logging | ⏳ Pendiente |
| 09_async | Async/await | ⏳ Pendiente |
