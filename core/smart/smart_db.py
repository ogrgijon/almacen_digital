"""
smart_db.py - S.M.A.R.T. history database integration

Provides functions to store and retrieve S.M.A.R.T. health and attribute history for drives.
"""
from typing import Dict, Optional, List
from datetime import datetime
import sqlite3

SMART_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS smart_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drive_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    reallocated_sectors INTEGER,
    temperature INTEGER,
    power_on_hours INTEGER,
    raw_json TEXT,
    FOREIGN KEY (drive_id) REFERENCES drives(id)
);
"""

class SmartDB:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute(SMART_TABLE_SCHEMA)
        self.conn.commit()

    def add_smart_entry(self, drive_id: int, status: str, attributes: Dict, raw_json: str = None):
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            "INSERT INTO smart_history (drive_id, date, status, reallocated_sectors, temperature, power_on_hours, raw_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                drive_id,
                now,
                status,
                int(attributes.get('Reallocated_Sector_Ct') or 0),
                int(attributes.get('Temperature_Celsius') or 0),
                int(attributes.get('Power_On_Hours') or 0),
                raw_json,
            )
        )
        self.conn.commit()

    def get_smart_history(self, drive_id: int) -> List[Dict]:
        cur = self.conn.execute(
            "SELECT date, status, reallocated_sectors, temperature, power_on_hours FROM smart_history WHERE drive_id = ? ORDER BY date DESC",
            (drive_id,)
        )
        return [dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()]

    def close(self):
        self.conn.close()
