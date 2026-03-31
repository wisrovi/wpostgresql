import psycopg

DB_CONFIG = {
    "dbname": "wpostgresql",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}


def setup_module(module):
    """Crea la base de datos si no existe."""
    config = DB_CONFIG.copy()
    config["dbname"] = "postgres"
    try:
        conn = psycopg.connect(**config)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'wpostgresql'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE wpostgresql")
        cursor.close()
        conn.close()
    except Exception:
        pass


def cleanup_table(table_name: str):
    """Limpia una tabla antes de cada test."""
    try:
        conn = psycopg.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        cursor.close()
        conn.close()
    except Exception:
        pass
