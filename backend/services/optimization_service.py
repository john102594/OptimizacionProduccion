import sqlite3
from typing import List, Optional, Dict, Any
from ..database import get_db_connection

class OptimizationService:
    def create_optimization_result(self, algorithm_type: str, timestamp: str, total_time: float, total_cost: float, schedule_details: str) -> Dict[str, Any]:
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

    def get_optimization_result(self, result_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM optimization_results WHERE id = ?", (result_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_all_optimization_results(self) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM optimization_results ORDER BY timestamp DESC")
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def delete_optimization_result(self, result_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM optimization_results WHERE id = ?", (result_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0

    def get_latest_optimization_result_by_algorithm(self, algorithm_type: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM optimization_results WHERE algorithm_type = ? ORDER BY timestamp DESC LIMIT 1", (algorithm_type,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
