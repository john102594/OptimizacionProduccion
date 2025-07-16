import sqlite3
from typing import List, Optional, Dict, Any

DATABASE_URL = "sqlite:///./production_optimizer.db"

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

# Funciones CRUD para Sleeve Sets
def create_sleeve_set(development: int, num_sleeves: int, status: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sleeve_sets (development, num_sleeves, status) VALUES (?, ?, ?)",
        (development, num_sleeves, status)
    )
    conn.commit()
    sleeve_set_id = cursor.lastrowid
    conn.close()
    return {"id": sleeve_set_id, "development": development, "num_sleeves": num_sleeves, "status": status}

def get_sleeve_set(sleeve_set_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sleeve_sets WHERE id = ?", (sleeve_set_id,))
    sleeve_set = cursor.fetchone()
    conn.close()
    return dict(sleeve_set) if sleeve_set else None

def get_all_sleeve_sets() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sleeve_sets")
    sleeve_sets = cursor.fetchall()
    conn.close()
    return [dict(ss) for ss in sleeve_sets]

def update_sleeve_set(sleeve_set_id: int, development: Optional[int] = None, num_sleeves: Optional[int] = None, status: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if development is not None:
        updates.append("development = ?")
        params.append(development)
    if num_sleeves is not None:
        updates.append("num_sleeves = ?")
        params.append(num_sleeves)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    
    if not updates:
        conn.close()
        return None

    params.append(sleeve_set_id)
    cursor.execute(f"UPDATE sleeve_sets SET {', '.join(updates)} WHERE id = ?", tuple(params))
    conn.commit()
    conn.close()
    return get_sleeve_set(sleeve_set_id)

def delete_sleeve_set(sleeve_set_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sleeve_sets WHERE id = ?", (sleeve_set_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

# Funciones CRUD para Máquinas
def create_machine(machine_number: str, max_material_width: float) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO machines (machine_number, max_material_width) VALUES (?, ?)",
        (machine_number, max_material_width)
    )
    conn.commit()
    machine_id = cursor.lastrowid
    conn.close()
    return {"id": machine_id, "machine_number": machine_number, "max_material_width": max_material_width}

def get_machine(machine_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM machines WHERE id = ?", (machine_id,))
    machine = cursor.fetchone()
    conn.close()
    return dict(machine) if machine else None

def get_all_machines() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM machines")
    machines = cursor.fetchall()
    conn.close()
    return [dict(m) for m in machines]

def update_machine(machine_id: int, machine_number: Optional[str] = None, max_material_width: Optional[float] = None) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if machine_number is not None:
        updates.append("machine_number = ?")
        params.append(machine_number)
    if max_material_width is not None:
        updates.append("max_material_width = ?")
        params.append(max_material_width)
    
    if not updates:
        conn.close()
        return None

    params.append(machine_id)
    cursor.execute(f"UPDATE machines SET {', '.join(updates)} WHERE id = ?", tuple(params))
    conn.commit()
    conn.close()
    return get_machine(machine_id)

def delete_machine(machine_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM machines WHERE id = ?", (machine_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

# Funciones para la compatibilidad entre Máquinas y Sleeve Sets
def add_machine_sleeve_set_compatibility(machine_id: int, sleeve_set_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO machine_sleeve_set_compatibility (machine_id, sleeve_set_id) VALUES (?, ?)",
            (machine_id, sleeve_set_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # La combinación ya existe o las FK no son válidas
        return False
    finally:
        conn.close()

def remove_machine_sleeve_set_compatibility(machine_id: int, sleeve_set_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM machine_sleeve_set_compatibility WHERE machine_id = ? AND sleeve_set_id = ?",
        (machine_id, sleeve_set_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

def get_compatible_sleeve_sets_for_machine(machine_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ss.* FROM sleeve_sets ss
        JOIN machine_sleeve_set_compatibility mssc ON ss.id = mssc.sleeve_set_id
        WHERE mssc.machine_id = ?
    """, (machine_id,))
    sleeve_sets = cursor.fetchall()
    conn.close()
    return [dict(ss) for ss in sleeve_sets]

def get_compatible_machines_for_sleeve_set(sleeve_set_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.* FROM machines m
        JOIN machine_sleeve_set_compatibility mssc ON m.id = mssc.machine_id
        WHERE mssc.sleeve_set_id = ?
    """, (sleeve_set_id,))
    machines = cursor.fetchall()
    conn.close()
    return [dict(m) for m in machines]

# Funciones CRUD para Optimization Results
def create_optimization_result(algorithm_type: str, timestamp: str, total_time: float, total_cost: float, schedule_details: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO optimization_results (algorithm_type, timestamp, total_time, total_cost, schedule_details) VALUES (?, ?, ?, ?, ?)",
        (algorithm_type, timestamp, total_time, total_cost, schedule_details)
    )
    conn.commit()
    result_id = cursor.lastrowid
    conn.close()
    return {"id": result_id, "algorithm_type": algorithm_type, "timestamp": timestamp, "total_time": total_time, "total_cost": total_cost, "schedule_details": schedule_details}

def get_optimization_result(result_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM optimization_results WHERE id = ?", (result_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def get_all_optimization_results() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM optimization_results ORDER BY timestamp DESC")
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

def delete_optimization_result(result_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM optimization_results WHERE id = ?", (result_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

# Funciones CRUD para Uploaded File Info
def create_uploaded_file_info(filename: str, upload_timestamp: str, file_hash: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO uploaded_file_info (id, filename, upload_timestamp, file_hash) VALUES ((SELECT id FROM uploaded_file_info WHERE file_hash = ?), ?, ?, ?)",
        (file_hash, filename, upload_timestamp, file_hash)
    )
    conn.commit()
    file_info_id = cursor.lastrowid
    conn.close()
    return {"id": file_info_id, "filename": filename, "upload_timestamp": upload_timestamp, "file_hash": file_hash}

def get_uploaded_file_info(file_info_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM uploaded_file_info WHERE id = ?", (file_info_id,))
    file_info = cursor.fetchone()
    conn.close()
    return dict(file_info) if file_info else None

def get_latest_uploaded_file_info() -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM uploaded_file_info ORDER BY upload_timestamp DESC LIMIT 1")
    file_info = cursor.fetchone()
    conn.close()
    return dict(file_info) if file_info else None

def delete_uploaded_file_info(file_info_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM uploaded_file_info WHERE id = ?", (file_info_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

def get_latest_optimization_result_by_algorithm(algorithm_type: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM optimization_results WHERE algorithm_type = ? ORDER BY timestamp DESC LIMIT 1", (algorithm_type,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None
