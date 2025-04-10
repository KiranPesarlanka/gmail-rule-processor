import sqlite3

class DB:
    def __init__(self, db_path="emails.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE,
                    from_email TEXT,
                    from_name TEXT,
                    subject TEXT,
                    body TEXT,
                    received_at TEXT
                )
            """)
            conn.commit()

    def save_email(self, message_id, from_email, from_name, subject, body, received_at):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO emails (message_id, from_email, from_name, subject, body, received_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, from_email, from_name, subject, body, received_at))
            conn.commit()

    def fetch_email_ids(self, query):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            email_ids = []
            for row in rows:
                email_ids.append(row[0])
        return email_ids
        

