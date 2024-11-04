import sqlite3

DATABASE = 'challenge.db'

def view_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("Data in 'users' table:")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print(user)

    print("\nData in 'flags' table:")
    cursor.execute("SELECT * FROM flags")
    flags = cursor.fetchall()
    for flag in flags:
        print(flag)
    
    conn.close()

if __name__ == '__main__':
    view_data()
