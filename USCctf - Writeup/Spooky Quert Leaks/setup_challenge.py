import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'challenge.db'
FLAG = "apala{awd123awd_awd_213ad_awdaw}"


def setup():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fungsi untuk membuat tabel
    def create_tables():
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS flags (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            flag TEXT NOT NULL
                        )''')
    
    # Membuat tabel untuk pertama kali
    create_tables()

    try:
        # Mencoba memasukkan data awal
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       ('admin', generate_password_hash('REDACTED')))
        cursor.execute("INSERT INTO flags (flag) VALUES (?)", (FLAG,))
        conn.commit()
        print("Database setup complete.")
    except sqlite3.IntegrityError:
        # Mengosongkan database jika IntegrityError terjadi
        print("Admin user or flag already exists. Resetting database.")
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS flags")
        create_tables()  # Membuat tabel ulang setelah menghapus
        # Memasukkan data ulang
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       ('admin', generate_password_hash('REDACTED')))
        cursor.execute("INSERT INTO flags (flag) VALUES (?)", (FLAG,))
        conn.commit()
        print("Database has been reset and setup complete.")
    
    conn.close()

if __name__ == '__main__':
    setup()
