import sqlite3


class Database:
    def __init__(self, path):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
           id INT PRIMARY KEY,
           user_id TEXT UNIQUE);
        """)
        self.conn.commit()

    def select_all(self):
        self.cursor.execute("SELECT * FROM users;")
        return self.cursor.fetchall()

    def select(self, column, value):
        self.cursor.execute(f"SELECT * FROM users WHERE {column}='{value}';")
        return self.cursor.fetchall()

    def insert(self, userid):
        try:
            self.cursor.execute(f"INSERT INTO users(user_id) VALUES('{userid}');")
            self.conn.commit()
        except Exception:
            return False
        return True

    def delete(self, userid):
        try:
            self.cursor.execute(f"DELETE FROM users WHERE user_id='{userid}'")
            self.conn.commit()
        except Exception:
            return False
        return True
