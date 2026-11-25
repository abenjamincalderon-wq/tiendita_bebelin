
import sqlite3
import os

RUTA_DB = os.path.join("instance", "preciocerca.db")


def get_db():
    os.makedirs("instance", exist_ok=True)
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    return conexion


def init_db():
    conexion = get_db()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS precios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            negocio TEXT NOT NULL,
            producto TEXT NOT NULL,
            precio INTEGER NOT NULL,
            direccion TEXT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexion.commit()
    conexion.close()


def buscar_precio(negocio, producto):
    conexion = get_db()

    resultado = conexion.execute("""
        SELECT precio
        FROM precios
        WHERE negocio = ? AND producto = ?
        ORDER BY fecha DESC
        LIMIT 1
    """, (negocio, producto)).fetchone()

    conexion.close()

    return resultado["precio"] if resultado else None


def guardar_precio(negocio, producto, precio, direccion):
    conexion = get_db()

    conexion.execute("""
        INSERT INTO precios (negocio, producto, precio, direccion)
        VALUES (?, ?, ?, ?)
    """, (negocio, producto, precio, direccion))

    conexion.commit()
    conexion.close()
