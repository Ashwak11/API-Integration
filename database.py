import sqlite3

def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS combined_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT,
                    crypto_id TEXT,
                    breed TEXT,
                    temperature REAL,
                    current_price REAL,
                    image_url TEXT,
                    timestamp TEXT
                 )''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
