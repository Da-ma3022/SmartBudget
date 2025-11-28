import sqlite3
from datetime import datetime

DB_NAME = "gastos.db"

def crear_base_datos():
    """Crea las tablas necesarias si no existen."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            fecha_registro TEXT NOT NULL
        )
    """)

    # Tabla de categorías
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    # Tabla de gastos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            categoria_id INTEGER NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY(categoria_id) REFERENCES categorias(id),
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    # Tabla de ingresos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    # Categorías por defecto
    categorias = ["Comida", "Transporte", "Servicios", "Entretenimiento", "Otros"]
    for cat in categorias:
        try:
            cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (cat,))
        except sqlite3.IntegrityError:
            pass  # ya existe

    conn.commit()
    conn.close()
    print("✔ Base de datos creada correctamente.")
