# database.py
import sqlite3
from pathlib import Path

class ShopHubLite:
    def __init__(self):
        self.db_path = Path("shop_hub.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_orders (
                id INTEGER PRIMARY KEY,
                status TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS diagnostic_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_order_id INTEGER,
                description TEXT,
                vin TEXT,
                dtc_codes TEXT,
                FOREIGN KEY(work_order_id) REFERENCES work_orders(id)
            )
        """)
        self.conn.commit()

    def update_work_order_status(self, wo_id, status):
        self.cursor.execute("INSERT OR REPLACE INTO work_orders (id, status) VALUES (?, ?)", (wo_id, status))
        self.conn.commit()

    def link_diagnostic_report(self, work_order_id, description, vin, dtc_codes):
        self.cursor.execute(
            "INSERT INTO diagnostic_reports (work_order_id, description, vin, dtc_codes) VALUES (?, ?, ?, ?)",
            (work_order_id, description, vin, dtc_codes)
        )
        self.conn.commit()

    def get_reports_for_work_order(self, wo_id):
        self.cursor.execute("SELECT * FROM diagnostic_reports WHERE work_order_id = ?", (wo_id,))
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()
