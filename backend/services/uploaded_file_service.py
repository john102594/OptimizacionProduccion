import sqlite3
from typing import Optional, Dict, Any
from ..database import get_db_connection

class UploadedFileService:
    def create_uploaded_file_info(self, filename: str, upload_timestamp: str, file_hash: str) -> Dict[str, Any]:
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

    def get_uploaded_file_info(self, file_info_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM uploaded_file_info WHERE id = ?", (file_info_id,))
        file_info = cursor.fetchone()
        conn.close()
        return dict(file_info) if file_info else None

    def get_latest_uploaded_file_info(self) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM uploaded_file_info ORDER BY upload_timestamp DESC LIMIT 1")
        file_info = cursor.fetchone()
        conn.close()
        return dict(file_info) if file_info else None

    def delete_uploaded_file_info(self, file_info_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM uploaded_file_info WHERE id = ?", (file_info_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
