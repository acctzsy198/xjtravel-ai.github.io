import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_file='chat_history.db'):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            ''')
            conn.commit()

    def create_session(self):
        session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sessions (session_id) VALUES (?)", (session_id,))
            conn.commit()
        return session_id

    def add_message(self, session_id, role, content):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.commit()

    def get_session_messages(self, session_id):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, created_at FROM messages WHERE session_id = ? ORDER BY created_at",
                (session_id,)
            )
            return cursor.fetchall()

    def get_all_sessions(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.session_id, s.created_at, 
                       COUNT(m.id) as message_count,
                       MIN(m.content) as first_message
                FROM sessions s
                LEFT JOIN messages m ON s.session_id = m.session_id
                GROUP BY s.session_id
                ORDER BY s.created_at DESC
            """)
            return cursor.fetchall()

    def delete_session(self, session_id):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()

    def export_session(self, session_id, format='json'):
        messages = self.get_session_messages(session_id)
        if format == 'json':
            return json.dumps([{
                'role': msg[0],
                'content': msg[1],
                'timestamp': msg[2]
            } for msg in messages], ensure_ascii=False, indent=2)
        elif format == 'markdown':
            return '\n\n'.join([
                f"### {msg[0].title()} ({msg[2]})\n{msg[1]}"
                for msg in messages
            ])
        else:
            raise ValueError(f"Unsupported format: {format}")
