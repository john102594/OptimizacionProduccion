import sqlite3
from typing import List, Optional, Dict, Any
from ..database import get_db_connection

class MachineService:
    def create_machine(self, machine_number: str, max_material_width: float) -> Dict[str, Any]:
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

    def get_machine(self, machine_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machines WHERE id = ?", (machine_id,))
        machine = cursor.fetchone()
        conn.close()
        return dict(machine) if machine else None

    def get_all_machines(self) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM machines")
        machines = cursor.fetchall()
        conn.close()
        return [dict(m) for m in machines]

    def update_machine(self, machine_id: int, machine_number: Optional[str] = None, max_material_width: Optional[float] = None) -> Optional[Dict[str, Any]]:
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
        return self.get_machine(machine_id)

    def delete_machine(self, machine_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM machines WHERE id = ?", (machine_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0

    def add_machine_sleeve_set_compatibility(self, machine_id: int, sleeve_set_id: int) -> bool:
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
            return False
        finally:
            conn.close()

    def remove_machine_sleeve_set_compatibility(self, machine_id: int, sleeve_set_id: int) -> bool:
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

    def get_compatible_sleeve_sets_for_machine(self, machine_id: int) -> List[Dict[str, Any]]:
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

    def get_compatible_machines_for_sleeve_set(self, sleeve_set_id: int) -> List[Dict[str, Any]]:
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
