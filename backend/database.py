import sqlite3
from typing import List, Optional, Dict, Any

from .config import DATABASE_URL

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DATABASE_URL.replace("sqlite:///./", ""))
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

def create_tables():
    """Crea las tablas necesarias en la base de datos si no existen."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabla de Sleeve Sets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sleeve_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            development INTEGER NOT NULL,
            num_sleeves INTEGER NOT NULL,
            status TEXT NOT NULL, -- 'disponible', 'en uso', 'fuera de servicio'
            UNIQUE(development)
        )
    """)

    # Tabla de Máquinas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_number TEXT NOT NULL UNIQUE,
            max_material_width REAL NOT NULL
        )
    """)

    # Tabla de relación entre Sleeve Sets y Máquinas (muchos a muchos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS machine_sleeve_set_compatibility (
            machine_id INTEGER NOT NULL,
            sleeve_set_id INTEGER NOT NULL,
            PRIMARY KEY (machine_id, sleeve_set_id),
            FOREIGN KEY (machine_id) REFERENCES machines (id) ON DELETE CASCADE,
            FOREIGN KEY (sleeve_set_id) REFERENCES sleeve_sets (id) ON DELETE CASCADE
        )
    """)

    # Tabla para resultados de optimización
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS optimization_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            algorithm_type TEXT NOT NULL, -- 'GA' o 'Greedy'
            timestamp TEXT NOT NULL,
            total_time REAL,
            total_cost REAL,
            schedule_details TEXT -- Almacenar el JSON del schedule optimizado
        )
    """)

    # Tabla para información del último archivo subido
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_file_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_timestamp TEXT NOT NULL,
            file_hash TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()


