import sqlite3
from typing import List, Optional, Dict, Any
from ..database import get_db_connection

class SleeveSetService:
    def create_sleeve_set(self, development: int, num_sleeves: int, status: str) -> Dict[str, Any]:
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

    def get_sleeve_set(self, sleeve_set_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sleeve_sets WHERE id = ?", (sleeve_set_id,))
        sleeve_set = cursor.fetchone()
        conn.close()
        return dict(sleeve_set) if sleeve_set else None

    def get_all_sleeve_sets(self) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sleeve_sets")
        sleeve_sets = cursor.fetchall()
        conn.close()
        return [dict(ss) for ss in sleeve_sets]

    def update_sleeve_set(self, sleeve_set_id: int, development: Optional[int] = None, num_sleeves: Optional[int] = None, status: Optional[str] = None) -> Optional[Dict[str, Any]]:
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
        return self.get_sleeve_set(sleeve_set_id)

    def delete_sleeve_set(self, sleeve_set_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sleeve_sets WHERE id = ?", (sleeve_set_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
