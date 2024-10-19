import sqlite3

# Database setup
async def db_start(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            budget REAL,
            currency
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            user_id INTEGER,
            amount REAL,
            date TIMESTAMP,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    conn.commit()
    conn.close()